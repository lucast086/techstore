"""
Configuración del admin para los modelos de stores.

Este módulo registra y personaliza la interfaz de administración de Django
para los modelos Store y Domain.
"""

from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import Domain, Store


@admin.register(Store)
class StoreAdmin(TenantAdminMixin, admin.ModelAdmin):
    """
    Admin para el modelo Store.

    Extiende TenantAdminMixin para proporcionar funcionalidad adicional
    específica para la administración de stores.
    """

    list_display = ("name", "schema_name", "created_on", "is_active", "on_trial")
    list_filter = ("is_active", "on_trial")
    search_fields = ("name", "schema_name", "email")
    readonly_fields = ("created_on",)
    fieldsets = (
        ("Información Básica", {"fields": ("name", "schema_name", "created_on")}),
        ("Contacto", {"fields": ("email", "phone")}),
        ("Estado", {"fields": ("is_active", "on_trial", "trial_end_date", "paid_until")}),
    )


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Admin para el modelo Domain."""

    list_display = ("domain", "tenant", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("domain",)
    raw_id_fields = ("tenant",)
    list_select_related = ("tenant",)
