import pytest
from datetime import datetime, timedelta
import pandas as pd
from pytz import utc
from price_analyzer.data_client.api.gridstatus_price import GridStatusPriceClient
from tests.data_client.api.component.utils import GridStatusClientMock
from price_analyzer.dtos.basic_types import ISOType, MarketType, PriceType, ResolutionType
MOCK_GRIDSTATUS_CLIENT = True


    
class TestGridStatusPriceClient:

    @pytest.fixture
    def client(self):
        if MOCK_GRIDSTATUS_CLIENT:
            return GridStatusPriceClient(GridStatusClientMock())
        else:
            return GridStatusPriceClient()

    def test_get_price_actual_happy_path(self, client):
        result = client.get_price_actual(
            iso=ISOType.ERCOT,
            market_type=MarketType.DAM,
            price_type=PriceType.SPP,
            node="HB_HOUSTON",
            start_time=datetime.now(utc) - timedelta(days=2),
            end_time=datetime.now(utc) - timedelta(days=1),
            resolution_type=ResolutionType.HOURLY,
        )
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        


    # more tests here around the various input arguments etc.


# if __name__ == "__main__":
#     # pytest.main(['-k', 'TestGridStatusPriceClient', '--pdb'])
#     test_client = TestGridStatusPriceClient()
#     test_client.test_get_price_actual_happy_path(test_client.client())