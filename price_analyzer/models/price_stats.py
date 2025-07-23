import pandas as pd
from zoneinfo import ZoneInfo
from typing import List, Tuple
from sklearn.cluster import KMeans
import numpy as np
from price_analyzer.models.features import(
    local_time_date_hour,
    weekly_monthly_info,
    peak_offpeak_labels,
    attach_peak_offpeak_labels,
    dam_rtm_hourly_dif,
    price_hourly_variations as price_hourly_variations_feature,
)

def price_daily_stats(df: pd.DataFrame, timezone: ZoneInfo) -> pd.DataFrame:
    
    hour_info = local_time_date_hour(df, timezone)
    df_copy = df[["price"]].copy()
    df_copy = pd.concat([df_copy, hour_info], axis=1)

    daily_stats = df_copy.groupby('date')['price'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index()
    day_of_week_map = df_copy[['date', 'day_of_week']].drop_duplicates()
    daily_stats = daily_stats.merge(day_of_week_map, on='date')
    return daily_stats

def price_weekly_stats(df: pd.DataFrame, timezone: ZoneInfo) -> pd.DataFrame:
    week_info = weekly_monthly_info(df, timezone)

    df_copy = df[["price"]].copy()
    df_copy = pd.concat([df_copy, week_info], axis=1)
    
    weekly_stats = df_copy.groupby(['year', 'month', 'week_of_month'])['price'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index()
    return weekly_stats

def price_daily_stats_extended(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    # Add local time column (assume interval_start_utc is already UTC-aware)

    hour_info = local_time_date_hour(df, timezone)
    df_copy = df[["price"]].copy()
    df_copy = pd.concat([df_copy, hour_info], axis=1)
    stats_list = []

    for date, group in df_copy.groupby('date'):
        group = group.copy()
        group['hour'] = group['interval_end_local'].dt.hour

        peak_indices_t3 = group['price'].nlargest(3).index.tolist()
        peak_prices_t3 = group.loc[peak_indices_t3, 'price'].values
        peak_hours_t3 = group.loc[peak_indices_t3, 'hour'].tolist()

        peak_indices_t2 = group['price'].nlargest(2).index.tolist()
        peak_prices_t2 = group.loc[peak_indices_t2, 'price'].values
        peak_hours_t2 = group.loc[peak_indices_t2, 'hour'].tolist()

        offpeak_indices_b3 = group['price'].nsmallest(3).index.tolist()
        offpeak_prices_b3 = group.loc[offpeak_indices_b3, 'price'].values
        offpeak_hours_b3 = group.loc[offpeak_indices_b3, 'hour'].tolist()

        offpeak_indices_b2 = group['price'].nsmallest(2).index.tolist()
        offpeak_prices_b2 = group.loc[offpeak_indices_b2, 'price'].values
        offpeak_hours_b2 = group.loc[offpeak_indices_b2, 'hour'].tolist()

        stats = {
            'date': date,
            'day_of_week': group["day_of_week"].drop_duplicates().values[0],
            'mean_peak_top3': peak_prices_t3.mean() if len(peak_prices_t3) > 0 else None,
            'mean_peak_top2': peak_prices_t2.mean() if len(peak_prices_t2) > 0 else None,
            'peak_top3_hours': peak_hours_t3,
            'peak_top2_hours': peak_hours_t2,
            'mean_offpeak_bottom3': offpeak_prices_b3.mean() if len(offpeak_prices_b3) > 0 else None,
            'mean_offpeak_bottom2': offpeak_prices_b2.mean() if len(offpeak_prices_b2) > 0 else None,
            'offpeak_bottom3_hours': offpeak_hours_b3,
            'offpeak_bottom2_hours': offpeak_hours_b2,
            'std_peak_top3': peak_prices_t3.std() if len(peak_prices_t3) > 0 else None,
            'std_peak_top2': peak_prices_t2.std() if len(peak_prices_t2) > 0 else None,
            'std_offpeak_bottom3': offpeak_prices_b3.std() if len(offpeak_prices_b3) > 0 else None,
            'std_offpeak_bottom2': offpeak_prices_b2.std() if len(offpeak_prices_b2) > 0 else None,            
        }
        stats_list.append(stats)

    return pd.DataFrame(stats_list)
   
def price_peak_offpeak_hours_aprox(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> Tuple[List[int], List[int], List[int]]:
    # here I want to do some classification to determine (a) peak hours in a set of prices
    # (b) off-peak hours in a set of prices (c) mid-peak hours in a set of prices
    # the sum of these hours should be 24 hours
    # we need to use a classification algorithm to determine these hours
    
    hour_info = local_time_date_hour(df, timezone)

    df_copy = df[["price"]].copy()
    df_copy = pd.concat([df_copy,hour_info], axis=1)

    # Aggregate prices by hour
    hourly_prices = df_copy.groupby('hour')['price'].mean().reset_index()

    # Reshape for clustering
    X = hourly_prices['price'].values.reshape(-1, 1)

    # KMeans clustering into 3 groups: peak, off-peak, mid-peak
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(X)

    # Map cluster centers to peak/off-peak/mid-peak by sorting centers
    centers = kmeans.cluster_centers_.flatten()
    sorted_indices = np.argsort(centers)
    peak_label = sorted_indices[2]
    midpeak_label = sorted_indices[1]
    offpeak_label = sorted_indices[0]

    peak_hours = hourly_prices['hour'][labels == peak_label].tolist()
    midpeak_hours = hourly_prices['hour'][labels == midpeak_label].tolist()
    offpeak_hours = hourly_prices['hour'][labels == offpeak_label].tolist()

    return peak_hours, midpeak_hours, offpeak_hours 

def price_peak_offpeak_hours(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> Tuple[List[int], List[int], List[int]]:
    
    hour_info = local_time_date_hour(df,timezone)
    peak_labels = peak_offpeak_labels(df, timezone)
    
    df_copy = df[['price']].copy()
    df_copy = pd.concat([df_copy, hour_info, peak_labels], axis=1)
    dominant_label_dict = _dominant_hourly_category(df_copy)

    return (
        dominant_label_dict['peak'],        
        dominant_label_dict['mid_peak'],
        dominant_label_dict['off_peak'],
    )
 
def _dominant_hourly_category(df: pd.DataFrame) -> dict:
    # Count how many times each (hour, category) occurs
    counts = df.groupby(['hour', 'price_period']).size().reset_index(name='count')

    # For each hour, find the category with the max count
    dominant_labels = counts.sort_values('count', ascending=False).drop_duplicates(subset='hour')

    result = {'peak': [], 'mid_peak': [], 'off_peak': []}
    for _, row in dominant_labels.iterrows():
        result[row['price_period']].append(row['hour'])

    # Sort each list of hours
    for key in result:
        result[key] = sorted(result[key])

    return result
        
def price_daily_stats_peak_off_peak(
    df: pd.DataFrame,
    peak_hours: List[int],
    offpeak_hours: List[int],
    midpeak_hours: List[int],
    timezone: ZoneInfo,
) -> pd.DataFrame:
    # group the price data into 3 group per day peak, off-peak, and mid-peak
    # and then calculate the stats for each group
    
    hour_info  = local_time_date_hour(df, timezone)
    price_period = attach_peak_offpeak_labels(peak_hours, offpeak_hours, midpeak_hours)
    df_copy = df[['price']].copy()
    df_copy = pd.concat([df_copy, hour_info, price_period], axis=1)
    
    # Group by date and period, then calculate statistics
    grouped = df_copy.groupby(['date', 'price_period'])['price'].agg(['mean', 'min', 'max', 'std']).reset_index()
    return grouped

def price_daily_stats_infer_peak(
    df: pd.DataFrame,    
    timezone: ZoneInfo,
) -> pd.DataFrame:
    # group the price data into 3 group per day peak, off-peak, and mid-peak
    # and then calculate the stats for each group
    hour_info = local_time_date_hour(df, timezone)
    price_period = peak_offpeak_labels(df, timezone)
    df_copy = df[['price']].copy()
    df_copy = pd.concat([df_copy, hour_info, price_period], axis=1)

    # Group by date and period, then calculate statistics
    grouped = df_copy.groupby(['date', 'price_period'])['price'].agg(['mean', 'min', 'max', 'std']).reset_index()

    grouped_pivot = grouped.pivot(index='date', columns='price_period', values=['mean', 'min', 'max', 'std'])
    grouped_pivot.columns = ['_'.join(col).strip() for col in grouped_pivot.columns.values]
    grouped_pivot.reset_index(inplace=True)
    return grouped_pivot

def price_stat_weekly_extended(
    df: pd.DataFrame,    
    timezone: ZoneInfo,
) -> pd.DataFrame:        

    week_info = weekly_monthly_info(df, timezone)
    price_period = peak_offpeak_labels(df, timezone)
    df_copy = df[['price']].copy()
    df_copy = pd.concat([df_copy, week_info, price_period], axis=1)

    weekly_stats = df_copy.groupby(
        ['year', 'month', 'week_of_month','price_period']
    )['price'].agg(['mean', 'min', 'max', 'std']).reset_index()

    weekly_stats_pivot = weekly_stats.pivot(
        index=['year', 'month', 'week_of_month'],
        columns='price_period', 
        values=['mean', 'min', 'max', 'std'],
    )

    weekly_stats_pivot.columns = ['_'.join(col).strip() for col in weekly_stats_pivot.columns.values]
    weekly_stats_pivot.reset_index(inplace=True)
    return weekly_stats_pivot

def price_stat_weekly_weekday_separated(
    df: pd.DataFrame,    
    timezone: ZoneInfo,
) -> pd.DataFrame:

    week_info = weekly_monthly_info(df, timezone)
    price_period = peak_offpeak_labels(df, timezone)
    df_copy = df[['price']].copy()
    df_copy = pd.concat([df_copy, week_info, price_period], axis=1)
    df_copy['day_type'] = df_copy['is_weekend'].apply(lambda x: 'weekend' if x else 'weekday')

    weekly_stats = df_copy.groupby(
        ['year', 'month', 'week_of_month', 'day_type','price_period']
    )['price'].agg(['mean', 'min', 'max', 'std']).reset_index()

    weekly_stats_pivot = weekly_stats.pivot(
        index=['year', 'month', 'week_of_month'],
        columns=['day_type', 'price_period'],
        values=['mean', 'min', 'max', 'std'],
    )

    weekly_stats_pivot.columns = ['_'.join(col).strip() for col in weekly_stats_pivot.columns.values]
    weekly_stats_pivot.reset_index(inplace=True)
    return weekly_stats_pivot

def price_hourly_means(
    df: pd.DataFrame,
    timezone: ZoneInfo,    
) -> List[float]:
    hour_info = local_time_date_hour(df, timezone)
    df_copy = df[['price']].copy()
    df_copy = pd.concat([df_copy, hour_info], axis=1)
    values = df_copy.groupby("hour")["price"].mean().values
    return list(values)

def price_period_means(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> List[float]:
    
    hour_info = local_time_date_hour(df, timezone)
    price_period = peak_offpeak_labels(df, timezone)
    df_copy = df[['price']].copy()
    df_copy = pd.concat([df_copy, hour_info, price_period], axis=1)

    df = df_copy.groupby("price_period")["price"].mean()
    return list(df.values)

def price_hourly_variations(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    df_copy = price_hourly_variations_feature(df, timezone)
    std_delta = (
        df_copy.groupby('hour')['delta_from_avg'].apply(lambda x: np.sqrt(np.mean(x ** 2)))  # std around fixed mean (avg_price)
    .rename('hourly_delta_std')
    )
    return std_delta

def dam_rtm_hourly_dif_stat(
    dam_df: pd.DataFrame,
    rtm_df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    
    dart = dam_rtm_hourly_dif(dam_df, rtm_df, timezone)
    dart_hour_info = local_time_date_hour(dart, timezone)
    dart_peak_info = peak_offpeak_labels(dart, timezone)
    dart = pd.concat([dart, dart_peak_info, dart_hour_info], axis=1)

    df = dart.groupby(['date','price_period'])['dart'].agg(['mean', 'min', 'max', 'std']).reset_index()
    return df


def dam_rtm_hourly_dif_short_term(
    dam_df: pd.DataFrame,
    rtm_df: pd.DataFrame,
    timezone: ZoneInfo,
    peak_hours: List[int],
    offpeak_hours: List[int],
    midpeak_hours: List[int],
) -> pd.DataFrame:
    
    dart = dam_rtm_hourly_dif(dam_df, rtm_df, timezone)
    dart_peak_info = attach_peak_offpeak_labels(dart, peak_hours, offpeak_hours, midpeak_hours, timezone)
    dart_hour_info = local_time_date_hour(dart, timezone)
    dart = pd.concat([dart, dart_peak_info, dart_hour_info], axis=1)

    # rtm_peak_info = attach_peak_offpeak_labels(rtm_df, peak_hours, offpeak_hours, midpeak_hours, timezone)
    # rtm_hour_info = local_time_date_hour(rtm_df, timezone)
    # rtm_df_copy = rtm_df[['price']].copy()
    # rtm_df_copy = pd.concat([rtm_df_copy, rtm_hour_info, rtm_peak_info], axis=1)
    # dam_hour_info = local_time_date_hour(dam_df, timezone)
    # dam_df_copy = dam_df[['price']].copy()
    # dam_df_copy = pd.concat([dam_df_copy, dam_hour_info], axis=1)
    # dam_df_copy.set_index("interval_end_local", inplace=True)
    # dam_df_copy.resample('15T').ffill()
    # dam_df_copy.reset_index(inplace=True)                
    # rtm_df_copy["dart"] =  dam_df_copy["price"] - rtm_df_copy["price"]

    df = dart.groupby(['date','hour','price_period'])['dart'].agg(['mean', 'min', 'max', 'std']).reset_index()
    return df

