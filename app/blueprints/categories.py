from __future__ import annotations

import asyncio

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import cache_lock
from app.services.coingecko import CoinGeckoClient
from app.utils.pagination import paginate, parse_pagination_params

categories_bp = Blueprint("categories", __name__)


@categories_bp.get("/categories")
@jwt_required()
def get_categories():
    page_num, per_page = parse_pagination_params(request)

    client = CoinGeckoClient(
        client=current_app.extensions["http_client"],
        config=current_app.config["APP_CONFIG"],
        cache=current_app.extensions["cache"],
        lock=cache_lock,
    )

    raw = asyncio.run(client.get_categories_list())
    categories = [
        {"category_id": c["category_id"], "name": c["name"]}
        for c in raw
    ]

    return jsonify(paginate(categories, page_num, per_page)), 200
