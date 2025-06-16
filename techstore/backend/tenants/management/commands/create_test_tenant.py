"""
Comando para crear un tenant de prueba.

Este comando crea un tenant de prueba con el nombre 'TestStore'.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.models import Domain, Store


class Command(BaseCommand):
    """
    Comando para crear un tenant de prueba.

    Crea un tenant llamado 'TestStore' con su dominio correspondiente.
    Útil para pruebas y desarrollo.
    """

    help = "Crea un tenant de prueba llamado TestStore"

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Ejecuta el comando para crear el tenant de prueba.

        Crea un tenant con schema_name='teststore' y un dominio asociado.
        """
        # Verificar si ya existe el tenant de prueba
        if Store.objects.filter(schema_name="teststore").exists():
            self.stdout.write(
                self.style.WARNING("El tenant TestStore ya existe. No se realizaron cambios.")
            )
            return

        # Crear el tenant de prueba
        test_tenant = Store(
            schema_name="teststore",
            name="TestStore",
            email="test@techstore.com",
            is_active=True,
            on_trial=True,
        )
        test_tenant.save()

        # Crear el dominio para el tenant de prueba
        domain = Domain(
            domain="teststore.localhost",
            tenant=test_tenant,
            is_primary=True,
        )
        domain.save()

        self.stdout.write(
            self.style.SUCCESS(f"Tenant TestStore creado exitosamente con dominio {domain.domain}")
        )
