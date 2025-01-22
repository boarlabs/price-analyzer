import os
from datetime import datetime
from typing import Tuple
import pandas as pd

from gridstatusio import GridStatusClient

from price_analyzer.dtos.basic_types import ISOType, MarketType, PriceType, ResolutionType

QUERY_LIMIT = 10_000

class GridStatusPriceClient:
    def __init__(
        self,
        api_clinet: GridStatusClient = None,
    ):
        # NOTE: we usualy prefer to pass the api_client and not instantiate it within the class
        # but here to make things easier, we add the option to make it optional.
        if not api_clinet:
            api_key = os.getenv('GRIDSTATUS_API_KEY')
            if not api_key:
                raise EnvironmentError("GRIDSTATUS_API_KEY environment variable not set")
            # ...existing code...

            self.client = GridStatusClient(
                api_key=api_key,
            )
           
        else:
            self.client = api_clinet
    
    
    def get_price_actual(
        self,
        iso: ISOType,
        market_type: MarketType,
        price_type: PriceType,
        node: str,
        start_time: datetime,
        end_time: datetime,
        resolution_type: ResolutionType,
    ) -> pd.DataFrame:
        """
        This is an implementation to get_price_actual from gridstatus.io api
        the time stamps should be in UTC, this is used for backend!
        also here we limit this query to one node at a time.
        """
        # NOTE: looks like that there is the client only returns dataframes
        # I thought there is a parameter to receive a json/dict response
        # but that method is the get method in the client that has a more involved parameter set
        # so we would deal with dataframes for the moment.
        _validate_inputs(node, start_time, end_time)
        
        data_set_name: str = _construct_dataset_name(iso, market_type, price_type, node, resolution_type)
        start_ts, end_ts = _convert_to_timestamps(start_time, end_time)
        results =  self.client.get_dataset(
            dataset=data_set_name,
            start=start_ts,
            end=end_ts,
            limit=QUERY_LIMIT,
            filter_column="location",
            filter_value=node,
        )
        return results
        

def _convert_to_timestamps(start_time: datetime, end_time: datetime) -> Tuple[str, str]:
    """ this function converts the datetime objects to timestamps in isoforamt
    """
    start_ts = start_time.isoformat()
    end_ts = end_time.isoformat()
    return start_ts, end_ts

def _construct_dataset_name(iso: ISOType, market_type: MarketType, price_type: PriceType, node: str, resolution_type: ResolutionType) -> str:
    """ this function constructs the dataset name for the gridstatus.io api
    """
    return f"{iso.value}_{price_type.value}_{market_type.value}_{resolution_type.value}"


def _validate_inputs(node: str, start_time: datetime, end_time: datetime) -> None:
    """ all the publich methods should validate inputs.
    here we validate that for example start-time and end-times are
    in UTC start-time is before end-time and so on.
    maybe nodenames need to be all lowercase, etc.
    """
    pass