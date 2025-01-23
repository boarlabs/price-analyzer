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
    REGUP = 'regulation_up'
    REGDOWN = 'regulation_down'
    RRS = 'responsive_reserves'
    

class PriceLocationType(Enum):
    HUB = 'Trading Hub'
    NODE = 'Resource Node'
    ZONE = 'Load Zone'
    
