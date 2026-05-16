from __future__ import annotations

from flask import Flask

from api.overview import overview_bp
from api.shanghai import shanghai_bp
from config import Config
from utils.response import ok


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(overview_bp)
    app.register_blueprint(shanghai_bp)

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response

    @app.get("/")
    def index():
        return ok(
            {
                "project": "MetroFlow",
                "data_source": Config.DATA_SOURCE,
                "endpoints": [
                    "/api/overview",
                    "/api/overview/cities",
                    "/api/shanghai/flow?hour=8",
                    "/api/shanghai/lines?hour=8",
                    "/api/shanghai/station/人民广场",
                ],
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
