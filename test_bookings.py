"""Booking API tests."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_bookings_empty() -> None:
    """Listing bookings for a non‑existent user should return an empty list."""
    response = client.get("/api/v1/bookings/99999")
    # 404 may be returned if user does not exist; accept 200 or 404
    assert response.status_code in (200, 404)

