import pandas as pd
from zoneinfo import ZoneInfo
from typing import List, Tuple
from sklearn.cluster import KMeans
import numpy as np

def price_daily_stats(df: pd.DataFrame, timezone: ZoneInfo) -> pd.DataFrame:
    df_copy = df.copy()
    df_copy['interval_start_local'] = df_copy['interval_start_utc'].dt.tz_convert(timezone)
    df_copy['date'] = df_copy['interval_start_local'].dt.date
    df_copy['day_of_week'] = df_copy['interval_start_local'].dt.dayofweek  # Monday=0, Sunday=6
    daily_stats = df_copy.groupby('date')['price'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index()
    day_of_week_map = df_copy[['date', 'day_of_week']].drop_duplicates()
    daily_stats = daily_stats.merge(day_of_week_map, on='date')
    return daily_stats

def price_weekly_stats(df: pd.DataFrame, timezone: ZoneInfo) -> pd.DataFrame:
    df_copy = df.copy()
    df_copy['interval_start_local'] = pd.to_datetime(df_copy['interval_start_utc']).dt.tz_convert(timezone)
    df_copy['month'] = df_copy['interval_start_local'].dt.month
    df_copy['year'] = df_copy['interval_start_local'].dt.isocalendar().year
    # Calculate week number in the month based on local date
    df_copy['week_of_month'] = df_copy['interval_start_local'].apply(lambda d: (d.day - 1) // 7 + 1)
    weekly_stats = df_copy.groupby(['year', 'month', 'week_of_month'])['price'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index()
    return weekly_stats

def price_daily_stats_extended(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    # Add local time column (assume interval_start_utc is already UTC-aware)
    df_copy = df.copy()
    df_copy['interval_start_local'] = df_copy['interval_start_utc'].dt.tz_convert(timezone)
    df_copy['date'] = df_copy['interval_start_local'].dt.date

    stats_list = []

    for date, group in df_copy.groupby('date'):
        group = group.copy()
        group['hour'] = group['interval_start_local'].dt.hour

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

    extended_stats_df = pd.DataFrame(stats_list)

    # Merge with basic daily stats (using local date)
    basic_stats = price_daily_stats(df_copy, timezone=timezone)
    result = basic_stats.merge(extended_stats_df, on='date')
    return result

def get_price_peak_offpeak_hours(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> Tuple[List[int], List[int], List[int]]:
    # here I want to do some classification to determine (a) peak hours in a set of prices
    # (b) off-peak hours in a set of prices (c) mid-peak hours in a set of prices
    # the sum of these hours should be 24 hours
    # we need to use a classification algorithm to determine these hours
    df_copy = df.copy()
    df_copy['interval_start_local'] = df_copy['interval_start_utc'].dt.tz_convert(timezone)
    df_copy['hour'] = df_copy['interval_start_local'].dt.hour
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

    return peak_hours, offpeak_hours, midpeak_hours

def get_price_peak_offpeak_hours_alt(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> Tuple[List[int], List[int], List[int]]:
    
    
    df_copy = add_peak_offpeak_labels(df, timezone)
    
    dominant_label_dict = get_dominant_hourly_category(df_copy)

    return (
        dominant_label_dict['peak'],
        dominant_label_dict['off_peak'],
        dominant_label_dict['mid_peak']
    )
    
def add_peak_offpeak_labels(df: pd.DataFrame, timezone: ZoneInfo) -> pd.DataFrame:

    df_copy = df.copy()
    df_copy['interval_start_local'] = df_copy['interval_start_utc'].dt.tz_convert(timezone)
    df_copy['date'] = df_copy['interval_start_local'].dt.date
    df_copy['hour'] = df_copy['interval_start_local'].dt.hour
    # Aggregate prices by hour

    result = {}

    for date, group in df_copy.groupby('date'):
        hourly = group.groupby('hour')['price'].mean().reset_index()

        # Ensure exactly 24 hourly values for clustering
        if len(hourly) != 24:
            continue  # skip incomplete days

        kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
        hourly['cluster'] = kmeans.fit_predict(hourly[['price']].values.reshape(-1, 1))

        # Rank clusters by average price
        cluster_order = hourly.groupby('cluster')['price'].mean().sort_values()
        cluster_to_label = {
            cluster_order.index[0]: 'off_peak',
            cluster_order.index[1]: 'mid_peak',
            cluster_order.index[2]: 'peak'
        }

        hourly['label'] = hourly['cluster'].map(cluster_to_label)

        # Map back to main df
        hourly_label_map = hourly.set_index('hour')['label'].to_dict()

        date_mask = df_copy['date'] == date
        df_copy.loc[date_mask, 'price_category'] = df_copy.loc[date_mask, 'hour'].map(hourly_label_map)

    return df_copy

def get_dominant_hourly_category(df: pd.DataFrame) -> dict:
    # Count how many times each (hour, category) occurs
    counts = df.groupby(['hour', 'price_category']).size().reset_index(name='count')

    # For each hour, find the category with the max count
    dominant_labels = counts.sort_values('count', ascending=False).drop_duplicates(subset='hour')

    result = {'peak': [], 'mid_peak': [], 'off_peak': []}
    for _, row in dominant_labels.iterrows():
        result[row['price_category']].append(row['hour'])

    # Sort each list of hours
    for key in result:
        result[key] = sorted(result[key])

    return result

        # result[str(date)] = {
        #     'peak': sorted(hourly[hourly['label'] == 'peak']['hour'].tolist()),
        #     'mid_peak': sorted(hourly[hourly['label'] == 'mid_peak']['hour'].tolist()),
        #     'off_peak': sorted(hourly[hourly['label'] == 'off_peak']['hour'].tolist())
        # }

def price_daily_stats_peak_off_peak(
    df: pd.DataFrame,
    peak_hours: List[int],
    offpeak_hours: List[int],
    midpeak_hours: List[int],
    timezone: ZoneInfo,
) -> pd.DataFrame:
    # group the price data into 3 group per day peak, off-peak, and mid-peak
    # and then calculate the stats for each group
    
    df_copy = df.copy()

    df_copy["interval_start_local"] = df_copy["interval_start_utc"].dt.tz_convert(timezone)
    df_copy["date"] = df_copy['interval_start_local'].dt.date
    df_copy["hour"] = df_copy['interval_start_local'].dt.hour

    
    # next we group the df_copy  rows based on date and hours that belong to peak hours
    # Assign a period label based on the hour
    def assign_period(hour):
        if hour in peak_hours:
            return 'peak'
        elif hour in offpeak_hours:
            return 'offpeak'
        elif hour in midpeak_hours:
            return 'midpeak'
        else:
            return 'unknown'

    df_copy['period'] = df_copy['hour'].apply(assign_period)

    # Group by date and period, then calculate statistics
    grouped = df_copy.groupby(['date', 'period'])['price'].agg(['mean', 'min', 'max', 'std']).reset_index()

    return grouped

def price_daily_stats_infer_peak(
    df: pd.DataFrame,    
    timezone: ZoneInfo,
) -> pd.DataFrame:
    # group the price data into 3 group per day peak, off-peak, and mid-peak
    # and then calculate the stats for each group
    
    df_copy = df.copy()

    df_copy = add_peak_offpeak_labels(df_copy, timezone)    

    # Group by date and period, then calculate statistics
    grouped = df_copy.groupby(['date', 'price_category'])['price'].agg(['mean', 'min', 'max', 'std']).reset_index()

    grouped_pivot = grouped.pivot(index='date', columns='price_category', values=['mean', 'min', 'max', 'std'])
    grouped_pivot.columns = ['_'.join(col).strip() for col in grouped_pivot.columns.values]
    grouped_pivot.reset_index(inplace=True)
    return grouped_pivot

def price_stat_weekly_extended(
    df: pd.DataFrame,    
    timezone: ZoneInfo,
) -> pd.DataFrame:        

    df_copy = add_peak_offpeak_labels(df, timezone)

    df_copy['month'] = df_copy['interval_start_local'].dt.month
    df_copy['year'] = df_copy['interval_start_local'].dt.isocalendar().year
    df_copy["week"] = df_copy['interval_start_local'].dt.isocalendar().week
    # Calculate week number in the month based on local date
    df_copy['week_of_month'] = df_copy['interval_start_local'].apply(lambda d: (d.day - 1) // 7 + 1)


    weekly_stats = df_copy.groupby(['year', 'month', 'week_of_month','price_category'])['price'].agg(['mean', 'min', 'max', 'std']).reset_index()

    weekly_stats_pivot = weekly_stats.pivot(index=['year', 'month', 'week_of_month'], columns='price_category', values=['mean', 'min', 'max', 'std'])

    weekly_stats_pivot.columns = ['_'.join(col).strip() for col in weekly_stats_pivot.columns.values]
    weekly_stats_pivot.reset_index(inplace=True)
    return weekly_stats_pivot

def price_stat_weekly_weekday_separated(
    df: pd.DataFrame,    
    timezone: ZoneInfo,
) -> pd.DataFrame:


    df_copy = add_peak_offpeak_labels(df, timezone)

    df_copy['month'] = df_copy['interval_start_local'].dt.month
    df_copy['year'] = df_copy['interval_start_local'].dt.isocalendar().year
    df_copy["week"] = df_copy['interval_start_local'].dt.isocalendar().week
    # Calculate week number in the month based on local date
    df_copy['week_of_month'] = df_copy['interval_start_local'].apply(lambda d: (d.day - 1) // 7 + 1)

    df_copy['day_of_week'] = df_copy['interval_start_local'].dt.dayofweek

    df_copy['day_type'] = df_copy['day_of_week'].apply(lambda x: 'weekend' if x >= 5 else 'weekday')

    weekly_stats = df_copy.groupby(['year', 'month', 'week_of_month', 'day_type','price_category'])['price'].agg(['mean', 'min', 'max', 'std']).reset_index()

    weekly_stats_pivot = weekly_stats.pivot(index=['year', 'month', 'week_of_month'], columns=['day_type', 'price_category'], values=['mean', 'min', 'max', 'std'])

    weekly_stats_pivot.columns = ['_'.join(col).strip() for col in weekly_stats_pivot.columns.values]
    weekly_stats_pivot.reset_index(inplace=True)
    return weekly_stats_pivot

def price_hourly_means(
    df: pd.DataFrame,
    timezone: ZoneInfo,    
) -> List[float]:
    
    df_copy = df.copy()

    df_copy['interval_start_local'] = df['interval_start_utc'].dt.tz_convert(timezone)
    df_copy["hour"] = df_copy['interval_start_local'].dt.hour

    df = df_copy.groupby("hour")["price"].mean()

    values = df.values
    return list(values)

def price_period_means(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> List[float]:
    
    df_copy = add_peak_offpeak_labels(df, timezone)

    df = df_copy.groupby("price_category")["price"].mean()
    return list(df.values)

def price_hourly_variations(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    
    df_copy = add_peak_offpeak_labels(df, timezone)

    # period_means =  df_copy.groupby("price_category")["price"].mean().values

    period_avg = df_copy.groupby('price_category')['price'].mean().rename('avg_price')

    df = df_copy.merge(period_avg, on='price_category')
    df['delta_from_avg'] = df['price'] - df['avg_price']


    std_delta = (
        df.groupby('hour')['delta_from_avg'].apply(lambda x: np.sqrt(np.mean(x ** 2)))  # std around fixed mean (avg_price)
    .rename('hourly_delta_std')
    )

    return std_delta


def dam_rtm_hourly_dif(
    dam_df: pd.DataFrame,
    rtm_df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    
    dam_df_copy = dam_df.copy()
    dam_df_copy['interval_start_local'] = dam_df_copy['interval_start_utc'].dt.tz_convert(timezone)
    dam_df_copy['date'] = dam_df_copy['interval_start_local'].dt.date
    dam_df_copy['hour'] = dam_df_copy['interval_start_local'].dt.hour
    dam_df_copy["dart"] = dam_df_copy["price"] - rtm_df["price"]
    dam_df_copy

    return dam_df_copy

def dam_rtm_hourly_dif_stat(
    dam_df: pd.DataFrame,
    rtm_df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    
    dam_df_copy = add_peak_offpeak_labels(dam_df, timezone)

    dam_df_copy["dart"] =  dam_df_copy["price"] - rtm_df["price"]


    df = dam_df_copy.groupby(['date','price_category'])['dart'].agg(['mean', 'min', 'max', 'std']).reset_index()

    return df


def dam_rtm_hourly_dif_short_term(
    dam_df: pd.DataFrame,
    rtm_df: pd.DataFrame,
    timezone: ZoneInfo,
    peak_hours: List[int],
    offpeak_hours: List[int],
    midpeak_hours: List[int],
) -> pd.DataFrame:
    
    rtm_df_copy = add_period_labels(rtm_df, peak_hours, offpeak_hours, midpeak_hours, timezone)

    dam_df_copy = dam_df.copy()
    dam_df_copy['interval_start_local'] = dam_df_copy['interval_start_utc'].dt.tz_convert(timezone)
    dam_df_copy['date'] = dam_df_copy['interval_start_local'].dt.date
    dam_df_copy['hour'] = dam_df_copy['interval_start_local'].dt.hour
    dam_df_copy.set_index("interval_start_local", inplace=True)
    dam_df_copy.resample('15T').ffill()
    dam_df_copy.reset_index(inplace=True)

    rtm_df_copy["dart"] =  dam_df_copy["price"] - rtm_df_copy["price"]

    df = rtm_df_copy.groupby(['date','hour','price_category'])['dart'].agg(['mean', 'min', 'max', 'std']).reset_index()

    return df


def add_period_labels(
    df: pd.DataFrame,
    peak_hours: List[int],
    offpeak_hours: List[int],
    midpeak_hours: List[int],
    timezone: ZoneInfo,
) -> pd.DataFrame:
    
    df_copy = df.copy()
    df_copy['interval_start_local'] = df_copy['interval_start_utc'].dt.tz_convert(timezone)
    df_copy['date'] = df_copy['interval_start_local'].dt.date
    df_copy['hour'] = df_copy['interval_start_local'].dt.hour

    # Assign a period label based on the hour
    def assign_period(hour):
        if hour in peak_hours:
            return 'peak'
        elif hour in offpeak_hours:
            return 'offpeak'
        elif hour in midpeak_hours:
            return 'midpeak'
        else:
            return 'unknown'

    df_copy['price_category'] = df_copy['hour'].apply(assign_period)

    return df_copy