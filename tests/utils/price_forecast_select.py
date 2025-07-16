import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("US/Central")
UTC = ZoneInfo("UTC")

def get_price_forecast_last(
    product_name: str, 
    forecast_table: pd.DataFrame, 
    start_time_utc: datetime,
    end_time_utc: datetime,
    as_of_utc: datetime,
    quantile: float = 0.5,    
) -> pd.DataFrame:
    """
    okay since we want the last forcast, if the as of time is  after the end-time 
    we would have each row selected from a single forecast_at time
    """

    forecast_table = forecast_table.copy()
    forecast_table["target_time_utc"] = forecast_table["target_time"].dt.tz_convert(UTC)
    forecast_table["forecast_at_utc"] = forecast_table["forecast_at"].dt.tz_convert(UTC)

    # Filter by product name and target_time  and forecast_at time 
    filtered_table = forecast_table[
        (forecast_table["product_name"] == product_name) &
        (forecast_table["target_time_utc"] >= start_time_utc) &
        (forecast_table["target_time_utc"] < end_time_utc) &
        (forecast_table["forecast_at_utc"] <= as_of_utc) &
        (forecast_table["quantile"] == quantile)
    ]
    
    # sort by target_time_utc and forecast_at_utc 
    filtered_table = filtered_table.sort_values(by=["target_time_utc", "forecast_at_utc"])
        
    # Get the last forecast for each target_time
    last_forecast = filtered_table.groupby("target_time_utc").last().reset_index()
    return last_forecast[["target_time_utc", "forecast_at_utc", "forecast_value" ]]




