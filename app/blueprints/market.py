from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.errors import NotFoundError, ValidationError
from app.extensions import cache_lock
from app.services.coingecko import CoinGeckoClient
from app.services.webhook import WebhookService
from app.utils.pagination import paginate, parse_pagination_params

market_bp = Blueprint("market", __name__)


@market_bp.get("/market")
@jwt_required()
def get_market():
    coin_id = request.args.get("coin_id")
    category = request.args.get("category")

    if not coin_id and not category:
        raise ValidationError("At least one of 'coin_id' or 'category' must be provided.")

    page_num, per_page = parse_pagination_params(request)

    config = current_app.config["APP_CONFIG"]
    http_client = current_app.extensions["http_client"]
    cache = current_app.extensions["cache"]

    coingecko = CoinGeckoClient(
        client=http_client,
        config=config,
        cache=cache,
        lock=cache_lock,
    )

    coin_ids = [coin_id] if coin_id else None

    raw, cache_miss = asyncio.run(
        coingecko.get_market_data(coin_ids, category, page_num, per_page)
    )

    if cache_miss:
        webhook = WebhookService(client=http_client, config=config)

        async def _fire():
            await webhook.notify_market_fetch(
                coin_id=coin_id,
                category=category,
                record_count=len(raw),
            )

        asyncio.run(_fire())

    if coin_id and not raw:
        raise NotFoundError(f"No market data found for coin_id '{coin_id}'.")

    records = [
        {
            "coin_id": item["id"],
            "name": item["name"],
            "symbol": item["symbol"],
            "current_price": item.get("current_price"),
            "market_cap": item.get("market_cap"),
            "total_volume": item.get("total_volume"),
            "price_change_percentage_24h": item.get("price_change_percentage_24h"),
        }
        for item in raw
    ]

    return jsonify(paginate(records, page_num, per_page)), 200
