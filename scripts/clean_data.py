from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

COUNT_FILE = DATA_DIR / "count_df.csv"
CITY_FILE = DATA_DIR / "metro_city_flow.csv"
STATION_FILE = DATA_DIR / "station_info.json"


CITY_META = {
    "上海": {"longitude": 121.4737, "latitude": 31.2304, "line_count": 20, "total_length": 896.0},
    "北京": {"longitude": 116.4074, "latitude": 39.9042, "line_count": 27, "total_length": 879.0},
    "广州": {"longitude": 113.2644, "latitude": 23.1291, "line_count": 16, "total_length": 690.0},
    "深圳": {"longitude": 114.0579, "latitude": 22.5431, "line_count": 16, "total_length": 595.0},
    "成都": {"longitude": 104.0665, "latitude": 30.5728, "line_count": 14, "total_length": 670.0},
    "杭州": {"longitude": 120.1551, "latitude": 30.2741, "line_count": 12, "total_length": 516.0},
    "武汉": {"longitude": 114.3054, "latitude": 30.5931, "line_count": 12, "total_length": 486.0},
    "南京": {"longitude": 118.7969, "latitude": 32.0603, "line_count": 14, "total_length": 530.0},
    "重庆": {"longitude": 106.5516, "latitude": 29.5630, "line_count": 12, "total_length": 561.0},
    "西安": {"longitude": 108.9398, "latitude": 34.3416, "line_count": 10, "total_length": 403.0},
}


@dataclass
class CountColumns:
    station: str
    month: str
    day: str
    hour: str
    slot: str
    value: str


def ensure_output_dir() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def line_short_from_station_info(line_name: str) -> str:
    if "浦江线" in line_name:
        return "浦江线"
    if "磁悬浮" in line_name:
        return "磁悬浮"
    match = re.search(r"(\d+号线)", line_name)
    if match:
        return match.group(1)
    return line_name.split("(")[0].replace("地铁", "").replace("轨道交通", "").strip()


def parse_swipe_station(raw_name: str) -> tuple[str, str]:
    if "浦江线" in raw_name:
        return "浦江线", raw_name.replace("浦江线", "", 1)
    if "磁悬浮" in raw_name:
        return "磁悬浮", raw_name.replace("磁悬浮", "", 1)
    match = re.match(r"^(\d+号线)(.+)$", raw_name)
    if match:
        return match.group(1), match.group(2)
    return "未知", raw_name


def build_station_dimension() -> pd.DataFrame:
    with STATION_FILE.open("r", encoding="utf-8") as fp:
        station_info = json.load(fp)

    rows: list[dict] = []
    for line in station_info["content"]:
        line_short = line_short_from_station_info(line["line_name"])
        for stop in line["stops"]:
            rows.append(
                {
                    "station_name": stop["name"],
                    "line_name": line_short,
                    "plot_x": float(stop["x"]),
                    "plot_y": float(stop["y"]),
                    "longitude": None,
                    "latitude": None,
                }
            )

    station_df = pd.DataFrame(rows)
    station_df = (
        station_df.groupby(["station_name", "line_name"], as_index=False)
        .agg({"plot_x": "mean", "plot_y": "mean", "longitude": "first", "latitude": "first"})
    )

    aggregated = (
        station_df.groupby("station_name", as_index=False)
        .agg(
            {
                "line_name": lambda values: "|".join(sorted(set(values))),
                "plot_x": "mean",
                "plot_y": "mean",
                "longitude": "first",
                "latitude": "first",
            }
        )
        .rename(columns={"line_name": "line_names"})
    )

    aggregated["line_count"] = aggregated["line_names"].str.split("|", regex=False).map(len)
    aggregated["is_transfer"] = (aggregated["line_count"] > 1).astype(int)
    aggregated = aggregated.sort_values("station_name").reset_index(drop=True)
    aggregated["station_id"] = aggregated.index + 1
    return aggregated[
        [
            "station_id",
            "station_name",
            "line_names",
            "line_count",
            "is_transfer",
            "longitude",
            "latitude",
            "plot_x",
            "plot_y",
        ]
    ]


