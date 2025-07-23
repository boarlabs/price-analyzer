from datetime import datetime
from zoneinfo import ZoneInfo

from price_analyzer.data_client.service.gridstatus.price_service import PriceService
from price_analyzer.data_client.api.gridstatus_price import GridStatusPriceClient   
from price_analyzer.dtos.basic_types import MarketType, PriceType, ISOType
from price_analyzer.dtos.prices import PriceLocation, PriceLocationType
from price_analyzer.tasks.get_price_stats import (
    get_price_stats,
    get_period_price_stats,
    get_weekly_price_stats,
    get_hourly_mean,
    get_dam_rtm_price_stats,
)


UTC = ZoneInfo("UTC")
TIMEZONE = ZoneInfo("US/Central")

def main():

    price_service = PriceService(price_data_client=GridStatusPriceClient())
    price_service.initialize_service_iso(ISOType.ERCOT)

    daily_stats, daily_stats_extended = get_price_stats(
        price_service=price_service,
        market_type=MarketType.DAM,
        price_type=PriceType.SPP,
        location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
        start_time=datetime(2024, 10, 1, 6, tzinfo=UTC),
        end_time=datetime(2024, 10, 30, 5, tzinfo=UTC),
    )

    peak_offpeak_periods, peak_offpeak_periods_stats = get_period_price_stats(
        price_service=price_service,
        market_type=MarketType.DAM,
        price_type=PriceType.SPP,
        location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
        start_time=datetime(2024, 10, 1, 6, tzinfo=UTC),
        end_time=datetime(2024, 10, 30, 5, tzinfo=UTC),
    )

    weekly_stats, weekly_stats_extended, weekday_weekend_stats = get_weekly_price_stats(
        price_service=price_service,
        market_type=MarketType.DAM,
        price_type=PriceType.SPP,
        location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
        start_time=datetime(2024, 10, 1, 6, tzinfo=UTC),
        end_time=datetime(2024, 10, 30, 5, tzinfo=UTC),
    )

    price_hourly_mean, hourly_variations = get_hourly_mean(
        price_service=price_service,
        market_type=MarketType.DAM,
        price_type=PriceType.SPP,
        location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
        start_time=datetime(2024, 10, 1, 6, tzinfo=UTC),
        end_time=datetime(2024, 10, 30, 5, tzinfo=UTC),
    )

    dart_stats = get_dam_rtm_price_stats(
        price_service=price_service,
        location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
    )
  

if __name__ == "__main__":
    main()