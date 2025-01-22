from enum import Enum


class ISOType(Enum):
    ERCOT = 'ercot'
    CAISO = 'caiso'

class MarketType(Enum):
    DAM = 'day_ahead'
    RTM = 'real_time'

class PriceType(Enum):
    LMP = 'lmp'
    SPP = 'spp'
    


class ResolutionType(Enum):
    # NOTE: for enums the convention typically is to use all caps for the name
    # and lower case for values or use auto(), however, we use it to have the value
    # matching the external resource, (our own db or api, or external api)
    HOURLY = 'hourly'
    MIN15 = '15_min'
    MIN5 = '5_min'