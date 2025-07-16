
ACTUAL_PRICE_TABLE_COLUMNS = ["target_time", "product_name", "value"]


DAILY_PRICE_SAMPLES = {
    "energy": {
        1: [8]*7+[15]*5 [21]*5+ [24]*4 + [11]*3,
    },
    "regulation":{
        1: [3]*12  + [7]*5 + [4]*4 + [2]*3,
    },
    "reserve": {
        1: [2]*12 + [5]*5 + [1]*7,
    },
}


PRICE_NAMES = ["spp", "regup", "regdown", "rrs" ]
