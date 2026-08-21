import json
from unittest.mock import AsyncMock, patch

FAKE_CATEGORIES = [{"category_id": f"cat{i}", "name": f"Category {i}"} for i in range(12)]


def test_categories_default_pagination(client, auth_headers):
    with patch("app.blueprints.categories.CoinGeckoClient") as MockClient:
        instance = MockClient.return_value
        instance.get_categories_list = AsyncMock(return_value=FAKE_CATEGORIES)
        r = client.get("/categories", headers=auth_headers)
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert len(data["data"]) == 10
        assert data["pagination"]["total_items"] == 12


def test_categories_custom_per_page(client, auth_headers):
    with patch("app.blueprints.categories.CoinGeckoClient") as MockClient:
        instance = MockClient.return_value
        instance.get_categories_list = AsyncMock(return_value=FAKE_CATEGORIES)
        r = client.get("/categories?per_page=5", headers=auth_headers)
        data = json.loads(r.get_data())
        assert r.status_code == 200
        assert len(data["data"]) == 5


def test_categories_no_token(client):
    r = client.get("/categories")
    assert r.status_code == 401


def test_categories_invalid_per_page(client, auth_headers):
    r = client.get("/categories?per_page=0", headers=auth_headers)
    data = json.loads(r.get_data())
    assert r.status_code == 400
    assert data["error"] == "VALIDATION_ERROR"
