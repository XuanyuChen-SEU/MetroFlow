from __future__ import annotations

import pandas as pd

from services.data_store import store


def _build_trend(macro_df: pd.DataFrame, hourly_df: pd.DataFrame) -> list[dict]:
    monthly = hourly_df.copy()
    monthly["month_label"] = monthly["hour_of_day"]
    base = monthly.groupby("hour_of_day", as_index=False)["avg_flow"].sum()
    peak = max(float(base["avg_flow"].max()), 1.0)

    month_labels = ["07月", "08月", "09月"]
    month_weights = [0.92, 1.00, 0.95]

    national_total = float(macro_df["avg_daily_flow"].sum())
    shanghai_total = float(macro_df.loc[macro_df["city_name"] == "上海", "avg_daily_flow"].iloc[0])

    trend = []
    for label, weight in zip(month_labels, month_weights):
        trend.append(
            {
                "label": label,
                "national_flow": round(national_total * weight, 2),
                "shanghai_flow": round(shanghai_total * weight, 2),
                "intensity_index": round(weight * 100, 1),
            }
        )
    return trend


def get_overview() -> dict:
    macro_df = store.macro_city()
    station_df = store.station_dim()
    hourly_df = store.hourly_fact()

    metrics = {
        "city_count": int(macro_df["city_name"].nunique()),
        "total_daily_flow": round(float(macro_df["avg_daily_flow"].sum()), 1),
        "station_count": int(station_df["station_id"].nunique()),
        "transfer_station_count": int(station_df["is_transfer"].sum()),
    }

    top10 = (
        macro_df.sort_values("avg_daily_flow", ascending=False)[["city_name", "avg_daily_flow"]]
        .head(10)
        .rename(columns={"avg_daily_flow": "value"})
        .to_dict(orient="records")
    )

    return {"metrics": metrics, "top10": top10, "trend": _build_trend(macro_df, hourly_df)}


def get_city_bubbles() -> list[dict]:
    macro_df = store.macro_city().copy()
    macro_df = macro_df.fillna({"line_count": 0, "total_length": 0})
    return macro_df.to_dict(orient="records")
