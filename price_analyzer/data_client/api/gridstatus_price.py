import os
from datetime import datetime
from typing import Tuple, Dict
import pandas as pd

from gridstatusio import GridStatusClient

from price_analyzer.dtos.basic_types import ISOType, MarketType, PriceType

QUERY_LIMIT = 10_000



PRICE_DATA_NAME_MAP: Dict[Tuple[MarketType, PriceType], str] = {
    (MarketType.DAM, PriceType.SPP): "ercot_spp_day_ahead_hourly",
    (MarketType.RTM, PriceType.SPP): "ercot_spp_real_time_15_min",
    (MarketType.RTM, PriceType.LMP): "ercot_lmp_by_settlement_point",
    (MarketType.DAM, PriceType.LMP): "ercot_lmp_by_bus_dam",  # NOTE: usually we care about the three above
}


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
    
    
    def get_energy_price_actual(
        self,
        iso: ISOType,
        market_type: MarketType,
        price_type: PriceType,
        node: str,
        start_time: datetime,
        end_time: datetime,
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
        _validate_inputs(price_type, node, start_time, end_time)
        
        data_set_name: str = _construct_dataset_name(iso, market_type, price_type)
        start_ts, end_ts = _convert_to_timestamps(start_time, end_time)
        results: pd.DataFrame =  self.client.get_dataset(
            dataset=data_set_name,
            start=start_ts,
            end=end_ts,
            limit=QUERY_LIMIT,
            filter_column="location",
            filter_value=node,
        )
        return _reformat_results(results, price_type)
        

    def get_as_price_actual(
        self,
        iso: ISOType,
        market_type: MarketType,
        start_time: datetime,
        end_time: datetime,
    ) -> pd.DataFrame:
        raise NotImplementedError("this method is not implemented yet")
        # NOTE: so I have to come back to this but based on the question it seems we only care about 
        # energy prices, but here is one note, for the service we probably not going to do per product
        # query, since this returns all of the as prices in different columns.
        # table name is ercot_as_prices


def _reformat_results(results: pd.DataFrame, price_type: PriceType) -> pd.DataFrame:
    # here I want to change the column "spp" or "lmp" to "price"
    if price_type == PriceType.SPP:
        results.rename(columns={"spp": "price"}, inplace=True)
    elif price_type == PriceType.LMP:
        results.rename(columns={"lmp": "price"}, inplace=True)
    return results       

def _convert_to_timestamps(start_time: datetime, end_time: datetime) -> Tuple[str, str]:
    """ this function converts the datetime objects to timestamps in isoforamt
    """
    start_ts = start_time.isoformat()
    end_ts = end_time.isoformat()
    return start_ts, end_ts

def _construct_dataset_name(iso: ISOType, market_type: MarketType, price_type: PriceType) -> str:
    """ this function constructs the dataset name for the gridstatus.io api
    """
    # NOTE: update I checked an the pattern for dataset name for LMP will not follow same as SPP :/
    if iso == ISOType.ERCOT:
        return PRICE_DATA_NAME_MAP[(market_type, price_type)]
    else:
        raise ValueError("only ERCOT is supported for now")




def _validate_inputs(price_type: PriceType, node: str, start_time: datetime, end_time: datetime) -> None:
    """ all the publich methods should validate inputs.
    here we validate that for example start-time and end-times are
    in UTC start-time is before end-time and so on.
    maybe nodenames need to be all lowercase, etc.
    most importantly we validate that the price_type is either LMP or SPP
    """
    pass