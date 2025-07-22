from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from price_analyzer.data_client.service.iprice_service import IPriceService
from price_analyzer.dtos.basic_types import MarketType, PriceType, ISOType
from price_analyzer.dtos.prices import PriceLocation, PriceLocationType
from price_analyzer.models.price_stats import (
    price_weekly_stats, 
    price_daily_stats_extended, 
    get_price_peak_offpeak_hours,
    get_price_peak_offpeak_hours_alt,
    price_daily_stats_infer_peak,
    price_stat_weekly_extended,
    price_stat_weekly_weekday_separated,
    price_hourly_means,
    price_hourly_variations,
    dam_rtm_hourly_dif_short_term,
)

from price_analyzer.data_client.service.gridstatus.price_service import PriceService
from price_analyzer.data_client.api.gridstatus_price import GridStatusPriceClient   

UTC = ZoneInfo("UTC")
TIMEZONE = ZoneInfo("US/Central")

def get_price_stats(
    price_service: IPriceService,
    market_type: MarketType,     
    price_type: PriceType,
    location: PriceLocation,
    start_time: datetime,
    end_time: datetime,        
):
    
    df = price_service.get_price_actual_df(
        market_type=market_type,
        price_type=price_type,
        location=location,
        start_time=start_time,
        end_time=end_time,
        resolution_minutes=60,
    )
    
    # df2 = price_daily_stats(df)
    
    df4 = price_daily_stats_extended(df, timezone=TIMEZONE)
    return df4

def get_period_price_stats(
    price_service: IPriceService,
    market_type: MarketType,     
    price_type: PriceType,
    location: PriceLocation,
    start_time: datetime,
    end_time: datetime,        
):
    df = price_service.get_price_actual_df(
        market_type=market_type,
        price_type=price_type,
        location=location,
        start_time=start_time,
        end_time=end_time,
        resolution_minutes=60,
    )
    
    # out = get_price_peak_offpeak_hours(
    #     df=df,
    #     timezone=TIMEZONE,
    # )
    # out_alt = get_price_peak_offpeak_hours_alt(
    #     df=df,
    #     timezone=TIMEZONE,
    # )
    stat_df = price_daily_stats_infer_peak(df, TIMEZONE)
    return stat_df

def get_weekly_price_stats(
    price_service: IPriceService,
    market_type: MarketType,     
    price_type: PriceType,
    location: PriceLocation,
    start_time: datetime,
    end_time: datetime,           
):
    df = price_service.get_price_actual_df(
        market_type=market_type,
        price_type=price_type,
        location=location,
        start_time=start_time,
        end_time=end_time,
        resolution_minutes=60,
    )
    # df3 = price_weekly_stats(df)
    # df = price_stat_weekly_extended(df, TIMEZONE)

    df = price_stat_weekly_weekday_separated(df, TIMEZONE)
    print(df.head())
    return  

def get_hourly_mean(
    price_service: IPriceService,
    market_type: MarketType,     
    price_type: PriceType,
    location: PriceLocation,
    start_time: datetime,
    end_time: datetime,               
):
    
    df = price_service.get_price_actual_df(
            market_type=market_type,
            price_type=price_type,
            location=location,
            start_time=start_time,
            end_time=end_time,
            resolution_minutes=60,
        )
    
    price_m = price_hourly_means(df, TIMEZONE)
    print(price_m)

    df = price_hourly_variations(df, TIMEZONE)
    print(df.head())

def get_dam_rtm_price_stats(
    price_service: IPriceService,
    location: PriceLocation,
):
    # first need to establish the trends of the prices in the DAM market
    start_time_dam = datetime(2024, 10, 1, 6, tzinfo=UTC)
    end_time_dam = datetime(2024, 10, 30, 5, tzinfo=UTC)

    dam_df = price_service.get_price_actual_df(
        market_type=MarketType.DAM,
        price_type=PriceType.SPP,
        location=location,
        start_time=start_time_dam,
        end_time=end_time_dam,
        resolution_minutes=60,
    )

    peak_hours, offpeak_hours, midpeak_hours = get_price_peak_offpeak_hours_alt(
        df=dam_df,
        timezone=TIMEZONE,
    )

    start_time_rtm = datetime(2024, 10, 1, 6, tzinfo=UTC)
    end_time_rtm = datetime(2024, 10, 5, 5, tzinfo=UTC)

    rtm_df = price_service.get_price_actual_df(
        market_type=MarketType.RTM,
        price_type=PriceType.SPP,
        location=location,
        start_time=start_time_rtm,
        end_time=end_time_rtm,
        resolution_minutes=15,
    )

    df = dam_rtm_hourly_dif_short_term(
        dam_df=dam_df,
        rtm_df=rtm_df,
        peak_hours=peak_hours,
        offpeak_hours=offpeak_hours,
        midpeak_hours=midpeak_hours,
        timezone=TIMEZONE,
    )
    return df



def main():

    price_service = PriceService(price_data_client=GridStatusPriceClient())
    price_service.initialize_service_iso(ISOType.ERCOT)

    # get_price_stats(
    #     price_service=price_service,
    #     market_type=MarketType.DAM,
    #     price_type=PriceType.SPP,
    #     location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
    #     start_time=datetime(2024, 10, 1, 6, tzinfo=UTC),
    #     end_time=datetime(2024, 10, 30, 5, tzinfo=UTC),
    # )

    # get_weekly_price_stats(
    #     price_service=price_service,
    #     market_type=MarketType.DAM,
    #     price_type=PriceType.SPP,
    #     location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
    #     start_time=datetime(2024, 10, 1, 6, tzinfo=UTC),
    #     end_time=datetime(2024, 10, 30, 5, tzinfo=UTC),
    # )

    # get_hourly_mean(
    #     price_service=price_service,
    #     market_type=MarketType.DAM,
    #     price_type=PriceType.SPP,
    #     location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
    #     start_time=datetime(2024, 10, 1, 6, tzinfo=UTC),
    #     end_time=datetime(2024, 10, 30, 5, tzinfo=UTC),
    # )

    get_dam_rtm_price_stats(
        price_service=price_service,
        location=PriceLocation(name="HB_HOUSTON", location_type=PriceLocationType.HUB),
    )
  

if __name__ == "__main__":
    main()