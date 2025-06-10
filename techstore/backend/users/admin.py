"""Admin configuration for the users app."""

from django.contrib import admin
from users.models import Permission, Role, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model."""

    list_display = ("username", "email", "first_name", "last_name", "role", "is_active")
    list_filter = ("is_active", "role")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""

    list_display = ("name", "description")
    search_fields = ("name",)
    filter_horizontal = ("permissions",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin interface for Permission model."""

    list_display = ("name", "codename", "description")
    search_fields = ("name", "codename")
    ordering = ("codename",)
