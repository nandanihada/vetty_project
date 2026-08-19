from __future__ import annotations

from datetime import timedelta

import httpx
from dotenv import load_dotenv
from flask import Flask

from app.config import Config
from app.extensions import cache_lock, jwt, make_cache
from app.logging_config import setup_logging


def create_app(config: Config | None = None) -> Flask:
    load_dotenv()
    cfg = config or Config()
    cfg.validate()

    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = cfg.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=cfg.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)

    setup_logging(cfg)

    cache = make_cache(cfg)
    jwt.init_app(app)

    app.config["APP_CONFIG"] = cfg
    app.extensions["cache"] = cache

    from app.blueprints.health import health_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.coins import coins_bp
    from app.blueprints.categories import categories_bp
    from app.blueprints.market import market_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(coins_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(market_bp)

    from app.errors import register_error_handlers

    register_error_handlers(app)

    client = httpx.AsyncClient(timeout=cfg.COINGECKO_TIMEOUT_SECONDS)
    app.extensions["http_client"] = client

    @app.teardown_appcontext
    def close_http_client(exc: BaseException | None) -> None:
        import asyncio

        c = app.extensions.get("http_client")
        if c:
            asyncio.run(c.aclose())

    return app
