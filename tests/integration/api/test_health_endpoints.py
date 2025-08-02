"""
Tests for health check endpoints
Following TDD - these tests should fail initially
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check API endpoints"""

    def test_basic_health_endpoint(self, client: TestClient):
        """Test basic health check endpoint"""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "TechStore API"
        assert "version" in data

    def test_database_health_endpoint(self, client: TestClient):
        """Test database health check endpoint"""
        response = client.get("/api/v1/health/db")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "postgres_version" in data
        assert "pool_size" in data
        assert "database_name" in data

    def test_database_health_endpoint_when_db_down(self, client: TestClient):
        """Test database health check when database is down"""
        from app.database import get_db
        from app.main import app

        # Create a mock database session that raises an exception
        def get_db_error():
            mock_session = MagicMock()
            mock_session.execute.side_effect = Exception("Database connection failed")
            yield mock_session

        # Override the dependency
        app.dependency_overrides[get_db] = get_db_error

        try:
            response = client.get("/api/v1/health/db")

            assert (
                response.status_code == 200
            )  # Still returns 200 but with unhealthy status
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
            assert "error" in data
        finally:
            # Reset the override
            app.dependency_overrides.clear()

    def test_readiness_endpoint(self, client: TestClient):
        """Test readiness check endpoint for k8s/docker"""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data
        assert data["checks"]["database"] == "passed"

    def test_readiness_endpoint_when_not_ready(self, client: TestClient):
        """Test readiness check when database is not ready"""
        with patch("app.api.v1.health.check_db_connection") as mock_check:
            mock_check.return_value = False

            response = client.get("/api/v1/health/ready")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_ready"
            assert data["checks"]["database"] == "failed"
