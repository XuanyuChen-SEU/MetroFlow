from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

COUNT_FILE = DATA_DIR / "count_df.csv"
CITY_FILE = DATA_DIR / "metro_global.json"
STATION_FILE = DATA_DIR / "station_info.json"

TOPOLOGY_COLORS = {
    "1号线": "#E3002B",
    "2号线": "#86B81C",
    "3号线": "#F7A600",
    "4号线": "#5A2D81",
    "5号线": "#B61E2E",
    "6号线": "#D0970A",
    "7号线": "#F3D03E",
    "8号线": "#008C95",
    "9号线": "#8E4D2D",
    "10号线": "#C6AFD4",
    "11号线": "#871C2A",
    "12号线": "#007A60",
    "13号线": "#E895C1",
    "16号线": "#98D1C0",
    "17号线": "#B88A5A",
    "浦江线": "#B5B5B6",
    "磁悬浮": "#0099D8",
}


CITY_COORDS = {
    "北京": {"longitude": 116.4074, "latitude": 39.9042},
    "上海": {"longitude": 121.4737, "latitude": 31.2304},
    "广州": {"longitude": 113.2644, "latitude": 23.1291},
    "深圳": {"longitude": 114.0579, "latitude": 22.5431},
    "成都": {"longitude": 104.0665, "latitude": 30.5728},
    "武汉": {"longitude": 114.3054, "latitude": 30.5931},
    "重庆": {"longitude": 106.5516, "latitude": 29.5630},
    "西安": {"longitude": 108.9398, "latitude": 34.3416},
    "杭州": {"longitude": 120.1551, "latitude": 30.2741},
    "南京": {"longitude": 118.7969, "latitude": 32.0603},
    "天津": {"longitude": 117.2000, "latitude": 39.1333},
    "郑州": {"longitude": 113.6254, "latitude": 34.7466},
    "长沙": {"longitude": 112.9388, "latitude": 28.2282},
    "沈阳": {"longitude": 123.4315, "latitude": 41.8057},
    "苏州": {"longitude": 120.5853, "latitude": 31.2989},
    "南宁": {"longitude": 108.3200, "latitude": 22.8240},
    "长春": {"longitude": 125.3235, "latitude": 43.8171},
    "太原": {"longitude": 112.5492, "latitude": 37.8570},
    "青岛": {"longitude": 120.3826, "latitude": 36.0671},
    "大连": {"longitude": 121.6147, "latitude": 38.9140},
    "呼和浩特": {"longitude": 111.7492, "latitude": 40.8426},
    "常州": {"longitude": 119.9741, "latitude": 31.8107},
    "昆明": {"longitude": 102.8329, "latitude": 24.8801},
    "东莞": {"longitude": 113.7518, "latitude": 23.0207},
    "贵阳": {"longitude": 106.6302, "latitude": 26.6470},
    "南昌": {"longitude": 115.8582, "latitude": 28.6820},
    "无锡": {"longitude": 120.3124, "latitude": 31.4900},
    "合肥": {"longitude": 117.2272, "latitude": 31.8206},
    "哈尔滨": {"longitude": 126.6425, "latitude": 45.7560},
    "石家庄": {"longitude": 114.5149, "latitude": 38.0428},
    "厦门": {"longitude": 118.0894, "latitude": 24.4798},
    "兰州": {"longitude": 103.8343, "latitude": 36.0611},
    "芜湖": {"longitude": 118.4329, "latitude": 31.3525},
    "佛山": {"longitude": 113.1214, "latitude": 23.0215},
    "绍兴": {"longitude": 120.5821, "latitude": 29.9971},
    "南通": {"longitude": 120.8943, "latitude": 31.9802},
}


@dataclass
class CountColumns:
    station: str
    month: str
    day: str
    hour: str
    slot: str
    flow: str


