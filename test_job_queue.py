"""Tests for the job queue plugin."""

from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_list_jobs_returns_list() -> None:
    response = client.get("/api/v1/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_nonexistent_job() -> None:
    response = client.get("/api/v1/jobs/9999")
    assert response.status_code == 404