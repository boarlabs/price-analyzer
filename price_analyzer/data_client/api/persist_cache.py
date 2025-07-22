from pathlib import Path
import pandas as pd
from typing import  List, Tuple 
from datetime import datetime

from price_analyzer.dtos.basic_types import ISOType, MarketType, PriceType

CACHE_VOLUME_PATH = Path(__file__).parent / "data_store_volume"

COLUMN_NAMES = [
    "interval_start_utc",
    "interval_end_utc",
    "location",
    "location_type",
    "market",
    "price",
]

def get_cache_file_path(
    iso: ISOType,
    market_type: MarketType,
    price_type: PriceType,
    node: str,
) -> Path:
    """
    Constructs the cache file path based on the parameters provided.
    """
    file_name = f"{iso.name}_{market_type.name}_{price_type.name}_{node}.csv"

    return CACHE_VOLUME_PATH / file_name



def get_cache_file(iso: ISOType, market_type: MarketType, price_type: PriceType, node: str) -> pd.DataFrame:
    """
    Retrieves the cache file path for the given parameters.
    If the file does not exist, creates an empty DataFrame.
    """
    cache_file_path = get_cache_file_path(iso, market_type, price_type, node)
    

    if not cache_file_path.exists():
        # Create an empty DataFrame and save it to the cache file
    
        cache_df = pd.DataFrame(columns=COLUMN_NAMES)
    else:
        # Load the existing cache file into a DataFrame
        cache_df = pd.read_csv(
            cache_file_path,
            parse_dates=["interval_start_utc", "interval_end_utc"]
        )
        
    return cache_df


def get_missing_periods(
    df: pd.DataFrame,
    start_time: datetime,
    end_time: datetime,
) -> List[Tuple[datetime, datetime]]:
    """
    Returns a DataFrame with missing periods between start_time and end_time.
    based on the existing intervals in cache DataFrame.
    """
    # the dataframe should have all the columns n COLUMN_NAMES
    # the rows could be sparce since we concatenate the queries
    # that may span different time periods
    # so we look at price columnn values if not null
    # we are gong to start with the interval_start_utc column in the dataframe
    # if the column does not nclude the start_time then the frst missing period
    # would be from start_time to the first interval_start_utc
    # then we contnue from the interval_start_utc to the end_time
    # and check if any of the intervals are missing value (null prce)
    # lastly we check if the end_time is included in the intervals
    # if not then we add the last period from the last interval_end_utc to end


    existing_periods = pd.to_datetime(
        df.loc[df['price'].notnull(), 'interval_start_utc'].dropna().unique()
    )
    existing_periods = pd.Series(existing_periods).sort_values().to_numpy()
    
    # Determine frequency
    if not df.empty:
        first_valid = df[df['price'].notnull()].iloc[0]
        freq = pd.to_datetime(first_valid['interval_end_utc']) - pd.to_datetime(first_valid['interval_start_utc'])
        # freq = pd.Timedelta('1H')
    else:
        freq = pd.Timedelta('1H')
    freq_timedelta = pd.Timedelta(freq)

    all_periods = pd.date_range(start=start_time, end=end_time - freq_timedelta, freq=freq_timedelta)
    missing_periods = all_periods.difference(existing_periods)

    if len(existing_periods) == 0:
        # All periods are missing
        missing_ranges = [(start_time, end_time)]
        return missing_ranges

    if missing_periods.empty:
        return []

    # Group consecutive missing periods into ranges
    missing_ranges = []
    start = missing_periods[0]
    prev = missing_periods[0]
    for current in missing_periods[1:]:
        if (current - prev) != freq_timedelta:
            # End of a missing range
            missing_ranges.append((start, prev + freq_timedelta))
            start = current
        prev = current
    # Add the last range
    missing_ranges.append((start, prev + freq_timedelta))
    return missing_ranges



def persist_cache_file(
    df: pd.DataFrame,
    iso: ISOType,
    market_type: MarketType,
    price_type: PriceType,
    node: str,
) -> None:
    """
    Persists the DataFrame to a cache file.
    """
    cache_file_path = get_cache_file_path(iso, market_type, price_type, node)
    
    # Ensure the directory exists
    cache_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the DataFrame to CSV
    df.to_csv(cache_file_path, index=False)
