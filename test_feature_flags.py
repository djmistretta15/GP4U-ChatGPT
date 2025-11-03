"""Tests for the feature flags API plugin."""

from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_list_feature_flags() -> None:
    """Ensure that listing feature flags returns expected keys."""
    response = client.get("/api/v1/feature-flags/")
    assert response.status_code == 200
    data = response.json()
    # Verify that default flags are present
    assert isinstance(data, dict)
    assert "pricing_engine" in data
    assert "marketplace" in data


def test_get_specific_feature_flag() -> None:
    """Ensure that querying a specific flag returns a boolean status."""
    response = client.get("/api/v1/feature-flags/pricing_engine")
    assert response.status_code == 200
    data = response.json()
    assert data["feature"] == "pricing_engine"
    assert isinstance(data["enabled"], bool)