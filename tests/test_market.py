import json
from unittest.mock import AsyncMock, patch

MARKET_RECORD = {
    "id": "bitcoin",
    "name": "Bitcoin",
    "symbol": "btc",
    "current_price": 50000,
    "market_cap": 1000000000,
    "total_volume": 50000000,
    "price_change_percentage_24h": 2.5,
}

MARKET_RECORD2 = {
    "id": "ethereum",
    "name": "Ethereum",
    "symbol": "eth",
    "current_price": 3000,
    "market_cap": 400000000,
    "total_volume": 20000000,
    "price_change_percentage_24h": 1.2,
}


def test_market_missing_both_params(client, auth_headers):
    r = client.get("/market", headers=auth_headers)
    data = json.loads(r.get_data())
    assert r.status_code == 400
    assert data["error"] == "VALIDATION_ERROR"


def test_market_coin_id(client, auth_headers):
    with patch("app.blueprints.market.CoinGeckoClient") as MockClient, \
         patch("app.blueprints.market.WebhookService") as MockWebhook:
        instance = MockClient.return_value
        instance.get_market_data = AsyncMock(return_value=([MARKET_RECORD], True))
        mock_webhook = MockWebhook.return_value
        mock_webhook.notify_market_fetch = AsyncMock(return_value=None)
        r = client.get("/market?coin_id=bitcoin", headers=auth_headers)
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert len(data["data"]) == 1
        item = data["data"][0]
        assert item["coin_id"] == "bitcoin"
        assert item["name"] == "Bitcoin"
        assert item["symbol"] == "btc"
        assert item["current_price"] == 50000
        assert item["market_cap"] == 1000000000
        assert item["total_volume"] == 50000000
        assert item["price_change_percentage_24h"] == 2.5


def test_market_category(client, auth_headers):
    with patch("app.blueprints.market.CoinGeckoClient") as MockClient, \
         patch("app.blueprints.market.WebhookService") as MockWebhook:
        instance = MockClient.return_value
        instance.get_market_data = AsyncMock(return_value=([MARKET_RECORD, MARKET_RECORD2], True))
        mock_webhook = MockWebhook.return_value
        mock_webhook.notify_market_fetch = AsyncMock(return_value=None)
        r = client.get("/market?category=defi", headers=auth_headers)
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert len(data["data"]) == 2


def test_market_unknown_coin_id(client, auth_headers):
    with patch("app.blueprints.market.CoinGeckoClient") as MockClient, \
         patch("app.blueprints.market.WebhookService") as MockWebhook:
        instance = MockClient.return_value
        instance.get_market_data = AsyncMock(return_value=([], True))
        mock_webhook = MockWebhook.return_value
        mock_webhook.notify_market_fetch = AsyncMock(return_value=None)
        r = client.get("/market?coin_id=unknown", headers=auth_headers)
        data = json.loads(r.get_data())
        assert r.status_code == 404
        assert data["error"] == "NOT_FOUND"


def test_market_no_token(client):
    r = client.get("/market?coin_id=bitcoin")
    assert r.status_code == 401


def test_market_response_fields(client, auth_headers):
    with patch("app.blueprints.market.CoinGeckoClient") as MockClient, \
         patch("app.blueprints.market.WebhookService") as MockWebhook:
        instance = MockClient.return_value
        instance.get_market_data = AsyncMock(return_value=([MARKET_RECORD], True))
        mock_webhook = MockWebhook.return_value
        mock_webhook.notify_market_fetch = AsyncMock(return_value=None)
        r = client.get("/market?coin_id=bitcoin", headers=auth_headers)
        data = json.loads(r.get_data())
        item = data["data"][0]
        expected_fields = {"coin_id", "name", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h"}
        assert expected_fields == set(item.keys())
