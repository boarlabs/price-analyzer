import pandas as pd

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("US/Central")

FORECAST_TABLE_COLUMNS = ["target_time","forecast_at", "product_name", "forecast_value", "quantile"]

PRICE_NAMES = ["spp", "regup", "regdown", "rrs" ]


DAILY_PRICE_SAMPLES = {
    "spp": {
        1: [8]*7+[15]*5 + [21]*5+ [24]*4 + [11]*3,
    },
    "regup":{
        1: [3]*12  + [7]*5 + [4]*4 + [2]*3,
    },
    "regdown":{
        1: [4.5]*12  + [5.6]*5 + [3]*4 + [2]*3,
    },
    "rrs": {
        1: [2]*12 + [5]*5 + [1]*7,
    },
}


def create_mock_forecast_table(start_time: datetime, end_time: datetime) -> pd.DataFrame:

    """
    create a mock forecast table with specified start and end times.
    The table will have a hourly frequency and include all products.
    """

    time_range = pd.date_range(start=start_time, end=end_time, freq='h', tz=TIMEZONE)
    data = []

    for forecast_time in time_range:
        target_range = pd.date_range(start=forecast_time, end=forecast_time + timedelta(hours=48), freq='h', tz=TIMEZONE)
        for target_time in target_range:
            for product in PRICE_NAMES:
                for quantile in [0.1, 0.5, 0.9]:
                    data.append({
                        "target_time": target_time,
                        "forecast_at": forecast_time,
                        "product_name": product,
                        "forecast_value": DAILY_PRICE_SAMPLES[product][1][target_time.hour] + (quantile * 10),  # Example value
                        "quantile": quantile
                    })

    return pd.DataFrame(data, columns=FORECAST_TABLE_COLUMNS)


if __name__ == "__main__":
    # Example usage
    start = datetime(2023, 10, 1, tzinfo=TIMEZONE)
    end = datetime(2023, 10, 3, tzinfo=TIMEZONE)
    mock_table = create_mock_forecast_table(start, end)
    print(mock_table.head())