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
    """
    ---
    tags:
      - Coins
    summary: List all available coins
    description: Returns a paginated list of all cryptocurrency coins.
    security:
      - Bearer: []
    parameters:
      - name: page_num
        in: query
        type: integer
        default: 1
        description: Page number (>= 1)
      - name: per_page
        in: query
        type: integer
        default: 10
        description: Items per page (1-250)
    responses:
      200:
        description: Paginated list of coins
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  coin_id:
                    type: string
                    example: bitcoin
                  name:
                    type: string
                    example: Bitcoin
                  symbol:
                    type: string
                    example: btc
            pagination:
              type: object
              properties:
                page_num:
                  type: integer
                per_page:
                  type: integer
                total_items:
                  type: integer
      400:
        description: Invalid pagination parameters
      401:
        description: Missing or invalid JWT token
    """
    page_num, per_page = parse_pagination_params(request)

    client = CoinGeckoClient(
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
