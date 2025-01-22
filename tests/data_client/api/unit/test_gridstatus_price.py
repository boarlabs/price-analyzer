# import os
# import pytest
# from datetime import datetime
# from unittest.mock import patch, MagicMock
# from price_analyzer.dtos.basic_types import ISOType, MarketType, PriceType, ResolutionType

# from price_analyzer.data_client.api.gridstatus_price import (
#     GridStatusPriceClient,
#     _convert_to_timestamps,
#     _construct_dataset_name,
#     _validate_inputs,
# )


# @pytest.fixture
# def mock_env_api_key(monkeypatch):
#     monkeypatch.setenv('GRIDSTATUS_API_KEY', 'test_api_key')

# @pytest.fixture
# def client(mock_env_api_key):
#     return GridStatusPriceClient()

# def test_init_no_api_key(monkeypatch):
#     monkeypatch.delenv('GRIDSTATUS_API_KEY', raising=False)
#     with pytest.raises(EnvironmentError, match="GRIDSTATUS_API_KEY environment variable not set"):
#         GridStatusPriceClient()

# def test_init_with_api_key(client):
#     assert client.api_key == 'test_api_key'

# def test_convert_to_timestamps():
#     start_time = datetime(2023, 1, 1, 0, 0, 0)
#     end_time = datetime(2023, 1, 2, 0, 0, 0)
#     start_ts, end_ts = _convert_to_timestamps(start_time, end_time)
#     assert start_ts == "2023-01-01T00:00:00"
#     assert end_ts == "2023-01-02T00:00:00"

# def test_construct_dataset_name():
#     dataset_name = _construct_dataset_name(
#         ISOType.ERCOT, MarketType.DAM, PriceType.SPP, ResolutionType.HOURLY
#     )
#     assert dataset_name == "ercot_spp_dam_hourly"


# @patch.object(GridStatusPriceClient, 'client', create=True)
# def test_get_price_actual(mock_client, client):
#     iso = ISOType.CAISO
#     market_type = MarketType.REAL_TIME
#     price_type = PriceType.LMP
#     node = "node1"
#     start_time = datetime(2023, 1, 1, 0, 0, 0)
#     end_time = datetime(2023, 1, 2, 0, 0, 0)
#     resolution_type = ResolutionType.FIVE_MIN

#     client.get_price_actual(iso, market_type, price_type, node, start_time, end_time, resolution_type)

#     mock_client.get_dataset.assert_called_once()
#     args, kwargs = mock_client.get_dataset.call_args
#     assert kwargs['dataset'] == "CAISO_LMP_REAL_TIME_FIVE_MIN"
#     assert kwargs['start'] == "2023-01-01T00:00:00"
#     assert kwargs['end'] == "2023-01-02T00:00:00"
#     assert kwargs['limit'] == 10000
#     assert kwargs['filter_column'] == "location"
#     assert kwargs['filter_value'] == "node1"



# TODO Come back here and clean this up