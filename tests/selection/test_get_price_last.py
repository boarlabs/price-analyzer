import pytest

from tests.utils.rtm_price_forecast_mock import PRICE_NAMES, create_mock_forecast_table
from datetime import datetime
from zoneinfo import ZoneInfo
from tests.utils.price_forecast_select import get_price_forecast_last

TIMEZONE = ZoneInfo("US/Central")
UTC = ZoneInfo("UTC")

def test_get_price_last_as_of_before():
    
    # Setup
    # Create a mock table with the specified columns
    mock_table = create_mock_forecast_table(
        start_time=datetime(2023, 10, 1, tzinfo=TIMEZONE),
        end_time=datetime(2023, 10, 5, tzinfo=TIMEZONE)
    )

    # print(mock_table.head(10))
    as_of_time = datetime(2023, 10, 1, 2, 0,0, tzinfo=TIMEZONE).astimezone(UTC)
    start_time_utc = datetime(2023, 10, 1,5, 0, 0, tzinfo=TIMEZONE).astimezone(UTC)
    end_time_utc = datetime(2023, 10, 1, 6, 0, 0, tzinfo=TIMEZONE).astimezone(UTC)
    product_name = "spp"

    # arrange
    expected_columns = ["target_time_utc", "forecast_at_utc", "forecast_value"]

    expected_results = mock_table[
        (mock_table["product_name"] == product_name) &
        (mock_table["target_time"].dt.tz_convert(UTC) >= start_time_utc) &
        (mock_table["target_time"].dt.tz_convert(UTC) < end_time_utc) &
        (mock_table["forecast_at"].dt.tz_convert(UTC) <= as_of_time) &
        (mock_table["quantile"] == 0.5)
    ].sort_values(by=["forecast_at"]).groupby("target_time").tail(1)
    # print(expected_results.head(10))
    expected_results["target_time_utc"] = expected_results["target_time"].dt.tz_convert(UTC)
    expected_results["forecast_at_utc"] = expected_results["forecast_at"].dt.tz_convert(UTC)
    expected_results = expected_results[expected_columns]
    expected_results = expected_results.sort_values(by=["target_time_utc"]).reset_index(drop=True)
    # print(expected_results.head(10))
    # act
    result = get_price_forecast_last(
        product_name=product_name,
        forecast_table=mock_table,
        start_time_utc=start_time_utc,
        end_time_utc=end_time_utc,
        as_of_utc=as_of_time,
        quantile=0.5
    )
    # print(result.head(10))
    # assert
    assert result.equals(expected_results), f"Expected:\n{expected_results}\nGot:\n{result}"


def test_get_price_last_as_of_middle():

    # Setup
    # Create a mock table with the specified columns
    mock_table = create_mock_forecast_table(
        start_time=datetime(2023, 10, 1, tzinfo=TIMEZONE),
        end_time=datetime(2023, 10, 5, tzinfo=TIMEZONE)
    )

    # print(mock_table.head(10))
    as_of_time = datetime(2023, 10, 1, 6, 0,0, tzinfo=TIMEZONE).astimezone(UTC)
    start_time_utc = datetime(2023, 10, 1,5, 0, 0, tzinfo=TIMEZONE).astimezone(UTC)
    end_time_utc = datetime(2023, 10, 1, 8, 0, 0, tzinfo=TIMEZONE).astimezone(UTC)
    product_name = "spp"

    # arrange
    expected_columns = ["target_time_utc", "forecast_at_utc", "forecast_value"]

    expected_results = mock_table[
        (mock_table["product_name"] == product_name) &
        (mock_table["target_time"].dt.tz_convert(UTC) >= start_time_utc) &
        (mock_table["target_time"].dt.tz_convert(UTC) < end_time_utc) &
        (mock_table["forecast_at"].dt.tz_convert(UTC) <= as_of_time) &
        (mock_table["quantile"] == 0.5)
    ].sort_values(by=["forecast_at"]).groupby("target_time").tail(1)
    # print(expected_results.head(10))
    expected_results["target_time_utc"] = expected_results["target_time"].dt.tz_convert(UTC)
    expected_results["forecast_at_utc"] = expected_results["forecast_at"].dt.tz_convert(UTC)
    expected_results = expected_results[expected_columns]
    expected_results = expected_results.sort_values(by=["target_time_utc"]).reset_index(drop=True)
    # print(expected_results.head(10))
    # act
    result = get_price_forecast_last(
        product_name=product_name,
        forecast_table=mock_table,
        start_time_utc=start_time_utc,
        end_time_utc=end_time_utc,
        as_of_utc=as_of_time,
        quantile=0.5
    )
    # print(result.head(10))
    # assert
    assert result.equals(expected_results), f"Expected:\n{expected_results}\nGot:\n{result}"

if __name__ == "__main__":
    test_get_price_last_as_of_middle()