"""Tests for warranty API endpoints."""


import pytest
from app.models.repair import Repair
from app.models.warranty import Warranty
from app.schemas.repair import RepairStatus
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestWarrantyAPI:
    """Test cases for warranty API endpoints."""

    def test_create_warranty(
        self,
        client: TestClient,
        db_session: Session,
        test_repair: Repair,
        test_user,
        auth_headers,
    ) -> None:
        """Test creating warranty via API."""
        # Set repair as delivered
        test_repair.status = RepairStatus.DELIVERED.value
        db_session.commit()

        response = client.post(
            "/api/v1/warranties/",
            json={
                "repair_id": test_repair.id,
                "parts_warranty_days": 90,
                "labor_warranty_days": 30,
                "coverage_type": "full",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["repair_id"] == test_repair.id
        assert data["data"]["warranty_number"].startswith("WRN-")

    def test_create_warranty_unauthorized(
        self,
        client: TestClient,
        test_repair: Repair,
    ) -> None:
        """Test creating warranty without authentication."""
        response = client.post(
            "/api/v1/warranties/",
            json={"repair_id": test_repair.id},
        )

        assert response.status_code == 401

    def test_check_warranty(
        self,
        client: TestClient,
        db_session: Session,
        test_warranty: Warranty,
    ) -> None:
        """Test checking warranty status."""
        response = client.get(
            "/api/v1/warranties/check",
            params={"warranty_number": test_warranty.warranty_number},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["found"] is True
        assert len(data["data"]["warranties"]) == 1

    def test_check_warranty_no_params(
        self,
        client: TestClient,
    ) -> None:
        """Test checking warranty without parameters."""
        response = client.get("/api/v1/warranties/check")

        assert response.status_code == 400
        assert "at least one search parameter" in response.json()["detail"].lower()

    def test_search_warranties(
        self,
        client: TestClient,
        db_session: Session,
        test_warranty: Warranty,
        auth_headers,
    ) -> None:
        """Test searching warranties."""
        response = client.get(
            "/api/v1/warranties/",
            params={"q": test_warranty.warranty_number},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert data["meta"]["total"] >= 1

    def test_get_warranty_details(
        self,
        client: TestClient,
        db_session: Session,
        test_warranty: Warranty,
        auth_headers,
    ) -> None:
        """Test getting warranty details."""
        response = client.get(
            f"/api/v1/warranties/{test_warranty.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_warranty.id
        assert data["data"]["warranty_number"] == test_warranty.warranty_number

    def test_get_warranty_not_found(
        self,
        client: TestClient,
        auth_headers,
    ) -> None:
        """Test getting non-existent warranty."""
        response = client.get(
            "/api/v1/warranties/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_void_warranty(
        self,
        client: TestClient,
        db_session: Session,
        test_warranty: Warranty,
        auth_headers,
    ) -> None:
        """Test voiding a warranty."""
        response = client.put(
            f"/api/v1/warranties/{test_warranty.id}/void",
            json={"void_reason": "Customer damaged device"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "voided"
        assert data["data"]["void_reason"] == "Customer damaged device"

    def test_create_warranty_claim(
        self,
        client: TestClient,
        db_session: Session,
        test_warranty: Warranty,
        auth_headers,
    ) -> None:
        """Test creating a warranty claim."""
        response = client.post(
            "/api/v1/warranties/claims",
            json={
                "warranty_id": test_warranty.id,
                "issue_description": "Device not charging",
                "parts_covered": True,
                "labor_covered": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["warranty_id"] == test_warranty.id
        assert data["data"]["issue_description"] == "Device not charging"

    def test_get_warranty_statistics(
        self,
        client: TestClient,
        db_session: Session,
        test_warranty: Warranty,
        auth_headers,
    ) -> None:
        """Test getting warranty statistics."""
        response = client.get(
            "/api/v1/warranties/statistics",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_warranties"] >= 1
        assert "claim_rate" in data["data"]

    def test_update_expired_warranties_admin_only(
        self,
        client: TestClient,
        auth_headers,
        test_user,
    ) -> None:
        """Test updating expired warranties (admin only)."""
        # Make user non-admin
        test_user.is_superuser = False

        response = client.post(
            "/api/v1/warranties/update-expired",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "permissions" in response.json()["detail"].lower()

    def test_update_expired_warranties_as_admin(
        self,
        client: TestClient,
        db_session: Session,
        auth_headers,
        test_user,
    ) -> None:
        """Test updating expired warranties as admin."""
        # Make user admin
        test_user.is_superuser = True
        db_session.commit()

        response = client.post(
            "/api/v1/warranties/update-expired",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "updated" in data["data"]


@pytest.fixture
def auth_headers(client: TestClient, test_user) -> dict:
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "test_password",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
