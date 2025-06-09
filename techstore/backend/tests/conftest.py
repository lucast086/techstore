"""Pytest configuration file with common fixtures."""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.test.client import TenantClient
from tenants.models import Domain, Tenant


@pytest.fixture(scope="function")
def tenant_test():
    """Create a test tenant for testing."""
    tenant = Tenant(
        schema_name="test",
        name="Test Tenant",
        email="test@example.com",
        is_active=True,
    )
    tenant.save()

    domain = Domain(
        domain="test.localhost",
        tenant=tenant,
        is_primary=True,
    )
    domain.save()

    yield tenant

    # Cleanup
    try:
        # Close any open connections to the tenant schema
        connection.close()
        # Delete domain first
        Domain.objects.filter(tenant=tenant).delete()
        # Force delete the tenant schema
        tenant.delete(force_drop=True)
    except Exception as e:
        print(f"Error during tenant cleanup: {e}")
        # If force delete failed, try to manually drop the schema
        try:
            cursor = connection.cursor()
            cursor.execute(f'DROP SCHEMA IF EXISTS "{tenant.schema_name}" CASCADE')
        except Exception as e2:
            print(f"Error during manual schema drop: {e2}")


@pytest.fixture(scope="function")
def tenant_client(tenant_test):
    """Return a client that automatically sets the tenant."""
    return TenantClient(tenant_test)


@pytest.fixture(scope="function")
def admin_user(tenant_client):
    """Create an admin user for testing."""
    User = get_user_model()
    admin = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpassword",
    )
    return admin


@pytest.fixture(scope="function")
def authenticated_client(tenant_client, admin_user):
    """Return an authenticated client."""
    tenant_client.login(username="admin", password="adminpassword")
    return tenant_client
