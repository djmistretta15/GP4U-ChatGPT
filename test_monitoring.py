"""Tests for monitoring plugin."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_monitoring_metrics() -> None:
    """Ensure monitoring metrics endpoint returns expected keys."""
    response = client.get("/api/v1/monitoring/metrics")
    assert response.status_code == 200
    data = response.json()
    for key in ["total_gpus", "total_bookings", "average_booking_hours", "total_revenue"]:
        assert key in data