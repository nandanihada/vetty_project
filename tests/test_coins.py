import json
from unittest.mock import AsyncMock, patch

FAKE_COINS = [{"id": f"coin{i}", "name": f"Coin {i}", "symbol": f"c{i}"} for i in range(15)]


def test_coins_default_pagination(client, auth_headers):
    with patch("app.blueprints.coins.CoinGeckoClient") as MockClient:
        instance = MockClient.return_value
        instance.get_coins_list = AsyncMock(return_value=FAKE_COINS)
        r = client.get("/coins", headers=auth_headers)
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert len(data["data"]) == 10
        assert data["pagination"]["total_items"] == 15


def test_coins_custom_per_page(client, auth_headers):
    with patch("app.blueprints.coins.CoinGeckoClient") as MockClient:
        instance = MockClient.return_value
        instance.get_coins_list = AsyncMock(return_value=FAKE_COINS)
        r = client.get("/coins?per_page=5", headers=auth_headers)
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert len(data["data"]) == 5


def test_coins_page2(client, auth_headers):
    with patch("app.blueprints.coins.CoinGeckoClient") as MockClient:
        instance = MockClient.return_value
        instance.get_coins_list = AsyncMock(return_value=FAKE_COINS)
        r = client.get("/coins?page_num=2&per_page=10", headers=auth_headers)
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert len(data["data"]) == 5


def test_coins_invalid_per_page_zero(client, auth_headers):
    r = client.get("/coins?per_page=0", headers=auth_headers)
    data = json.loads(r.get_data())
    assert r.status_code == 400
    assert data["error"] == "VALIDATION_ERROR"


def test_coins_invalid_per_page_too_large(client, auth_headers):
    r = client.get("/coins?per_page=300", headers=auth_headers)
    data = json.loads(r.get_data())
    assert r.status_code == 400
    assert data["error"] == "VALIDATION_ERROR"


def test_coins_invalid_page_num_zero(client, auth_headers):
    r = client.get("/coins?page_num=0", headers=auth_headers)
    data = json.loads(r.get_data())
    assert r.status_code == 400
    assert data["error"] == "VALIDATION_ERROR"


def test_coins_no_token(client):
    r = client.get("/coins")
    assert r.status_code == 401
