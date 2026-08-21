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
    """
    ---
    tags:
      - Categories
    summary: List all coin categories
    description: Returns a paginated list of all cryptocurrency categories.
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
        description: Paginated list of categories
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  category_id:
                    type: string
                    example: layer-1
                  name:
                    type: string
                    example: Layer 1 (L1)
            pagination:
              type: object
              properties:
                page_num:
                  type: integer
                per_page:
                  type: integer
                total_items:
                  type: integer
      401:
        description: Missing or invalid JWT token
    """
    page_num, per_page = parse_pagination_params(request)

    client = CoinGeckoClient(
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
