"""URL configuration for techstore_api project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

# API Routers
router = DefaultRouter()


# API root view para verificar estado
@api_view(["GET"])
def api_root(request):
    """Endpoint principal para verificar estado de la API."""
    return Response(
        {"status": "online", "message": "API funcionando correctamente", "version": "0.1.0"}
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    # API URLs
    path("api/", api_root),  # Endpoint para verificar estado
    path("api/v1/", include(router.urls)),
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
