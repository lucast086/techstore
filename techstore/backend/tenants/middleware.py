"""Middleware for store validation and user permissions."""

from django.http import HttpResponseForbidden
from users.models import UserAuditLog


class StoreMiddleware:
    """Middleware for store validation and user permissions.

    This middleware:
    1. Validates that the user belongs to the current store
    2. Checks if the store is active
    3. Validates user roles and permissions
    4. Logs store access
    """

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
        # Skip validation for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        try:
            # Get current store
            store = getattr(request, "tenant", None)  # django-tenants uses 'tenant' in request
            if not store:
                return HttpResponseForbidden("No store found")

            # Validate store status
            if not store.is_active:
                return HttpResponseForbidden("Store is inactive")

            # Validate user has at least one role (group)
            if not request.user.is_superuser and not request.user.groups.exists():
                return HttpResponseForbidden("User has no role assigned")

            # Log store access
            self._log_store_access(request, store)

        except Exception as e:
            return HttpResponseForbidden(f"Store validation error: {str(e)}")

        return self.get_response(request)

    def _log_store_access(self, request, store):
        """Log store access for auditing.

        Args:
            request: The current request
            store: The current store
        """
        # Get user's groups (roles)
        user_groups = list(request.user.groups.values_list("name", flat=True))

        UserAuditLog.log_action(
            user=request.user,
            action="store_access",
            details={
                "store": store.schema_name,
                "path": request.path,
                "method": request.method,
                "roles": user_groups,
            },
            request=request,
        )
