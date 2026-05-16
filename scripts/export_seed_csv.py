from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"


def main() -> None:
    station = pd.read_csv(PROCESSED_DIR / "dim_station.csv")
    flow = pd.read_csv(PROCESSED_DIR / "fact_hourly_flow.csv")
    macro = pd.read_csv(PROCESSED_DIR / "macro_city_flow_clean.csv")

    summary = {
        "station_count": len(station),
        "transfer_station_count": int(station["is_transfer"].sum()),
        "hourly_rows": len(flow),
        "macro_city_count": int(macro["city_name"].nunique()),
        "macro_row_count": len(macro),
        "macro_latest_date": str(macro["stat_date"].max()),
        "peak_hour": int(flow.groupby("hour_of_day")["avg_flow"].sum().idxmax()),
    }
    print(summary)


if __name__ == "__main__":
    main()
