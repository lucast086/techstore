"""Admin configuration for the users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from users.models import User, UserAuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""

    # Customize the fieldsets to include our custom fields
    fieldsets = BaseUserAdmin.fieldsets + ((_("Additional Info"), {"fields": ("phone",)}),)

    # Customize list display
    list_display = ("username", "email", "first_name", "last_name", "get_role_display", "is_active")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)

    def get_role_display(self, obj):
        """Display the user's primary role (first group)."""
        role = obj.get_role()
        return role.name if role else "-"

    get_role_display.short_description = _("Role")


@admin.register(UserAuditLog)
class UserAuditLogAdmin(admin.ModelAdmin):
    """Admin interface for UserAuditLog model."""

    list_display = ("user", "action", "timestamp", "ip_address")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "user__email", "action", "ip_address")
    readonly_fields = ("user", "action", "timestamp", "details", "ip_address", "user_agent")
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent modification of audit logs."""
        return False


# Customize the Group admin to make it more user-friendly
admin.site.unregister(Group)


@admin.register(Group)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Group model (used as roles)."""

    list_display = ("name", "get_user_count")
    search_fields = ("name",)
    filter_horizontal = ("permissions",)

    def get_user_count(self, obj):
        """Get the number of users in this role."""
        return obj.user_set.count()

    get_user_count.short_description = _("Users")

    class Meta:
        """Meta configuration for the Group model."""

        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
