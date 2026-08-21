from __future__ import annotations

from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask

from app.config import Config
from app.extensions import jwt, make_cache
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

    from flasgger import Swagger
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Vetty Crypto Market API",
            "description": "REST API for cryptocurrency market data powered by CoinGecko.",
            "version": "1.0.0",
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Bearer token. Format: Bearer <token>",
            }
        },
        "security": [{"Bearer": []}],
    }
    Swagger(app, template=swagger_template)

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

    from app.middleware import register_middleware
    register_middleware(app)

    return app
