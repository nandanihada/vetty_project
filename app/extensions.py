from __future__ import annotations

import threading

from cachetools import TTLCache
from flask_jwt_extended import JWTManager

from app.config import Config

jwt = JWTManager()
cache_lock = threading.Lock()


def make_cache(config: Config) -> TTLCache:
    return TTLCache(maxsize=1024, ttl=config.CACHE_TTL_SECONDS)