def read_count_source() -> tuple[pd.DataFrame, CountColumns]:
    count_df = pd.read_csv(COUNT_FILE, encoding="gbk")
    cols = CountColumns(*count_df.columns.tolist())
    return count_df, cols


def build_hourly_fact(station_dim: pd.DataFrame) -> pd.DataFrame:
    count_df, cols = read_count_source()
    parsed = count_df[cols.station].map(parse_swipe_station)
    count_df["line_name"] = parsed.map(lambda item: item[0])
    count_df["station_name"] = parsed.map(lambda item: item[1])

    observed_days = (
        count_df[[cols.month, cols.day]]
        .drop_duplicates()
        .rename(columns={cols.month: "month", cols.day: "day"})
    )
    observed_day_count = max(len(observed_days), 1)

    hourly = (
        count_df.groupby(["station_name", cols.hour], as_index=False)[cols.value]
        .sum()
        .rename(columns={cols.hour: "hour_of_day", cols.value: "hourly_flow"})
    )
    hourly["avg_flow"] = (hourly["hourly_flow"] / observed_day_count).round().astype(int)

    all_hours = pd.DataFrame({"hour_of_day": list(range(24))})
    station_hours = station_dim[["station_id", "station_name", "line_names", "is_transfer", "plot_x", "plot_y"]].merge(
        all_hours, how="cross"
    )

    fact = station_hours.merge(hourly[["station_name", "hour_of_day", "avg_flow"]], on=["station_name", "hour_of_day"], how="left")
    fact["avg_flow"] = fact["avg_flow"].fillna(0).astype(int)

    max_flow = max(int(fact["avg_flow"].max()), 1)
    fact["crowd_index"] = (fact["avg_flow"] / max_flow * 100).round().astype(int)
    fact["hour_label"] = fact["hour_of_day"].map(lambda hour: f"{hour:02d}:00")
    fact["line_count"] = fact["line_names"].str.split("|", regex=False).map(len)
    return fact[
        [
            "station_id",
            "station_name",
            "line_names",
            "line_count",
            "is_transfer",
            "hour_of_day",
            "hour_label",
            "avg_flow",
            "crowd_index",
            "plot_x",
            "plot_y",
        ]
    ]


def build_macro_city() -> pd.DataFrame:
    macro = pd.read_csv(CITY_FILE, encoding="utf-8")
    macro = macro.rename(
        columns={
            "城市名称": "city_name",
            "统计日期": "stat_date",
            "日均客流（万人次）": "avg_daily_flow",
        }
    )
    for column in ["longitude", "latitude", "line_count", "total_length"]:
        macro[column] = macro["city_name"].map(lambda city: CITY_META.get(city, {}).get(column))
    return macro


def main() -> None:
    ensure_output_dir()

    station_dim = build_station_dimension()
    hourly_fact = build_hourly_fact(station_dim)
    macro_city = build_macro_city()

    station_dim.to_csv(PROCESSED_DIR / "dim_station.csv", index=False, encoding="utf-8-sig")
    hourly_fact.to_csv(PROCESSED_DIR / "fact_hourly_flow.csv", index=False, encoding="utf-8-sig")
    macro_city.to_csv(PROCESSED_DIR / "macro_city_flow_clean.csv", index=False, encoding="utf-8-sig")

    matched_names = set(hourly_fact.loc[hourly_fact["avg_flow"] > 0, "station_name"])
    all_station_names = set(station_dim["station_name"])
    unmatched = sorted(matched_names - all_station_names)

    print(f"dim_station rows: {len(station_dim)}")
    print(f"fact_hourly_flow rows: {len(hourly_fact)}")
    print(f"macro_city_flow rows: {len(macro_city)}")
    print(f"unmatched flow stations: {len(unmatched)}")
    if unmatched:
        print("sample unmatched:", unmatched[:20])


if __name__ == "__main__":
    main()
