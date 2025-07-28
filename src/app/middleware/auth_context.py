"""Middleware to inject authentication context into requests."""

from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.template_context import get_current_user_context


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Middleware that adds current user to request state for templates."""
    
    async def dispatch(self, request: Request, call_next):
        """Process each request to add user context.
        
        This middleware:
        1. Extracts the access_token from cookies
        2. Attempts to get the current user
        3. Adds the user (or None) to request.state
        4. Templates can then access it via request.state.current_user
        """
        # Get access token from cookies
        access_token = request.cookies.get("access_token")
        
        # Get current user (returns None if not authenticated)
        current_user = await get_current_user_context(request, access_token)
        
        # Add to request state so templates can access it
        request.state.current_user = current_user
        
        # Continue processing the request
        response = await call_next(request)
        return response