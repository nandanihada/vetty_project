import asyncio

from flask import Blueprint, current_app, jsonify

from app.extensions import cache_lock
from app.services.coingecko import CoinGeckoClient

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    config = current_app.config["APP_CONFIG"]
    client = CoinGeckoClient(
        client=current_app.extensions["http_client"],
        config=config,
        cache=current_app.extensions["cache"],
        lock=cache_lock,
    )

    try:
        ping_data = asyncio.run(client.ping())
        coingecko_status = {
            "status": "reachable",
            "version": ping_data.get("gecko_says"),
        }
    except Exception:
        coingecko_status = {
            "status": "unreachable",
            "version": None,
        }

    return jsonify({
        "status": "ok",
        "version": config.APP_VERSION,
        "coingecko": coingecko_status,
    }), 200
