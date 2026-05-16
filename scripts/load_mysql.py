from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"


def build_mysql_url() -> str:
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "123456")
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "metroflow")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def main() -> None:
    engine = create_engine(build_mysql_url())

    dim_station = pd.read_csv(PROCESSED_DIR / "dim_station.csv")
    fact_hourly_flow = pd.read_csv(PROCESSED_DIR / "fact_hourly_flow.csv")
    macro_city_flow = pd.read_csv(PROCESSED_DIR / "macro_city_flow_clean.csv")

    dim_station.to_sql("dim_station", engine, if_exists="append", index=False, chunksize=500)
    fact_hourly_flow.to_sql("fact_hourly_flow", engine, if_exists="append", index=False, chunksize=2000)
    macro_city_flow.to_sql("macro_city_flow", engine, if_exists="append", index=False, chunksize=200)

    print("MySQL load completed.")


if __name__ == "__main__":
    main()
