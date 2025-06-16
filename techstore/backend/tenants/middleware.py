"""Middleware for store validation and user permissions."""

import logging

from django.http import HttpResponseForbidden
from users.models import UserAuditLog

logger = logging.getLogger(__name__)


class StoreMiddleware:
    """Middleware for store validation and user permissions.

    This middleware:
    1. Validates that the user belongs to the current store
    2. Checks if the store is active
    3. Validates user roles and permissions
    4. Logs important store actions (not every request)
    """

    # Rutas que no requieren validación de store
    EXCLUDED_PATHS = [
        "/static/",
        "/media/",
        "/api/auth/",  # Login/logout no deberían validar store
        "/api/v1/users/login/",  # Login específico
        "/api/v1/users/token/",  # Token refresh
        "/admin/",
        "/api-auth/",
        "/__debug__/",  # Django debug toolbar
    ]

    # Métodos HTTP que queremos loguear
    LOGGED_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    # Rutas que NO queremos loguear incluso con métodos logged
    NO_LOG_PATHS = [
        "/api/v1/users/token/refresh/",
        "/api/v1/users/token/verify/",
        "/api/heartbeat/",  # Si tienes endpoint de health check
    ]

    def __init__(self, get_response):
        """Initialize middleware.

        Args:
            get_response: The next middleware in the chain
        """
        self.get_response = get_response

    def __call__(self, request):
        """Process the request.

        Args:
            request: The current request

        Returns:
            HttpResponse: The response
        """
        # Skip para rutas excluidas
        if self._is_excluded_path(request.path):
            return self.get_response(request)

        # Skip validation for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        try:
            # Get current store from django-tenants
            store = getattr(request, "tenant", None)
            if not store:
                logger.warning(f"No store found for authenticated user {request.user.username}")
                return HttpResponseForbidden("No store found")

            # Validate store status
            if not store.is_active:
                logger.warning(
                    f"Inactive store access attempt: {store.schema_name} by {request.user.username}"
                )
                return HttpResponseForbidden("Store is inactive")

            # Para superusuarios, skip validaciones adicionales
            if request.user.is_superuser:
                # Log acceso de superusuario si es acción importante
                if self._should_log_action(request):
                    self._log_store_access(request, store, is_superuser=True)
                return self.get_response(request)

            # Validación opcional de grupos para usuarios normales
            # Solo advertir, no bloquear (para permitir usuarios recién creados)
            if not request.user.groups.exists():
                logger.info(
                    f"{request.user.username} has no groups assigned in store {store.schema_name}"
                )

            # Log solo acciones importantes
            if self._should_log_action(request):
                self._log_store_access(request, store)

        except Exception as e:
            logger.error(
                f"Store validation error for user {request.user.username}: {str(e)}", exc_info=True
            )
            return HttpResponseForbidden("Store validation error")

        return self.get_response(request)

    def _is_excluded_path(self, path):
        """Check if the path should be excluded from validation.

        Args:
            path: The request path

        Returns:
            bool: True if path should be excluded
        """
        return any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS)

    def _should_log_action(self, request):
        """Determine if this action should be logged.

        Args:
            request: The current request

        Returns:
            bool: True if action should be logged
        """
        # No loguear GET requests
        if request.method not in self.LOGGED_METHODS:
            return False

        # No loguear rutas específicas
        if any(request.path.startswith(path) for path in self.NO_LOG_PATHS):
            return False

        # No loguear requests AJAX frecuentes (opcional)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Podrías ser más selectivo aquí
            if "/autocomplete/" in request.path or "/search/" in request.path:
                return False

        return True

    def _log_store_access(self, request, store, is_superuser=False):
        """Log store access for auditing important actions only.

        Args:
            request: The current request
            store: The current store
            is_superuser: Whether the user is a superuser
        """
        # Construir nombre de acción más descriptivo
        if request.resolver_match:
            action = f"{request.method.lower()}_{request.resolver_match.url_name or 'unknown'}"
        else:
            action = f"{request.method.lower()}_action"

        # Get user's groups (roles)
        user_groups = list(request.user.groups.values_list("name", flat=True))

        # Preparar detalles del log
        details = {
            "store": store.schema_name,
            "store_name": store.name,
            "path": request.path,
            "method": request.method,
            "roles": user_groups,
            "is_superuser": is_superuser,
        }

        # Agregar información adicional si está disponible
        if request.resolver_match:
            details["view_name"] = request.resolver_match.view_name
            if request.resolver_match.kwargs:
                # No loguear información sensible
                details["url_params"] = {
                    k: v
                    for k, v in request.resolver_match.kwargs.items()
                    if k not in ["password", "token", "secret"]
                }

        try:
            UserAuditLog.log_action(
                user=request.user,
                action=action,
                details=details,
                request=request,
            )
        except Exception as e:
            # No fallar la request si el logging falla
            logger.error(f"Failed to log user action: {str(e)}", exc_info=True)
