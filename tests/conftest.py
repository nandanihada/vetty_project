import json
import os
import pytest

os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["API_USERNAME"] = "testuser"
os.environ["API_PASSWORD"] = "testpass"
os.environ["WEBHOOK_URL"] = ""

from app import create_app


@pytest.fixture()
def app():
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    r = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = json.loads(r.get_data())["access_token"]
    return {"Authorization": "Bearer " + token}
