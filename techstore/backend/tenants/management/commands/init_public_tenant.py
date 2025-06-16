"""
Comando para inicializar el tenant público.

Este comando crea el tenant público necesario para la arquitectura multitenant.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.models import Domain, Store


class Command(BaseCommand):
    """
    Comando para inicializar el tenant público.

    Crea el tenant público y su dominio asociado para la arquitectura multitenant.
    """

    help = "Inicializa el tenant público para la aplicación"

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Ejecuta el comando para crear el tenant público.

        Crea un tenant con schema_name='public' y un dominio asociado.
        """
        # Verificar si ya existe un tenant público
        if Store.objects.filter(schema_name="public").exists():
            self.stdout.write(
                self.style.WARNING("El tenant público ya existe. No se realizaron cambios.")
            )
            return

        # Crear el tenant público
        public_tenant = Store(
            schema_name="public",
            name="TechStore",
            email="techstore.softsolutions@gmail.com",
            is_active=True,
            on_trial=False,
        )
        public_tenant.save()

        # Crear el dominio para el tenant público
        domain = Domain(
            domain="localhost",
            tenant=public_tenant,
            is_primary=True,
        )
        domain.save()

        self.stdout.write(
            self.style.SUCCESS(f"Tenant público creado exitosamente con dominio {domain.domain}")
        )
