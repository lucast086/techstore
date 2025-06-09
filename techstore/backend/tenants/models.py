"""
Modelos para la gestión de tenants.

Este módulo define los modelos principales para la arquitectura multitenant:
- Tenant: Representa un inquilino/negocio en el sistema
- Domain: Representa un dominio asociado a un tenant
"""

from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Tenant(TenantMixin):
    """
    Modelo que representa un inquilino en el sistema.

    Un inquilino (tenant) es una instancia separada de la aplicación con sus propios
    datos, usuarios y configuración. Hereda de TenantMixin que proporciona los campos
    y métodos base para la funcionalidad multitenant.
    """

    # Información básica del tenant
    name = models.CharField(
        max_length=100, verbose_name="Nombre", help_text="Nombre comercial del negocio"
    )
    created_on = models.DateField(auto_now_add=True, verbose_name="Fecha de creación")

    # Información de contacto
    email = models.EmailField(verbose_name="Email", help_text="Email de contacto principal")
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Teléfono",
        help_text="Teléfono de contacto",
    )

    # Metadatos y configuración
    is_active = models.BooleanField(
        default=True, verbose_name="Activo", help_text="Indica si el tenant está activo"
    )
    on_trial = models.BooleanField(
        default=True,
        verbose_name="En prueba",
        help_text="Indica si el tenant está en período de prueba",
    )
    trial_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fin de prueba",
        help_text="Fecha en que termina el período de prueba",
    )
    paid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Pagado hasta",
        help_text="Fecha hasta la que el tenant ha pagado",
    )

    # Configuración del schema
    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        """Metadatos del modelo Tenant."""

        verbose_name = "Inquilino"
        verbose_name_plural = "Inquilinos"
        ordering = ["name"]

    def __str__(self):
        """Representación en string del tenant."""
        return self.name


class Domain(DomainMixin):
    """
    Modelo que representa un dominio asociado a un tenant.

    Cada tenant puede tener múltiples dominios que apuntan a él.
    Hereda de DomainMixin que proporciona los campos base para dominios en multitenancy.
    """

    is_primary = models.BooleanField(
        default=False,
        verbose_name="Dominio principal",
        help_text="Indica si este es el dominio principal para el tenant",
    )

    class Meta:
        """Metadatos del modelo Domain."""

        verbose_name = "Dominio"
        verbose_name_plural = "Dominios"
        ordering = ["domain"]

    def __str__(self):
        """Representación en string del dominio."""
        return self.domain
