import pytest
from unittest.mock import patch
import os
import pandas as pd
from datetime import datetime, timedelta
from pytz import utc

from price_analyzer.data_client.api.gridstatus_price import GridStatusPriceClient
from gridstatusio import GridStatusClient
from price_analyzer.dtos.basic_types import ISOType, MarketType, PriceType



class TestGridStatusPriceClient:
    @classmethod
    def setup_class(cls):
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'test_data.csv')
        cls.mock_data = pd.read_csv(file_path)
       
        cls.patcher = patch.object(GridStatusClient, 'get_dataset', return_value=cls.mock_data)
    
    def test_process_data(self):
        
        grid_status_api = GridStatusClient()
        client = GridStatusPriceClient(grid_status_api)
      
        result =client.get_energy_price_actual(
            iso=ISOType.ERCOT,
            market_type=MarketType.DAM,
            price_type=PriceType.SPP,
            node="HB_HOUSTON",
            start_time=datetime.now(utc) - timedelta(days=2),
            end_time=datetime.now(utc) - timedelta(days=1),
        )
        assert result is not None