"""Authentication tests for the GP4U API."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_login_invalid_credentials() -> None:
    """Ensure login with invalid credentials returns HTTP 400."""
    response = client.post("/api/v1/auth/login", params={"email": "unknown@example.com", "password": "invalid"})
    assert response.status_code == 400

