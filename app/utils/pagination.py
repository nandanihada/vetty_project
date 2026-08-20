from __future__ import annotations

from flask import Request

from app.errors import ValidationError


def parse_pagination_params(request: Request) -> tuple[int, int]:
    try:
        page_num = int(request.args.get("page_num", 1))
    except (TypeError, ValueError):
        raise ValidationError("'page_num' must be an integer")

    try:
        per_page = int(request.args.get("per_page", 10))
    except (TypeError, ValueError):
        raise ValidationError("'per_page' must be an integer")

    if page_num < 1:
        raise ValidationError("'page_num' must be >= 1")

    if per_page < 1 or per_page > 250:
        raise ValidationError("'per_page' must be between 1 and 250")

    return page_num, per_page


def paginate(items: list, page_num: int, per_page: int) -> dict:
    total = len(items)
    start = (page_num - 1) * per_page
    end = start + per_page
    return {
        "data": items[start:end],
        "pagination": {
            "page_num": page_num,
            "per_page": per_page,
            "total_items": total,
        },
    }
