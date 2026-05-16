from __future__ import annotations

from flask import jsonify


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "message": message, "data": data})


def fail(message="error", code=1, status=400):
    return jsonify({"code": code, "message": message, "data": None}), status
