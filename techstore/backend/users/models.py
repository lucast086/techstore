"""User models for tenant-specific user management."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model for tenant users.

    Extends Django's AbstractUser to add tenant-specific fields.
    Uses Django's built-in Group and Permission models for authorization.
    """

    phone = models.CharField(_("phone number"), max_length=20, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)

    # Role is now handled by Django's built-in groups
    # Each group represents a role (admin, vendedor, tecnico)

    class Meta:
        """Meta options for User model."""

        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        """Return string representation of user."""
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self) -> str:
        """Return the user's full name.

        Returns:
            str: User's full name.
        """
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_role(self):
        """Get the primary role (group) of the user.

        Returns:
            Group: The first group the user belongs to, or None.
        """
        return self.groups.first()

    def has_role(self, role_name):
        """Check if user has a specific role.

        Args:
            role_name: Name of the role to check.

        Returns:
            bool: True if user has the role, False otherwise.
        """
        return self.groups.filter(name=role_name).exists()


class UserAuditLog(models.Model):
    """Model for tracking user actions and changes.

    This model stores a log of all significant user actions for auditing purposes.
    """

    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="audit_logs", verbose_name=_("user")
    )
    action = models.CharField(_("action"), max_length=50, help_text=_("Type of action performed"))
    timestamp = models.DateTimeField(
        _("timestamp"), default=timezone.now, help_text=_("When the action was performed")
    )
    details = models.JSONField(
        _("details"), default=dict, help_text=_("Additional details about the action")
    )
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True,
        help_text=_("IP address from which the action was performed"),
    )
    user_agent = models.TextField(
        _("user agent"), blank=True, help_text=_("Browser/client information")
    )

    class Meta:
        """Meta options for UserAuditLog model."""

        verbose_name = _("user audit log")
        verbose_name_plural = _("user audit logs")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "action"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        """Return string representation of audit log entry."""
        return f"{self.user} - {self.action} - {self.timestamp}"

    @classmethod
    def log_action(cls, user, action, details=None, request=None):
        """Log a user action.

        Args:
            user: The user performing the action
            action: The type of action performed
            details: Additional details about the action
            request: Optional request object to extract IP and user agent

        Returns:
            UserAuditLog: The created audit log entry
        """
        log_data = {
            "user": user,
            "action": action,
            "details": details or {},
        }

        if request:
            log_data.update(
                {
                    "ip_address": cls._get_client_ip(request),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                }
            )

        return cls.objects.create(**log_data)

    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request.

        Args:
            request: The request object

        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
