from dataclasses import dataclass
from typing import List
from datetime import datetime, timedelta

from price_analyzer.dtos.basic_types import PriceType, PriceLocationType


@dataclass
class PriceLocation:
    name: str
    location_type: PriceLocationType

@dataclass
class Price:
    price_type: PriceType
    values: List[float]
    start_time: datetime   # NOTE: let's come back to this
    interval_duration: timedelta
    