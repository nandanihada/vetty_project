import json
from unittest.mock import AsyncMock, patch


def test_health_coingecko_reachable(client):
    with patch("app.blueprints.health.CoinGeckoClient") as MockClient:
        instance = MockClient.return_value
        instance.ping = AsyncMock(return_value={"gecko_says": "To the Moon!"})
        r = client.get("/health")
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert data["status"] == "ok"
        assert data["coingecko"]["status"] == "reachable"


def test_health_coingecko_unreachable(client):
    with patch("app.blueprints.health.CoinGeckoClient") as MockClient:
        instance = MockClient.return_value
        instance.ping = AsyncMock(side_effect=Exception("timeout"))
        r = client.get("/health")
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert data["status"] == "ok"
        assert data["coingecko"]["status"] == "unreachable"
