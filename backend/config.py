from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DATA_SOURCE = os.getenv("DATA_SOURCE", "csv").lower()

    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "metroflow")

    DIM_STATION_FILE = DATA_DIR / "dim_station.csv"
    FACT_HOURLY_FILE = DATA_DIR / "fact_hourly_flow.csv"
    MACRO_CITY_FILE = DATA_DIR / "macro_city_flow_clean.csv"
