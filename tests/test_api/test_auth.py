"""Tests for authentication API endpoints."""

from datetime import timedelta

import pytest
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.models.user import User
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_user(async_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("TestPass123!"),
        full_name="Test User",
        role="technician",
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(async_session: AsyncSession) -> User:
    """Create an admin test user."""
    user = User(
        email="admin@example.com",
        password_hash=get_password_hash("AdminPass123!"),
        full_name="Admin User",
        role="admin",
        is_active=True,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(async_session: AsyncSession) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        password_hash=get_password_hash("InactivePass123!"),
        full_name="Inactive User",
        role="technician",
        is_active=False,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


class TestLogin:
    """Test login endpoint."""

    async def test_login_success(self, async_client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await async_client.post(
            "/api/v1/auth/login", json={"email": "test@example.com", "password": "TestPass123!"}
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

    async def test_login_invalid_password(self, async_client: AsyncClient, test_user: User):
        """Test login with invalid password."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "WrongPassword123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent user."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "Password123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    async def test_login_inactive_user(self, async_client: AsyncClient, inactive_user: User):
        """Test login with inactive user."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "InactivePass123!"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    async def test_login_rate_limiting(self, async_client: AsyncClient):
        """Test login rate limiting."""
        # Make 6 failed login attempts (limit is 5)
        for i in range(6):
            response = await async_client.post(
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

    async def test_refresh_token_success(self, async_client: AsyncClient, test_user: User):
        """Test successful token refresh."""
        # Create refresh token
        refresh_token = create_refresh_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
        )

        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """Test refresh with invalid token."""
        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid-token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate refresh token"

    async def test_refresh_token_wrong_type(self, async_client: AsyncClient, test_user: User):
        """Test refresh with access token instead of refresh token."""
        # Create access token (wrong type)
        access_token = create_access_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
        )

        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": access_token}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCurrentUser:
    """Test get current user endpoint."""

    async def test_get_current_user_success(self, async_client: AsyncClient, test_user: User):
        """Test getting current user info."""
        # Create access token
        access_token = create_access_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
        )

        response = await async_client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["role"] == test_user.role
        assert data["is_active"] is True

    async def test_get_current_user_no_token(self, async_client: AsyncClient):
        """Test getting current user without token."""
        response = await async_client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    async def test_get_current_user_invalid_token(self, async_client: AsyncClient):
        """Test getting current user with invalid token."""
        response = await async_client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate credentials"

    async def test_get_current_user_expired_token(self, async_client: AsyncClient, test_user: User):
        """Test getting current user with expired token."""
        # Create expired token
        expired_token = create_access_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role},
            expires_delta=timedelta(seconds=-1),
        )

        response = await async_client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """Test logout endpoint."""

    async def test_logout_success(self, async_client: AsyncClient, test_user: User):
        """Test successful logout."""
        # Create access token
        access_token = create_access_token(
            {"sub": str(test_user.id), "email": test_user.email, "role": test_user.role}
        )

        response = await async_client.post(
            "/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Successfully logged out"

        # Check cookies are cleared
        assert response.cookies.get("access_token") is None
        assert response.cookies.get("refresh_token") is None


class TestRoleBasedAccess:
    """Test role-based access control."""

    async def test_admin_only_endpoint(
        self, async_client: AsyncClient, admin_user: User, test_user: User
    ):
        """Test that admin-only endpoints work correctly."""
        # This is a placeholder - in real implementation, you'd test actual admin endpoints
        pass

    async def test_require_role_unauthorized(self, async_client: AsyncClient, test_user: User):
        """Test access denied for insufficient role."""
        # This is a placeholder - in real implementation, you'd test actual role-protected endpoints
        pass
