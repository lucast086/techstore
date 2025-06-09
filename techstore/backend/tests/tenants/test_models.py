"""Tests for the tenants models."""

import pytest
from django.db import transaction
from django_tenants.test.cases import TenantTestCase
from tenants.models import Domain, Tenant


@pytest.mark.django_db
class TestTenantModel:
    """Test suite for the Tenant model."""

    def test_tenant_creation(self):
        """Test that a tenant can be created."""
        tenant = Tenant(
            schema_name="test",
            name="Test Tenant",
            email="test@example.com",
            is_active=True,
        )
        tenant.save()

        assert Tenant.objects.filter(schema_name="test").exists()
        assert tenant.name == "Test Tenant"
        assert tenant.email == "test@example.com"
        assert tenant.is_active is True

    def test_tenant_str_representation(self):
        """Test the string representation of a tenant."""
        tenant = Tenant(
            schema_name="test",
            name="Test Tenant",
            email="test@example.com",
        )
        tenant.save()

        assert str(tenant) == "Test Tenant"


@pytest.mark.django_db
class TestDomainModel:
    """Test suite for the Domain model."""

    def test_domain_creation(self):
        """Test that a domain can be created and linked to a tenant."""
        tenant = Tenant(
            schema_name="test",
            name="Test Tenant",
            email="test@example.com",
        )
        tenant.save()

        domain = Domain(
            domain="test.localhost",
            tenant=tenant,
            is_primary=True,
        )
        domain.save()

        assert Domain.objects.filter(domain="test.localhost").exists()
        assert domain.tenant.schema_name == "test"
        assert domain.is_primary is True

    def test_domain_str_representation(self):
        """Test the string representation of a domain."""
        tenant = Tenant(
            schema_name="test",
            name="Test Tenant",
            email="test@example.com",
        )
        tenant.save()

        domain = Domain(
            domain="test.localhost",
            tenant=tenant,
        )
        domain.save()

        assert str(domain) == "test.localhost"


class TenantDomainIntegrationTest(TenantTestCase):
    """Integration tests for Tenant and Domain models."""

    @classmethod
    def setUpClass(cls):
        """Set up test tenant and domain."""
        super().setUpClass()

        # This test case automatically creates a tenant and domain
        # via TenantTestCase

    def test_tenant_domain_relationship(self):
        """Test the relationship between tenants and domains."""
        tenant = self.tenant
        domains = tenant.domains.all()

        assert domains.exists()
        assert domains.filter(is_primary=True).exists()

        # Test we can add another domain to this tenant
        with transaction.atomic():
            new_domain = Domain(
                domain="another.localhost",
                tenant=tenant,
                is_primary=False,
            )
            new_domain.save()

        assert tenant.domains.count() == 2
        assert tenant.domains.filter(domain="another.localhost").exists()
