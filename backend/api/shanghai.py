from __future__ import annotations

from flask import Blueprint, request

from services.shanghai_service import get_hourly_flow, get_line_heat, get_load_trend, get_station_detail, get_topology
from utils.response import fail, ok


shanghai_bp = Blueprint("shanghai", __name__, url_prefix="/api/shanghai")


@shanghai_bp.get("/flow")
def flow():
    hour = request.args.get("hour", default=8, type=int)
    return ok(get_hourly_flow(hour))


@shanghai_bp.get("/topology")
def topology():
    return ok(get_topology())


@shanghai_bp.get("/lines")
def lines():
    hour = request.args.get("hour", default=8, type=int)
    return ok(get_line_heat(hour))


@shanghai_bp.get("/load-trend")
def load_trend():
    line = request.args.get("line", default="all", type=str)
    return ok(get_load_trend(line))


@shanghai_bp.get("/station/<station>")
def station_detail(station: str):
    payload = get_station_detail(station)
    if payload is None:
        return fail("station not found", status=404)
    return ok(payload)
