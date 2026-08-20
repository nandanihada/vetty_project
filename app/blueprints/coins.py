from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import cache_lock
from app.services.coingecko import CoinGeckoClient
from app.utils.pagination import paginate, parse_pagination_params

coins_bp = Blueprint("coins", __name__)


@coins_bp.get("/coins")
@jwt_required()
def get_coins():
    page_num, per_page = parse_pagination_params(request)

    client = CoinGeckoClient(
        client=current_app.extensions["http_client"],
        config=current_app.config["APP_CONFIG"],
        cache=current_app.extensions["cache"],
        lock=cache_lock,
    )

    raw = asyncio.run(client.get_coins_list())
    coins = [
        {"coin_id": c["id"], "name": c["name"], "symbol": c["symbol"]}
        for c in raw
    ]

    return jsonify(paginate(coins, page_num, per_page)), 200
