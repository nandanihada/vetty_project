from __future__ import annotations

import hashlib
import json
import logging
import threading
from typing import Any

import httpx
from cachetools import TTLCache

from app.config import Config
from app.errors import GatewayTimeoutError, UpstreamError

logger = logging.getLogger(__name__)


class CoinGeckoClient:
    def __init__(
        self,
        config: Config,
        cache: TTLCache,
        lock: threading.Lock,
    ) -> None:
        self._base_url = config.COINGECKO_BASE_URL
        self._timeout = config.COINGECKO_TIMEOUT_SECONDS
        self._cache = cache
        self._lock = lock

    def _cache_key(self, endpoint: str, **params: Any) -> str:
        serialised = json.dumps(params, sort_keys=True)
        digest = hashlib.sha256(f"{endpoint}:{serialised}".encode()).hexdigest()[:16]
        return f"{endpoint}:{digest}"

    def _get_cached(self, key: str) -> Any | None:
        with self._lock:
            return self._cache.get(key)

    def _set_cached(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = value

    async def _get(self, path: str, **params: Any) -> Any:
        url = f"{self._base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, params=params)
            if not response.is_success:
                raise UpstreamError(
                    f"CoinGecko returned {response.status_code} for {path}"
                )
            return response.json()
        except httpx.TimeoutException as exc:
            raise GatewayTimeoutError(f"CoinGecko timed out: {path}") from exc
        except httpx.RequestError as exc:
            raise UpstreamError(f"CoinGecko request failed: {exc}") from exc

    async def ping(self) -> dict:
        return await self._get("/ping")

    async def get_coins_list(self) -> list[dict]:
        key = self._cache_key("coins_list")
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        data = await self._get("/coins/list")
        self._set_cached(key, data)
        return data

    async def get_categories_list(self) -> list[dict]:
        key = self._cache_key("categories_list")
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        data = await self._get("/coins/categories/list")
        self._set_cached(key, data)
        return data

    async def get_market_data(
        self,
        coin_ids: list[str] | None,
        category: str | None,
        page: int,
        per_page: int,
    ) -> tuple[list[dict], bool]:
        params: dict[str, Any] = {
            "vs_currency": "cad",
            "page": page,
            "per_page": per_page,
        }
        if coin_ids:
            params["ids"] = ",".join(coin_ids)
        if category:
            params["category"] = category

        key = self._cache_key("market_data", **params)
        cached = self._get_cached(key)
        if cached is not None:
            return cached, False

        data = await self._get("/coins/markets", **params)
        self._set_cached(key, data)
        return data, True
