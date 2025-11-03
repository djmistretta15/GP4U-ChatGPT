"""Tests for detailed analytics plugin."""

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_top_gpus_returns_list() -> None:
    response = client.get("/api/v1/analytics/detailed/top-gpus")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_top_users_returns_list() -> None:
    response = client.get("/api/v1/analytics/detailed/top-users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)