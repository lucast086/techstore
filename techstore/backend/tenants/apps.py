"""
Configuración de la aplicación tenants.

Define la configuración de la aplicación tenants para Django.
"""

from django.apps import AppConfig


class TenantsConfig(AppConfig):
    """
    Configuración de la aplicación tenants.

    Esta clase define la configuración de la aplicación encargada de gestionar
    los inquilinos (tenants) y sus dominios en el sistema multitenant.
    """

    name = "tenants"
    verbose_name = "Gestión de Inquilinos"

    def ready(self):
        """
        Método llamado cuando la aplicación está completamente cargada.

        Se utiliza para registrar señales u otras inicializaciones necesarias.
        """
        # Importar handlers de señales si son necesarios
        # from . import signals
