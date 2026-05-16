from __future__ import annotations

import pandas as pd

from services.data_store import store


def _normalize_macro_df(macro_df: pd.DataFrame) -> pd.DataFrame:
    normalized = macro_df.copy()
    normalized["stat_date"] = pd.to_datetime(normalized["stat_date"])
    return normalized


def _latest_snapshot(macro_df: pd.DataFrame) -> pd.DataFrame:
    ordered = macro_df.sort_values(["city_name", "stat_date"])
    return ordered.groupby("city_name", as_index=False).tail(1).reset_index(drop=True)


def _build_trend(macro_df: pd.DataFrame) -> list[dict]:
    national = (
        macro_df.groupby("stat_date", as_index=False)["avg_daily_flow"]
        .sum()
        .rename(columns={"avg_daily_flow": "national_flow"})
    )
    shanghai = (
        macro_df.loc[macro_df["city_name"] == "上海", ["stat_date", "avg_daily_flow"]]
        .rename(columns={"avg_daily_flow": "shanghai_flow"})
    )
    trend = national.merge(shanghai, on="stat_date", how="left").sort_values("stat_date")
    trend["label"] = trend["stat_date"].dt.strftime("%m-%d")
    trend["intensity_index"] = (trend["national_flow"] / max(float(trend["national_flow"].max()), 1.0) * 100).round(1)
    trend["shanghai_flow"] = trend["shanghai_flow"].fillna(0)
    return trend[["label", "national_flow", "shanghai_flow", "intensity_index"]].round(2).to_dict(orient="records")


def get_overview() -> dict:
    macro_df = _normalize_macro_df(store.macro_city())
    station_df = store.station_dim()
    latest = _latest_snapshot(macro_df)
    latest_date = latest["stat_date"].max()
    peak_city = latest.sort_values("avg_daily_flow", ascending=False).iloc[0]

    metrics = {
        "city_count": int(latest["city_name"].nunique()),
        "latest_stat_date": latest_date.strftime("%Y-%m-%d"),
        "tracked_days": int(macro_df["stat_date"].nunique()),
        "total_daily_flow": round(float(latest["avg_daily_flow"].sum()), 1),
        "station_count": int(station_df["station_id"].nunique()),
        "transfer_station_count": int(station_df["is_transfer"].sum()),
    }

    top10 = (
        latest.sort_values("avg_daily_flow", ascending=False)[["city_name", "avg_daily_flow"]]
        .head(10)
        .rename(columns={"avg_daily_flow": "value"})
        .to_dict(orient="records")
    )

    meta = {
        "source": latest["source"].dropna().iloc[0] if "source" in latest and latest["source"].notna().any() else None,
        "scraped_at_epoch": int(latest["scraped_at_epoch"].dropna().iloc[0]) if "scraped_at_epoch" in latest and latest["scraped_at_epoch"].notna().any() else None,
        "peak_city": {"city_name": peak_city["city_name"], "value": round(float(peak_city["avg_daily_flow"]), 2)},
    }

    return {"metrics": metrics, "top10": top10, "trend": _build_trend(macro_df), "meta": meta}


def get_city_bubbles() -> list[dict]:
    macro_df = _normalize_macro_df(store.macro_city())
    latest = _latest_snapshot(macro_df)
    latest["stat_date"] = latest["stat_date"].dt.strftime("%Y-%m-%d")
    return latest.to_dict(orient="records")
