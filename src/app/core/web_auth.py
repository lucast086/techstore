"""Web authentication dependencies for cookie-based auth."""

import logging
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token, verify_token_type
from app.dependencies import get_db
from app.models.user import User

logger = logging.getLogger(__name__)


async def get_current_user_from_cookie(
    request: Request,
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from cookie-based JWT token.

    Args:
        request: FastAPI request object.
        access_token: JWT access token from cookie.
        db: Database session.

    Returns:
        Current user object.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = decode_token(access_token)

        # Verify token type
        if not verify_token_type(payload, "access"):
            raise credentials_exception

        # Get user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception from None

    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


async def get_current_user_optional(
    request: Request,
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> User | None:
    """Get current authenticated user from cookie-based JWT token.

    Returns None if user is not authenticated instead of raising an exception.
    This is useful for public pages that need to show different content
    based on authentication status.

    Args:
        request: FastAPI request object.
        access_token: JWT access token from cookie.
        db: Database session.

    Returns:
        Current user object or None if not authenticated.
    """
    if not access_token:
        return None

    try:
        # Decode token
        payload = decode_token(access_token)

        # Verify token type
        if not verify_token_type(payload, "access"):
            return None

        # Get user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

    except JWTError:
        return None

    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None or not user.is_active:
        return None

    return user


def require_web_role(allowed_roles: list[str]):
    """Dependency to require specific roles for web routes.

    Args:
        allowed_roles: List of allowed roles.

    Returns:
        Dependency function that checks user role.
    """

    def role_checker(
        current_user: User = Depends(get_current_user_from_cookie),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker
