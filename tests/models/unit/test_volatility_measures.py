import pytest

from price_analyzer.models.volatility_measures import (
    calc_price_vector_daily_mean,
    calc_price_vector_volatility_variance,
    _validate_inputs
)

def test_calc_price_vector_daily_mean():
    price_vector = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    daily_resolution = 24
    expected_result = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    result = calc_price_vector_daily_mean(price_vector, daily_resolution)
    assert result == expected_result

def test_calc_price_vector_daily_mean_invalid_length():
    price_vector = [1, 2, 3, 4, 5]
    daily_resolution = 24
    with pytest.raises(ValueError):
        calc_price_vector_daily_mean(price_vector, daily_resolution)

def test_calc_price_vector_volatility_variance():
    price_vector = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    base_daily_mean_vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    expected_result = 0.0
    result = calc_price_vector_volatility_variance(price_vector, base_daily_mean_vals)
    assert result == expected_result

def test_calc_price_vector_volatility_variance_invalid_length():
    price_vector = [1, 2, 3, 4, 5]
    base_daily_mean_vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    with pytest.raises(ValueError):
        calc_price_vector_volatility_variance(price_vector, base_daily_mean_vals)

def test_validate_inputs_valid():
    price_vector = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    base_daily_mean_vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    _validate_inputs(price_vector, base_daily_mean_vals)  # Should not raise any exception

def test_validate_inputs_invalid_price_vector_length():
    price_vector = [1, 2, 3, 4, 5]
    base_daily_mean_vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    with pytest.raises(ValueError):
        _validate_inputs(price_vector, base_daily_mean_vals)

def test_validate_inputs_invalid_base_daily_mean_vals_length():
    price_vector = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    base_daily_mean_vals = [1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        _validate_inputs(price_vector, base_daily_mean_vals)