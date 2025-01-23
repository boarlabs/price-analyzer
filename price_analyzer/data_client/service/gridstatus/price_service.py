from datetime import datetime, timedelta
from typing import List
import pandas as pd
import numpy as np
from price_analyzer.data_client.service.iprice_service import IPriceService
from price_analyzer.dtos.prices import Price, PriceLocation
from price_analyzer.dtos.basic_types import MarketType, PriceType, ResolutionType, ISOType
from price_analyzer.data_client.api.gridstatus_price import GridStatusPriceClient


class PriceService(IPriceService):
    def __init__(
        self, 
        price_data_client: GridStatusPriceClient,
    ):
        self.price_data_client = price_data_client
        self._iso = None
    
    @property
    def iso(self) -> ISOType:
        if self._iso is None:
            raise ValueError("ISO is not initialized")
        return self._iso
    
    def initilize_service_iso(self, iso: ISOType):
        """
        so we can either pass it in each call, but normally we deal with the same market,
        so might be annoying to pass it in each call,
        or we could put it in the constructor, but again normally we might not have the pieace of 
        info in the very top levels that we instantiate the service,
        so for now I decied to initialize it here
        """
        self._iso = iso

    def get_price_actual(
        self,
        market_type: MarketType,
        price_type: PriceType,
        location: PriceLocation,
        start_time: datetime,
        end_time: datetime,
        resolution_minutes: int,
    ) -> Price:
        """
        This is an implementation for getting actual energy price data
        """
       
        _validate_inputs(market_type, price_type, location, start_time, end_time, resolution_minutes)
        
        if price_type in [PriceType.LMP, PriceType.SPP]:
            return self._get_energy_price_actual(market_type, price_type, location, start_time, end_time, resolution_minutes)
        elif price_type in [PriceType.REGUP, PriceType.REGDOWN, PriceType.RRS]:
            return self._get_as_price_actual(
                price_type,
                start_time,
                end_time,
                resolution_minutes
            )
        else:
            raise ValueError("Invalid price type")
        
    
    def _get_as_price_actual(
        self,
        price_type: PriceType,
        start_time: datetime,
        end_time: datetime,
        resolution_minutes: int,
    ) -> Price:
       raise NotImplementedError
    
    def _get_energy_price_actual(
        self,
        market_type: MarketType,
        price_type: PriceType,
        location: PriceLocation,
        start_time: datetime,
        end_time: datetime,
        resolution_minutes: int,
    ) -> Price:    
        df: pd.DataFrame = self.price_data_client.get_energy_price_actual(
            iso=self.iso,
            market_type=market_type,
            price_type=price_type,
            node=location.name,
            start_time=start_time,
            end_time=end_time,
        )
        return _convert_df_to_energy_price(df, start_time, end_time, resolution_minutes, price_type)
    




def _convert_df_to_energy_price(
    df: pd.DataFrame,
    start_time: datetime,
    end_time: datetime, 
    resolution_minutes: int,
    price_type: PriceType,
) -> Price:
    """
    in this method we sort the dataframe by interval start,
    then check for missing intervals, if any, and fill them with NaN,
    then based on the resolution minutes, we could do some resampling
    and convert the dataframe to a Price object
    """
    df = df.sort_values(by='interval_start_utc')
    df.set_index('interval_start_utc', inplace=True)
    
    # Create a date range with the given resolution
    df_resampled = resample_dataframe(df, resolution_minutes)
    
    # Convert the dataframe to a Price object
    price_values: List[float]= df_resampled['price'].tolist()
    
    return Price(
        price_type=price_type,
        start_time=start_time,
        interval_duration=timedelta(minutes=resolution_minutes),
        resolution_minutes=resolution_minutes,
        values=price_values
    )


def _validate_inputs(
    market_type: MarketType,
    price_type: PriceType,
    node: PriceLocation,
    start_time: datetime,
    end_time: datetime,
    resolution_minutes: int,
):
    """
    here we will add some validation for the inputs
    particularly the start and end times and resolution,
    I think even though we specify the resolution in minutes, 
    it is not going to be good to allow any resolution.
    """
    pass


def resample_dataframe(df, resolution_minutes):
    # Infer the original resolution from the first row
    original_resolution = (
        df['interval_end_utc'].iloc[0] - df['interval_start_utc'].iloc[0]
    ).seconds // 60

    # Create a date range with the desired resolution
    date_range = pd.date_range(
        start=df['interval_start_utc'].min(), 
        end=df['interval_end_utc'].max(), 
        freq=f'{resolution_minutes}T',
    )

    # Set the interval_start as the index
    df.set_index('interval_start_utc', inplace=True)

    if resolution_minutes < original_resolution:
        # Downsampling
        df_resampled = df.resample(f'{resolution_minutes}T').mean()
    else:
        # Upsampling
        df_resampled = df.resample(f'{resolution_minutes}T').interpolate(method='linear')

    # Reindex to ensure the DataFrame matches the desired date range
    df_resampled = df_resampled.reindex(date_range, fill_value=np.nan)

    return df_resampled
