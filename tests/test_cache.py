import asyncio
import threading

from cachetools import TTLCache
from unittest.mock import AsyncMock, patch

from app.config import Config
from app.services.coingecko import CoinGeckoClient


def make_client(cache=None):
    cfg = Config()
    if cache is None:
        cache = TTLCache(maxsize=100, ttl=60)
    return CoinGeckoClient(config=cfg, cache=cache, lock=threading.Lock())


def test_cache_miss_calls_get(app):
    with app.app_context():
        client = make_client()
        fake_data = [{"id": "bitcoin", "name": "Bitcoin", "symbol": "btc"}]
        with patch.object(client, "_get", new=AsyncMock(return_value=fake_data)) as mock_get:
            result = asyncio.run(client.get_coins_list())
            assert mock_get.call_count == 1
            assert result == fake_data


def test_cache_hit_skips_get(app):
    with app.app_context():
        cache = TTLCache(maxsize=100, ttl=60)
        client = make_client(cache=cache)
        fake_data = [{"id": "bitcoin", "name": "Bitcoin", "symbol": "btc"}]
        key = client._cache_key("coins_list")
        cache[key] = fake_data
        with patch.object(client, "_get", new=AsyncMock(return_value=[])) as mock_get:
            result = asyncio.run(client.get_coins_list())
            assert mock_get.call_count == 0
            assert result == fake_data


def test_second_call_hits_cache(app):
    with app.app_context():
        client = make_client()
        fake_data = [{"id": "ethereum", "name": "Ethereum", "symbol": "eth"}]
        with patch.object(client, "_get", new=AsyncMock(return_value=fake_data)) as mock_get:
            asyncio.run(client.get_coins_list())
            asyncio.run(client.get_coins_list())
            assert mock_get.call_count == 1


def test_market_data_cache_miss(app):
    with app.app_context():
        client = make_client()
        fake_data = [{"id": "bitcoin"}]
        with patch.object(client, "_get", new=AsyncMock(return_value=fake_data)):
            data, cache_miss = asyncio.run(client.get_market_data(["bitcoin"], None, 1, 10))
            assert cache_miss is True
            assert data == fake_data


def test_market_data_cache_hit(app):
    with app.app_context():
        cache = TTLCache(maxsize=100, ttl=60)
        client = make_client(cache=cache)
        fake_data = [{"id": "bitcoin"}]
        params = {"vs_currency": "cad", "page": 1, "per_page": 10, "ids": "bitcoin"}
        key = client._cache_key("market_data", **params)
        cache[key] = fake_data
        with patch.object(client, "_get", new=AsyncMock(return_value=[])) as mock_get:
            data, cache_miss = asyncio.run(client.get_market_data(["bitcoin"], None, 1, 10))
            assert cache_miss is False
            assert mock_get.call_count == 0
            assert data == fake_data
