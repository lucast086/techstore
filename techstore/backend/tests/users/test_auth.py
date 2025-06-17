"""Tests for authentication endpoints."""

from django.urls import reverse
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient
from django_tenants.utils import schema_context
from rest_framework import status
from tenants.models import Domain, Store


class LoginEndpointTest(TenantTestCase):
    """Test the login endpoint."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for the login endpoint tests."""
        cls.tenant = Store.objects.create(
            schema_name="test",
            name="Test Tenant",
            email="test@example.com",
            is_active=True,
        )
        cls.domain = Domain.objects.create(
            domain="test.localhost",
            tenant=cls.tenant,
            is_primary=True,
        )

    def setUp(self):
        """Set up test client for each test."""
        self.client = TenantClient(self.tenant)

    def test_login_url_exists(self):
        """Test that login URL is properly configured."""
        url = reverse("users:login")
        self.assertEqual(url, "/api/v1/users/login/")

    def test_login_get_not_allowed(self):
        """Test that GET is not allowed on login endpoint."""
        response = self.client.get(reverse("users:login"), HTTP_HOST=self.domain.domain)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_login_post_without_data(self):
        """Test that POST without data returns 400 Bad Request."""
        url = reverse("users:login")
        response = self.client.post(url, {}, format="json", HTTP_HOST=self.domain.domain)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)

    def test_login_post_with_invalid_credentials(self):
        """Test that login with invalid credentials returns 401 Unauthorized."""
        url = reverse("users:login")
        data = {"username": "invalid", "password": "invalid"}
        response = self.client.post(url, data, format="json", HTTP_HOST=self.domain.domain)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_post_with_valid_credentials(self):
        """Test that login with valid credentials returns 200 OK and user data."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="testuser", password="testpass123")  # noqa: F841
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(
            reverse("users:login"),
            data,
            content_type="application/json",
            HTTP_HOST=self.domain.domain,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)

    def test_login_post_with_user_from_different_tenant(self):
        """Test that users cannot login to a different tenant."""
        from django.contrib.auth import get_user_model
        from django_tenants.test.client import TenantClient
        from tenants.models import Domain, Store

        User = get_user_model()

        # Create a user in the current tenant
        user = User.objects.create_user(username="testuser", password="testpass123")

        # Create a new tenant and domain in the public schema
        with schema_context("public"):
            other_tenant = Store.objects.create(
                name="Other Store",
                schema_name="other_store",
                paid_until="2024-12-31",
                on_trial=False,
            )
            other_domain = Domain.objects.create(
                domain="other-store.localhost", tenant=other_tenant, is_primary=True
            )

        # Create a client for the other tenant
        other_client = TenantClient(other_tenant)

        # Try to login in the other tenant
        data = {"username": "testuser", "password": "testpass123"}
        response = other_client.post(
            reverse("users:login"),
            data,
            content_type="application/json",
            HTTP_HOST=other_domain.domain,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid credentials")

    def test_logout_success(self):
        """Un usuario autenticado puede cerrar sesión exitosamente."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Crear y autenticar usuario
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_login(user)

        # Intentar logout
        response = self.client.post(
            reverse("users:logout"), content_type="application/json", HTTP_HOST=self.domain.domain
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Successfully logged out")

    def test_logout_requires_authentication(self):
        """Un usuario no autenticado no puede cerrar sesión."""
        response = self.client.post(
            reverse("users:logout"), content_type="application/json", HTTP_HOST=self.domain.domain
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
