"""GPU API tests."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_gpus() -> None:
    """Ensure the list GPUs endpoint returns a list (possibly empty)."""
    response = client.get("/api/v1/gpus/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

