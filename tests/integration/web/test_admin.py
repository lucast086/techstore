"""Tests for admin panel functionality."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAdminPanel:
    """Test cases for admin panel access and functionality."""

    def test_admin_access_denied_without_auth(self, client: TestClient):
        """Test that admin panel requires authentication."""
        response = client.get("/admin")
        assert response.status_code == 401

    def test_admin_access_denied_for_non_admin(
        self, client: TestClient, normal_user_token_headers: dict
    ):
        """Test that non-admin users cannot access admin panel."""
        response = client.get("/admin", headers=normal_user_token_headers)
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_admin_dashboard_access(
        self, client: TestClient, admin_user_token_headers: dict
    ):
        """Test that admin users can access the dashboard."""
        response = client.get("/admin", headers=admin_user_token_headers)
        assert response.status_code == 200
        assert "Dashboard Overview" in response.text
        assert "TechStore Admin" in response.text

    def test_admin_navigation_links(
        self, client: TestClient, admin_user_token_headers: dict
    ):
        """Test that all navigation links are present."""
        response = client.get("/admin", headers=admin_user_token_headers)
        assert response.status_code == 200

        # Check for navigation items
        assert "Dashboard" in response.text
        assert "User Management" in response.text
        assert "System Settings" in response.text
        assert "Activity Logs" in response.text
        assert "Return to Main App" in response.text

    def test_admin_breadcrumbs(
        self, client: TestClient, admin_user_token_headers: dict
    ):
        """Test that breadcrumbs are displayed correctly."""
        response = client.get("/admin", headers=admin_user_token_headers)
        assert response.status_code == 200
        assert "Admin" in response.text
        assert "Dashboard" in response.text

    def test_admin_user_stats(
        self, client: TestClient, admin_user_token_headers: dict, db: Session
    ):
        """Test that user statistics are displayed correctly."""
        response = client.get("/admin", headers=admin_user_token_headers)
        assert response.status_code == 200

        # Check for stats cards
        assert "Total Users" in response.text
        assert "Active Users" in response.text
        assert "Admin Users" in response.text
        assert "System Status" in response.text

    def test_admin_htmx_navigation(
        self, client: TestClient, admin_user_token_headers: dict
    ):
        """Test HTMX partial loading for navigation."""
        # Test dashboard partial
        response = client.get("/admin/dashboard", headers=admin_user_token_headers)
        assert response.status_code == 200
        assert "Dashboard Overview" in response.text

        # Test users partial
        response = client.get("/admin/users/list", headers=admin_user_token_headers)
        assert response.status_code == 200
        assert "User Management" in response.text

        # Test settings partial
        response = client.get(
            "/admin/settings/content", headers=admin_user_token_headers
        )
        assert response.status_code == 200
        assert "System Settings" in response.text

        # Test logs partial
        response = client.get("/admin/logs/content", headers=admin_user_token_headers)
        assert response.status_code == 200
        assert "Activity Logs" in response.text

    def test_admin_responsive_classes(
        self, client: TestClient, admin_user_token_headers: dict
    ):
        """Test that responsive classes are present."""
        response = client.get("/admin", headers=admin_user_token_headers)
        assert response.status_code == 200

        # Check for responsive grid classes
        assert "md:grid-cols-2" in response.text
        assert "lg:grid-cols-4" in response.text

    def test_admin_session_timeout_elements(
        self, client: TestClient, admin_user_token_headers: dict
    ):
        """Test that session timeout elements are present."""
        response = client.get("/admin", headers=admin_user_token_headers)
        assert response.status_code == 200

        # Check for session timeout modal
        assert "session-timeout-modal" in response.text
        assert "Session Timeout Warning" in response.text
        assert "Continue Session" in response.text

    def test_admin_loading_indicator(
        self, client: TestClient, admin_user_token_headers: dict
    ):
        """Test that loading indicator is present."""
        response = client.get("/admin", headers=admin_user_token_headers)
        assert response.status_code == 200

        # Check for loading indicator
        assert "loading-indicator" in response.text
        assert "htmx-indicator" in response.text

    def test_admin_quick_actions(
        self, client: TestClient, admin_user_token_headers: dict
    ):
        """Test that quick actions are displayed."""
        response = client.get("/admin", headers=admin_user_token_headers)
        assert response.status_code == 200

        # Check for quick actions
        assert "Quick Actions" in response.text
        assert "Add New User" in response.text
        assert "System Configuration" in response.text
        assert "View System Logs" in response.text

    def test_admin_all_routes_protected(self, client: TestClient):
        """Test that all admin routes require authentication."""
        admin_routes = [
            "/admin",
            "/admin/dashboard",
            "/admin/users",
            "/admin/users/list",
            "/admin/settings",
            "/admin/settings/content",
            "/admin/logs",
            "/admin/logs/content",
        ]

        for route in admin_routes:
            response = client.get(route)
            assert response.status_code == 401, f"Route {route} is not protected"

    def test_admin_all_routes_require_admin_role(
        self, client: TestClient, normal_user_token_headers: dict
    ):
        """Test that all admin routes require admin role."""
        admin_routes = [
            "/admin",
            "/admin/dashboard",
            "/admin/users",
            "/admin/users/list",
            "/admin/settings",
            "/admin/settings/content",
            "/admin/logs",
            "/admin/logs/content",
        ]

        for route in admin_routes:
            response = client.get(route, headers=normal_user_token_headers)
            assert response.status_code == 403, f"Route {route} allows non-admin access"
