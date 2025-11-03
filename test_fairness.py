"""Tests for fairness plugin."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_fairness_scores_returns_list() -> None:
    """Ensure the fairness scores endpoint returns a list."""
    response = client.get("/api/v1/fairness/scores")
    assert response.status_code == 200
    assert isinstance(response.json(), list)