import json
from unittest.mock import AsyncMock, patch


def test_login_valid(client):
    r = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    data = json.loads(r.get_data())
    assert r.status_code == 200
    assert "access_token" in data


def test_login_wrong_password(client):
    r = client.post("/auth/login", json={"username": "testuser", "password": "wrong"})
    data = json.loads(r.get_data())
    assert r.status_code == 401
    assert data["error"] == "UNAUTHORIZED"


def test_login_missing_username(client):
    r = client.post("/auth/login", json={"password": "testpass"})
    data = json.loads(r.get_data())
    assert r.status_code == 400
    assert data["error"] == "VALIDATION_ERROR"


def test_login_empty_body(client):
    r = client.post("/auth/login", json={})
    assert r.status_code == 400


def test_protected_route_without_token(client):
    with patch("app.blueprints.coins.CoinGeckoClient") as MockClient:
        instance = MockClient.return_value
        instance.get_coins_list = AsyncMock(return_value=[])
        r = client.get("/coins")
        assert r.status_code == 401


def test_protected_route_invalid_token(client):
    r = client.get("/coins", headers={"Authorization": "Bearer invalid.token.here"})
    assert r.status_code == 401
