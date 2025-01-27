
from typing import List

import numpy as np




def calc_price_vector_daily_mean(
    price_vector: List[float],
    daily_resolution: int,
) -> List[float]:
    """
        this is a basic method to get the daily mean values of a price vector
        that is given for multiple days
        Calculate the daily mean values of a price vector.
        We are making the assumption that the price vector is comming with the same resolutoin
        that is given by the daily_resolution parameter.
        Parameters:
        price_vector: List[float]
            The price vector to calculate the daily mean values of, length of vector should be multiple of 24
        daily_resolution: int
            The number of interval in a day (e.g. 24 for hourly data)
    """
    # NOTE: We first validate the inputs to ensure the price vector length is a multiple of 24
    # we calculate the daily mean values by reshaping the price vector
    # we construct the price vector for each day by reshaping the price vector
    # and then calculate the mean of the price vector for each interval, across multiple days

    # Ensure the price vector length is a multiple of daily_resolution
    if len(price_vector) % daily_resolution != 0:
        raise ValueError(f"Length of price_vector should be a multiple of {daily_resolution}")

    # Reshape the price vector to a 2D array where each row represents a day
    reshaped_price_vector = np.reshape(price_vector, (-1, daily_resolution))

    # Calculate the mean of each column (interval) across multiple days
    daily_mean_values = np.mean(reshaped_price_vector, axis=0)

    return daily_mean_values.tolist()


def calc_price_vector_volatility_variance(
    price_vector: List[float],
    base_daily_mean_vals: List[float],
) -> float:
    """
    Calculate the volatility of the price vector, via the variance of the
    noise, relative to the base_daily_mean_vals.
    The base_daily_mean_vals are the mean values of the price vector
    Parameters:
    price_vector: List[float]
        The price vector to calculate the volatility of, length of vector should be multiple of 24
    base_daily_mean_vals: List[float] 
        The mean values of the price vector, length of vector should be 24
    """
    # NOTE: we calculate the variance of the noise, via numpy
    # we construct the mean value price vector for the length of the price vector
    # from the base_daily_mean_vals and 
    # then, we get the noise by subtracting the mean value price vector from the price vector
    # and then calculate the variance of the noise

    # Ensure the price vector length is a multiple of 24
    _validate_inputs(price_vector, base_daily_mean_vals)
    
    # Construct the mean value price vector
    mean_value_price_vector = np.tile(base_daily_mean_vals, len(price_vector) // 24)

    # Calculate the noise
    noise = np.array(price_vector) - mean_value_price_vector

    # Calculate and return the variance of the noise
    return np.var(noise)





def _validate_inputs(price_vector: List[float], base_daily_mean_vals: List[float]) -> None:
    if len(price_vector) % 24 != 0:
        raise ValueError("Length of price_vector should be a multiple of 24")
    if len(base_daily_mean_vals) != 24:
        raise ValueError("Length of base_daily_mean_vals should be 24")
