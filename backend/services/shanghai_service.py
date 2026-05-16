from __future__ import annotations

from typing import Any

from services.data_store import store


def get_hourly_flow(hour: int) -> list[dict[str, Any]]:
    hourly = store.hourly_fact()
    filtered = hourly[hourly["hour_of_day"] == int(hour)].copy()
    return filtered.sort_values("crowd_index", ascending=False).to_dict(orient="records")


def get_line_heat(hour: int) -> list[dict[str, Any]]:
    filtered = store.hourly_fact()
    filtered = filtered[filtered["hour_of_day"] == int(hour)].copy()
    filtered["line_name"] = filtered["line_names"].str.split("|", regex=False)
    exploded = filtered.explode("line_name")
    grouped = (
        exploded.groupby("line_name", as_index=False)[["avg_flow", "crowd_index"]]
        .mean()
        .round(2)
        .sort_values("crowd_index", ascending=False)
    )
    return grouped.to_dict(orient="records")


def get_station_detail(station: str) -> dict[str, Any] | None:
    hourly = store.hourly_fact()
    station_dim = store.station_dim()

    if station.isdigit():
        station_id = int(station)
        station_rows = hourly[hourly["station_id"] == station_id].copy()
        station_meta = station_dim[station_dim["station_id"] == station_id]
    else:
        station_rows = hourly[hourly["station_name"] == station].copy()
        station_meta = station_dim[station_dim["station_name"] == station]

    if station_rows.empty or station_meta.empty:
        return None

    station_rows = station_rows.sort_values("hour_of_day")
    meta = station_meta.iloc[0].to_dict()
    series = station_rows[["hour_of_day", "hour_label", "avg_flow", "crowd_index"]].to_dict(orient="records")
    return {"station": meta, "series": series}
