import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

from app.config import Config
from app.services.webhook import WebhookService


def make_service(webhook_url=""):
    cfg = Config()
    cfg.WEBHOOK_URL = webhook_url
    cfg.WEBHOOK_TIMEOUT_SECONDS = 10
    return WebhookService(config=cfg)


def test_webhook_empty_url_logs_warning(caplog):
    svc = make_service(webhook_url="")
    with caplog.at_level(logging.WARNING, logger="app.services.webhook"):
        asyncio.run(svc.notify_market_fetch(coin_id="bitcoin", category=None, record_count=1))
    assert any("WEBHOOK_URL" in record.message for record in caplog.records)


def test_webhook_empty_url_no_http_call():
    svc = make_service(webhook_url="")
    with patch("app.services.webhook.httpx.AsyncClient") as mock_cls:
        asyncio.run(svc.notify_market_fetch(coin_id="bitcoin", category=None, record_count=1))
        mock_cls.assert_not_called()


def test_webhook_successful_post():
    svc = make_service(webhook_url="https://example.com/webhook")
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)
    with patch("app.services.webhook.httpx.AsyncClient", return_value=mock_client):
        asyncio.run(svc.notify_market_fetch(coin_id="bitcoin", category=None, record_count=1))
    mock_client.post.assert_called_once()


def test_webhook_post_returns_500_logs_error(caplog):
    svc = make_service(webhook_url="https://example.com/webhook")
    mock_response = MagicMock()
    mock_response.is_success = False
    mock_response.status_code = 500
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)
    with patch("app.services.webhook.httpx.AsyncClient", return_value=mock_client):
        with caplog.at_level(logging.ERROR, logger="app.services.webhook"):
            asyncio.run(svc.notify_market_fetch(coin_id="bitcoin", category=None, record_count=1))
    assert any("failed" in record.message.lower() or "error" in record.message.lower() for record in caplog.records)


def test_webhook_post_raises_exception_logs_error(caplog):
    svc = make_service(webhook_url="https://example.com/webhook")
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(side_effect=Exception("connection refused"))
    with patch("app.services.webhook.httpx.AsyncClient", return_value=mock_client):
        with caplog.at_level(logging.ERROR, logger="app.services.webhook"):
            asyncio.run(svc.notify_market_fetch(coin_id="bitcoin", category=None, record_count=1))
    assert any("exception" in record.message.lower() or "error" in record.message.lower() for record in caplog.records)


def test_webhook_called_on_cache_miss_via_market_endpoint(client, auth_headers):
    market_record = {
        "id": "bitcoin", "name": "Bitcoin", "symbol": "btc",
        "current_price": 50000, "market_cap": 1000000000,
        "total_volume": 50000000, "price_change_percentage_24h": 2.5,
    }
    with patch("app.blueprints.market.CoinGeckoClient") as MockClient, \
         patch("app.blueprints.market.WebhookService") as MockWebhook:
        instance = MockClient.return_value
        instance.get_market_data = AsyncMock(return_value=([market_record], True))
        mock_webhook_instance = MockWebhook.return_value
        mock_webhook_instance.notify_market_fetch = AsyncMock(return_value=None)
        r = client.get("/market?coin_id=bitcoin", headers=auth_headers)
        assert r.status_code == 200
        mock_webhook_instance.notify_market_fetch.assert_called_once()
