from datetime import datetime
import pandas as pd

from price_analyzer.dtos.basic_types import MarketType, PriceType
from price_analyzer.dtos.prices import Price, PriceLocation

class IPriceService:
    
    def get_price_actual(
        self,
        market_type: MarketType,
        price_type: PriceType,
        node: PriceLocation,
        start_time: datetime,
        end_time: datetime,
        resolution_minutes: int,
    ) -> Price:
        """
        This is an interface for getting actual price data
        """
        raise NotImplementedError
    
    def get_price_actual_df(
        self,
        market_type: MarketType,
        price_type: PriceType,
        node: PriceLocation,
        start_time: datetime,
        end_time: datetime,
        resolution_minutes: int,
    ) -> pd.DataFrame:
        """
        This is an interface for getting actual price data as a DataFrame
        """
        raise NotImplementedError