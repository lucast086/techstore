"""User models for tenant-specific user management."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    """Permission model for tenant-specific permissions.

    These are different from Django's built-in permissions.
    """

    name = models.CharField(_("name"), max_length=255)
    codename = models.CharField(_("codename"), max_length=100, unique=True)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        """Meta options for Permission model."""

        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
        ordering = ["codename"]

    def __str__(self) -> str:
        """Return string representation of permission."""
        return self.name


class Role(models.Model):
    """Role model for tenant users.

    Each role has a set of permissions.
    """

    name = models.CharField(_("name"), max_length=100)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
    )
    description = models.TextField(_("description"), blank=True)

    class Meta:
        """Meta options for Role model."""

        verbose_name = _("role")
        verbose_name_plural = _("roles")
        ordering = ["name"]

    def __str__(self) -> str:
        """Return string representation of role."""
        return self.name


class User(AbstractUser):
    """Custom user model for tenant users.

    Extends Django's AbstractUser to add tenant-specific fields.
    """

    role = models.ForeignKey(
        Role,
        verbose_name=_("role"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    phone = models.CharField(_("phone number"), max_length=20, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    last_login = models.DateTimeField(_("last login"), auto_now=True)

    class Meta:
        """Meta options for User model."""

        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        """Return string representation of user."""
        return f"{self.get_full_name()} ({self.email})"

    def has_tenant_permission(self, permission_codename: str) -> bool:
        """Check if user has a specific permission through their role.

        Args:
            permission_codename: The codename of the permission to check.

        Returns:
            bool: True if user has the permission, False otherwise.
        """
        if not self.role:
            return False
        return self.role.permissions.filter(codename=permission_codename).exists()

    def get_tenant_permissions(self):
        """Get all permissions for the user through their role.

        Returns:
            QuerySet: QuerySet of Permission objects.
        """
        if not self.role:
            return Permission.objects.none()
        return self.role.permissions.all()

    def get_full_name(self) -> str:
        """Return the user's full name.

        Returns:
            str: User's full name.
        """
        return f"{self.first_name} {self.last_name}".strip()
