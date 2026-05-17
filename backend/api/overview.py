from __future__ import annotations

from flask import Blueprint, request

from services.overview_service import get_city_bubbles, get_overview, get_city_trend
from utils.response import ok


overview_bp = Blueprint("overview", __name__, url_prefix="/api/overview")


@overview_bp.get("")
def overview():
    return ok(get_overview())


@overview_bp.get("/cities")
def cities():
    return ok(get_city_bubbles())

@overview_bp.get("/trend")
def city_trend():
    city = request.args.get("city", "上海")
    return ok(get_city_trend(city))