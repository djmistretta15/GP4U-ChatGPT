"""Tests for bidding plugin endpoints."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_bids_for_nonexistent_order() -> None:
    """Listing bids for a non‑existing order should return an empty list."""
    response = client.get("/api/v1/bidding/orders/9999/bids")
    assert response.status_code == 200
    assert response.json() == []


def test_accept_highest_no_bids() -> None:
    """Accepting a highest bid when no bids exist should return 404."""
    response = client.post("/api/v1/bidding/orders/9999/accept-highest")
    assert response.status_code == 404