import asyncio

from flask import Blueprint, current_app, jsonify

from app.extensions import cache_lock
from app.services.coingecko import CoinGeckoClient

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """
    ---
    tags:
      - Health
    summary: Application health check
    description: Returns application status, version, and CoinGecko reachability.
    responses:
      200:
        description: Health status
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            version:
              type: string
              example: 1.0.0
            coingecko:
              type: object
              properties:
                status:
                  type: string
                  example: reachable
                version:
                  type: string
                  example: 4.0.1
    """
    config = current_app.config["APP_CONFIG"]
    client = CoinGeckoClient(
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
