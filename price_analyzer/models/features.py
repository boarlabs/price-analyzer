import pandas as pd
from zoneinfo import ZoneInfo
from sklearn.cluster import KMeans
from typing import List

def local_time_date_hour(df: pd.DataFrame, timezone: ZoneInfo) -> pd.DataFrame:
    df_new = df[["interval_end_utc"]].copy()
    df_new["interval_end_local"] = df_new["interval_end_utc"].dt.tz_convert(timezone)
    df_new["hour"] = df_new["interval_end_local"].dt.hour
    df_new["date"] = df_new["interval_end_local"].dt.date
    df_new["day_of_week"] = df_new["interval_end_local"].dt.day_of_week

    return df_new

def weekly_monthly_info(df: pd.DataFrame, timezone: ZoneInfo) -> pd.DataFrame:
    hour_info = local_time_date_hour(df, timezone)

    df_new = df[["interval_end_utc"]].copy()
    df_new["day_of_week"] = hour_info["interval_end_local"].dt.day_of_week
    df_new["month"] = hour_info["interval_end_local"].dt.month
    df_new["year"] = hour_info["interval_end_local"].dt.isocalendar().year
    df_new["week_of_month"] = hour_info["interval_end_local"].apply(lambda d: (d.day - 1) // 7 + 1)
    df_new["is_weekend"] = df_new["day_of_week"].apply(lambda x: True if x >= 5 else False)

    return df_new

def peak_offpeak_labels(df: pd.DataFrame, timezone: ZoneInfo) -> pd.DataFrame:

    df_copy = df[['price']].copy()
    hour_info = local_time_date_hour(df, timezone)

    df_copy  = pd.concat([df_copy, hour_info], axis=1)

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
        df_copy.loc[date_mask, 'price_period'] = df_copy.loc[date_mask, 'hour'].map(hourly_label_map)

    return df_copy[["price_period"]]

def attach_peak_offpeak_labels(
    df: pd.DataFrame,
    peak_hours: List[int],
    offpeak_hours: List[int],
    midpeak_hours: List[int],
    timezone: ZoneInfo,
) -> pd.DataFrame:
    
    df_copy = local_time_date_hour(df, timezone)

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

    df_copy['price_period'] = df_copy['hour'].apply(assign_period)

    return df_copy[['price_period']]

def dam_rtm_hourly_dif(
    dam_df: pd.DataFrame,
    rtm_df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    
    hour_info = local_time_date_hour(dam_df, timezone)
    df_copy = dam_df[['price']].copy()
    dam_df_copy = pd.concat([df_copy, hour_info], axis=1)

    dam_df_copy.set_index("interval_end_local", inplace=True)
    dam_df_copy.resample('15T').ffill()
    dam_df_copy.reset_index(inplace=True)

    dam_df_copy["dart"] = dam_df_copy["price"] - rtm_df["price"]

    return dam_df_copy[['interval_end_utc', 'dart']]


def price_hourly_variations(
    df: pd.DataFrame,
    timezone: ZoneInfo,
) -> pd.DataFrame:
    
    hour_info = local_time_date_hour(df, timezone)
    price_period = peak_offpeak_labels(df, timezone)
    df_copy = df[['price']].copy()
    df_copy = pd.concat([df_copy, hour_info, price_period], axis=1)

    period_avg = df_copy.groupby('price_period')['price'].mean().rename('period_avg_price')

    df = df_copy.merge(period_avg, on='price_period')
    df['delta_from_avg'] = df['price'] - df['period_avg_price']

    return df[['interval_end_utc', 'price_period', 'period_avg_price','delta_from_avg']]