from __future__ import annotations

from functools import lru_cache

import pandas as pd

from config import Config
from db.mysql import get_engine


class DataStore:
    def __init__(self):
        self.source = Config.DATA_SOURCE

    @lru_cache(maxsize=1)
    def station_dim(self) -> pd.DataFrame:
        if self.source == "mysql":
            return pd.read_sql("SELECT * FROM dim_station", get_engine())
        return pd.read_csv(Config.DIM_STATION_FILE)

    @lru_cache(maxsize=1)
    def hourly_fact(self) -> pd.DataFrame:
        if self.source == "mysql":
            return pd.read_sql("SELECT * FROM fact_hourly_flow", get_engine())
        return pd.read_csv(Config.FACT_HOURLY_FILE)

    @lru_cache(maxsize=1)
    def macro_city(self) -> pd.DataFrame:
        if self.source == "mysql":
            return pd.read_sql("SELECT * FROM macro_city_flow", get_engine())
        return pd.read_csv(Config.MACRO_CITY_FILE)


store = DataStore()
