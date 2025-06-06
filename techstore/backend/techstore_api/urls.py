"""URL configuration for techstore_api project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

# API Routers
router = DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    # API URLs
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    # Servir archivos estáticos
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# En desarrollo, permite servir Angular desde Django
if settings.DEBUG:
    # Esta configuración es para cuando usamos el enfoque híbrido
    # y queremos que Django sirva la aplicación Angular en producción
    urlpatterns += [
        # Captura todas las rutas no manejadas y las envía a Angular
        re_path(
            r"^(?!api/|admin/|static/|media/).*$", TemplateView.as_view(template_name="index.html")
        ),
    ]
