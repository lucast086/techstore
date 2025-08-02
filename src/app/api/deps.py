"""API dependencies - imports from existing modules."""

from app.api.v1.auth import get_current_user as get_current_active_user
from app.api.v1.auth import oauth2_scheme
from app.dependencies import get_db

__all__ = ["get_db", "get_current_active_user", "oauth2_scheme"]