def ensure_output_dir() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def line_sort_key(line_name: str) -> tuple[int, int | str]:
    if line_name == "磁悬浮":
        return (1, "磁悬浮")
    if line_name == "浦江线":
        return (1, "浦江线")
    match = re.match(r"^(\d+)号线$", line_name)
    if match:
        return (0, int(match.group(1)))
    return (2, line_name)


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
                    "raw_line_name": line["line_name"],
                    "line_name": line_short,
                    "plot_x": float(stop["x"]),
                    "plot_y": float(stop["y"]),
                    "longitude": None,
                    "latitude": None,
                }
            )

    station_df = pd.DataFrame(rows)
    station_df = (
        station_df.groupby(["station_name", "line_name", "raw_line_name"], as_index=False)
        .agg({"plot_x": "mean", "plot_y": "mean", "longitude": "first", "latitude": "first"})
    )

    aggregated = (
        station_df.groupby("station_name", as_index=False)
        .agg(
            {
                "raw_line_name": lambda values: "|".join(sorted(set(values))),
                "line_name": lambda values: "|".join(sorted(set(values), key=line_sort_key)),
                "plot_x": "mean",
                "plot_y": "mean",
                "longitude": "first",
                "latitude": "first",
            }
        )
        .rename(columns={"raw_line_name": "line_variants", "line_name": "line_names"})
    )

    aggregated["line_count"] = aggregated["line_names"].str.split("|", regex=False).map(len)
    aggregated["line_variant_count"] = aggregated["line_variants"].str.split("|", regex=False).map(len)
    aggregated["topology_record_count"] = station_df.groupby("station_name").size().reindex(aggregated["station_name"]).to_numpy()
    aggregated["is_transfer"] = (aggregated["line_count"] > 1).astype(int)
    aggregated = aggregated.sort_values("station_name").reset_index(drop=True)
    aggregated["station_id"] = aggregated.index + 1
    return aggregated[
        [
            "station_id",
            "station_name",
            "line_names",
            "line_count",
            "line_variants",
            "line_variant_count",
            "topology_record_count",
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
        count_df.groupby(["station_name", cols.hour], as_index=False)[cols.flow]
        .sum()
        .rename(columns={cols.hour: "hour_of_day", cols.flow: "hourly_flow"})
    )
    hourly["avg_flow"] = (hourly["hourly_flow"] / observed_day_count).round().astype(int)

    all_hours = pd.DataFrame({"hour_of_day": list(range(24))})
    station_hours = station_dim[
        [
            "station_id",
            "station_name",
            "line_names",
            "line_count",
            "line_variants",
            "line_variant_count",
            "topology_record_count",
            "is_transfer",
            "plot_x",
            "plot_y",
        ]
    ].merge(all_hours, how="cross")

    fact = station_hours.merge(hourly[["station_name", "hour_of_day", "avg_flow"]], on=["station_name", "hour_of_day"], how="left")
    fact["avg_flow"] = fact["avg_flow"].fillna(0).astype(int)

    max_flow = max(int(fact["avg_flow"].max()), 1)
    fact["crowd_index"] = (fact["avg_flow"] / max_flow * 100).round().astype(int)
    fact["hour_label"] = fact["hour_of_day"].map(lambda hour: f"{hour:02d}:00")
    return fact[
        [
            "station_id",
            "station_name",
            "line_names",
            "line_count",
            "line_variants",
            "line_variant_count",
            "topology_record_count",
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
    with CITY_FILE.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)

    rows: list[dict] = []
    for city in payload["cities"]:
        city_meta = CITY_COORDS.get(city["city"], {})
        for day in city["recent_15_days"]:
            rows.append(
                {
                    "city_slug": city["slug"],
                    "city_name": city["city"],
                    "stat_date": day["date"],
                    "avg_daily_flow": float(day["ridership_10k"]),
                    "latest_update": city["latest_update"],
                    "is_latest": int(day["date"] == city["latest_update"]),
                    "longitude": city_meta.get("longitude"),
                    "latitude": city_meta.get("latitude"),
                    "source": payload.get("source"),
                    "scraped_at_epoch": payload.get("scraped_at_epoch"),
                }
            )

    macro = pd.DataFrame(rows)
    macro["stat_date"] = pd.to_datetime(macro["stat_date"])
    macro["latest_update"] = pd.to_datetime(macro["latest_update"])
    macro["days_from_latest"] = (macro["latest_update"] - macro["stat_date"]).dt.days
    macro = macro.sort_values(["stat_date", "city_name"]).reset_index(drop=True)
    macro["stat_date"] = macro["stat_date"].dt.strftime("%Y-%m-%d")
    macro["latest_update"] = macro["latest_update"].dt.strftime("%Y-%m-%d")
    return macro[
        [
            "city_slug",
            "city_name",
            "stat_date",
            "avg_daily_flow",
            "latest_update",
            "is_latest",
            "days_from_latest",
            "longitude",
            "latitude",
            "source",
            "scraped_at_epoch",
        ]
    ]


def build_line_topology() -> dict:
    with STATION_FILE.open("r", encoding="utf-8") as fp:
        station_info = json.load(fp)

    seen_paths: set[tuple[str, tuple[str, ...]]] = set()
    paths: list[dict] = []
    min_x = float("inf")
    max_x = float("-inf")
    min_y = float("inf")
    max_y = float("-inf")

    for line in station_info["content"]:
        short_name = line_short_from_station_info(line["line_name"])
        points = [[float(stop["x"]), float(stop["y"])] for stop in line["stops"]]
        station_names = tuple(stop["name"] for stop in line["stops"])
        canonical_names = min(station_names, tuple(reversed(station_names)))
        dedupe_key = (short_name, canonical_names)
        if dedupe_key in seen_paths:
            continue
        seen_paths.add(dedupe_key)

        for x, y in points:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        paths.append(
            {
                "line_name": short_name,
                "variant_name": line["line_name"],
                "color": TOPOLOGY_COLORS.get(short_name, "#0081ff"),
                "points": points,
                "station_count": len(points),
            }
        )

    paths.sort(key=lambda item: (line_sort_key(item["line_name"]), item["variant_name"]))
    return {
        "lines": paths,
        "extent": {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
        },
    }


def main() -> None:
    ensure_output_dir()

    station_dim = build_station_dimension()
    hourly_fact = build_hourly_fact(station_dim)
    macro_city = build_macro_city()
    line_topology = build_line_topology()

    station_dim.to_csv(PROCESSED_DIR / "dim_station.csv", index=False, encoding="utf-8-sig")
    hourly_fact.to_csv(PROCESSED_DIR / "fact_hourly_flow.csv", index=False, encoding="utf-8-sig")
    macro_city.to_csv(PROCESSED_DIR / "macro_city_flow_clean.csv", index=False, encoding="utf-8-sig")
    (PROCESSED_DIR / "shanghai_line_topology.json").write_text(
        json.dumps(line_topology, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

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
