"""Models for tenant management.

This module defines the main models for the multitenant architecture:
- Tenant: Represents a tenant/business in the system
- Domain: Represents a domain associated with a tenant
"""

from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Tenant(TenantMixin):
    """Model representing a tenant in the system.

    A tenant is a separate instance of the application with its own
    data, users and configuration. Inherits from TenantMixin which provides
    the base fields and methods for multitenant functionality.
    """

    # Basic tenant information
    name = models.CharField(
        max_length=100,
        verbose_name="Name",
        help_text="Business name",
    )
    created_on = models.DateField(
        auto_now_add=True,
        verbose_name="Creation date",
    )

    # Contact information
    email = models.EmailField(
        verbose_name="Email",
        help_text="Primary contact email",
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Phone",
        help_text="Contact phone number",
    )

    # Metadata and configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indicates if the tenant is active",
    )
    on_trial = models.BooleanField(
        default=True,
        verbose_name="On trial",
        help_text="Indicates if the tenant is in trial period",
    )
    trial_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Trial end date",
        help_text="Date when the trial period ends",
    )
    paid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Paid until",
        help_text="Date until which the tenant has paid",
    )

    # Schema configuration
    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        """Meta options for Tenant model."""

        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ["name"]

    def __str__(self) -> str:
        """Return string representation of tenant."""
        return self.name


class Domain(DomainMixin):
    """Model representing a domain associated with a tenant.

    Each tenant can have multiple domains pointing to it.
    Inherits from DomainMixin which provides the base fields for domains in multitenancy.
    """

    is_primary = models.BooleanField(
        default=False,
        verbose_name="Primary domain",
        help_text="Indicates if this is the primary domain for the tenant",
    )

    class Meta:
        """Meta options for Domain model."""

        verbose_name = "Domain"
        verbose_name_plural = "Domains"
        ordering = ["domain"]

    def __str__(self) -> str:
        """Return string representation of domain."""
        return self.domain
