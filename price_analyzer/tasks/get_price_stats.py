from datetime import datetime
from zoneinfo import ZoneInfo
from price_analyzer.data_client.service.iprice_service import IPriceService
from price_analyzer.dtos.basic_types import MarketType, PriceType
from price_analyzer.dtos.prices import PriceLocation
from price_analyzer.models.price_stats import (
    price_weekly_stats, 
    price_daily_stats,
    price_daily_stats_extended, 
    price_peak_offpeak_hours_aprox,
    price_peak_offpeak_hours,
    price_daily_stats_infer_peak,
    price_stat_weekly_extended,
    price_stat_weekly_weekday_separated,
    price_hourly_means,
    price_hourly_variations,
    dam_rtm_hourly_dif_short_term,
)



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
    
    daily_stats = price_daily_stats(df, timezone=TIMEZONE)
    
    daily_stats_extended = price_daily_stats_extended(df, timezone=TIMEZONE)
    return daily_stats, daily_stats_extended

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
    
    # peak_hours_aprox = price_peak_offpeak_hours_aprox(
    #     df=df,
    #     timezone=TIMEZONE,
    # )
    peak_hours = price_peak_offpeak_hours(
        df=df,
        timezone=TIMEZONE,
    )
    stat_for_periods = price_daily_stats_infer_peak(df, TIMEZONE)
    return peak_hours, stat_for_periods

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
    weekly_stats = price_weekly_stats(df, TIMEZONE)
    weekly_stats_extended = price_stat_weekly_extended(df, TIMEZONE)
    weekday_weekend_stats = price_stat_weekly_weekday_separated(df, TIMEZONE)
    return  weekly_stats, weekly_stats_extended, weekday_weekend_stats

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
    
    price_hourly_mean = price_hourly_means(df, TIMEZONE)
    hourly_variations = price_hourly_variations(df, TIMEZONE)
    return price_hourly_mean, hourly_variations

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

    peak_hours, midpeak_hours, offpeak_hours,  = price_peak_offpeak_hours(
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

    dart_stats = dam_rtm_hourly_dif_short_term(
        dam_df=dam_df,
        rtm_df=rtm_df,
        peak_hours=peak_hours,
        offpeak_hours=offpeak_hours,
        midpeak_hours=midpeak_hours,
        timezone=TIMEZONE,
    )
    return dart_stats


