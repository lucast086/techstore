"""URL configuration for tenant schemas."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

# API Routers para tenants
router = DefaultRouter()


# API root view para verificar estado del tenant
@api_view(["GET"])
def tenant_api_root(request):
    """Endpoint principal para verificar estado de la API en el tenant actual."""
    tenant = request.tenant
    return Response(
        {
            "status": "online",
            "message": f"API funcionando correctamente en tenant: {tenant.name}",
            "tenant_schema": tenant.schema_name,
            "version": "0.1.0",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    # API URLs
    path("api/", tenant_api_root),  # Endpoint para verificar estado
    path("api/v1/", include(router.urls)),
    path(
        "api/v1/users/", include("users.urls", namespace="users")
    ),  # Incluir URLs de usuarios con namespace
    path("api-auth/", include("rest_framework.urls")),
    # Servir archivos estáticos
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]

# En desarrollo, servir archivos estáticos directamente
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Servir la aplicación Angular para cualquier otra ruta
urlpatterns += [
    # Captura todas las rutas no manejadas y las envía a Angular
    re_path(
        r"^(?!api/|admin/|static/|media/).*$", TemplateView.as_view(template_name="index.html")
    ),
]
