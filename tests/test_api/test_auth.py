"""Tests for authentication API endpoints."""

from datetime import timedelta

import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.models.user import User
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def auth_test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("TestPass123!"),
        full_name="Test User",
        role="technician",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create an admin test user."""
    user = User(
        email="admin@example.com",
        password_hash=get_password_hash("AdminPass123!"),
        full_name="Admin User",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session: Session) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        password_hash=get_password_hash("InactivePass123!"),
        full_name="Inactive User",
        role="technician",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestLogin:
    """Test login endpoint."""

    def test_login_success(self, client: TestClient, auth_test_user: User):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "TestPass123!"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 8 * 3600

        # Check cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with invalid password."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "WrongPassword123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "Password123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_inactive_user(self, client: TestClient, inactive_user: User):
        """Test login with inactive user."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "InactivePass123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_rate_limiting(self, client: TestClient):
        """Test login rate limiting."""
        # Make 6 failed login attempts (limit is 5)
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "WrongPassword"},
            )

            if i < 5:
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
            else:
                assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                assert "Too many login attempts" in response.json()["detail"]


class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_refresh_token_success(self, client: TestClient, test_user: User):
        """Test successful token refresh."""
        # Create refresh token
        refresh_token = create_refresh_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
        )

        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid-token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate refresh token"

    def test_refresh_token_wrong_type(self, client: TestClient, test_user: User):
        """Test refresh with access token instead of refresh token."""
        # Create access token (wrong type)
        access_token = create_access_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
        )

        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": access_token}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCurrentUser:
    """Test get current user endpoint."""

    def test_get_current_user_success(self, client: TestClient, test_user: User):
        """Test getting current user info."""
        # Create access token
        access_token = create_access_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
        )

        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["role"] == test_user.role
        assert data["is_active"] is True

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate credentials"

    def test_get_current_user_expired_token(self, client: TestClient, test_user: User):
        """Test getting current user with expired token."""
        # Create expired token
        expired_token = create_access_token(
            {
                "sub": str(test_user.id),
                "email": test_user.email,
                "role": test_user.role,
            },
            expires_delta=timedelta(seconds=-1),
        )

        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """Test logout endpoint."""

    def test_logout_success(self, client: TestClient, test_user: User):
        """Test successful logout."""
        # Create access token
        access_token = create_access_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
        )

        response = client.post(
            "/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully logged out"

        # Check cookies are cleared
        assert response.cookies.get("access_token") is None
        assert response.cookies.get("refresh_token") is None


class TestRoleBasedAccess:
    """Test role-based access control."""

    def test_admin_only_endpoint(
        self, client: TestClient, admin_user: User, test_user: User
    ):
        """Test that admin-only endpoints work correctly."""
        # This is a placeholder - in real implementation, you'd test actual admin endpoints
        pass

    def test_require_role_unauthorized(self, client: TestClient, test_user: User):
        """Test access denied for insufficient role."""
        # This is a placeholder - in real implementation, you'd test actual role-protected endpoints
        pass
