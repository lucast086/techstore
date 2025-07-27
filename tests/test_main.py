"""Test main application endpoints."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "TechStore API is running"}


def test_welcome_page(client: TestClient):
    """Test welcome page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert "TechStore" in response.text
