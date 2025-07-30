"""Authentication API endpoints."""

import logging
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth import AuthService
from app.core.security import decode_token, verify_token_type
from app.database import get_async_session
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Simple in-memory rate limiting
login_attempts: dict[str, list[datetime]] = defaultdict(list)
RATE_LIMIT_ATTEMPTS = settings.LOGIN_RATE_LIMIT_PER_MINUTE
RATE_LIMIT_WINDOW = (
    timedelta(minutes=1)
    if settings.LOGIN_RATE_LIMIT_PER_MINUTE > 0
    else timedelta(seconds=0)
)


def check_rate_limit(ip_address: str) -> bool:
    """Check if IP address has exceeded rate limit.

    Args:
        ip_address: The IP address to check.

    Returns:
        True if within rate limit, False if exceeded.
    """
    # If rate limiting is disabled (0), always return True
    if RATE_LIMIT_ATTEMPTS == 0:
        return True

    now = datetime.now(UTC)
    attempts = login_attempts[ip_address]

    # Remove old attempts outside the window
    attempts[:] = [attempt for attempt in attempts if now - attempt < RATE_LIMIT_WINDOW]

    # Check if exceeded
    if len(attempts) >= RATE_LIMIT_ATTEMPTS:
        return False

    # Record this attempt
    attempts.append(now)
    return True


def get_client_ip(request: Request) -> str:
    """Get client IP address from request.

    Args:
        request: FastAPI request object.

    Returns:
        Client IP address.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_async_session),
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        token: JWT access token.
        db: Database session.

    Returns:
        Current user object.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = decode_token(token)

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
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


def require_role(allowed_roles: list[str]):
    """Dependency to require specific roles.

    Args:
        allowed_roles: List of allowed roles.

    Returns:
        Dependency function that checks user role.
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db: Session = Depends(get_async_session),
) -> TokenResponse:
    """Login endpoint to authenticate users and issue tokens.

    Rate limited to 5 attempts per 15 minutes per IP address.

    Args:
        request: FastAPI request object.
        response: FastAPI response object.
        login_data: Login credentials.
        db: Database session.

    Returns:
        JWT tokens on successful authentication.

    Raises:
        HTTPException: If authentication fails or rate limit exceeded.
    """
    print("[API LOGIN DEBUG] Login endpoint called")
    print(f"[API LOGIN DEBUG] Request data: email={login_data.email}")

    # Check rate limit
    client_ip = get_client_ip(request)
    print(f"[API LOGIN DEBUG] Client IP: {client_ip}")

    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        print(f"[API LOGIN DEBUG] Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )

    auth_service = AuthService(db)
    print("[API LOGIN DEBUG] AuthService created")

    # Log login attempt
    logger.info(f"Login attempt for email: {login_data.email} from IP: {client_ip}")
    print(f"[API LOGIN DEBUG] Calling authenticate_user with email: {login_data.email}")

    # Authenticate user
    user = auth_service.authenticate_user(
        email=login_data.email, password=login_data.password
    )
    print(f"[API LOGIN DEBUG] authenticate_user returned: {user}")

    if not user:
        # Log failed attempt
        logger.warning(
            f"Failed login attempt for email: {login_data.email} from IP: {client_ip}"
        )
        print("[API LOGIN DEBUG] Authentication failed - user is None")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    tokens = auth_service.create_tokens(user)

    # Set cookies for web clients
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=8 * 3600,  # 8 hours
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=30 * 24 * 3600,  # 30 days
    )

    # Log successful login
    logger.info(f"Successful login for user: {user.email} (ID: {user.id})")

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_async_session),
) -> TokenResponse:
    """Refresh access token using refresh token.

    Args:
        response: FastAPI response object.
        refresh_data: Refresh token request.
        db: Database session.

    Returns:
        New JWT tokens.

    Raises:
        HTTPException: If refresh token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)

        # Verify token type
        if not verify_token_type(payload, "refresh"):
            raise credentials_exception

        # Get user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception from None

    # Get user from database
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(int(user_id))

    if user is None or not user.is_active:
        raise credentials_exception

    # Generate new tokens
    tokens = auth_service.create_tokens(user)

    # Update cookies
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=8 * 3600,  # 8 hours
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=30 * 24 * 3600,  # 30 days
    )

    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current user information.

    Args:
        current_user: The authenticated user.

    Returns:
        User information.
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    response: Response, current_user: Annotated[User, Depends(get_current_user)]
) -> dict[str, str]:
    """Logout endpoint to clear session cookies.

    Args:
        response: FastAPI response object.
        current_user: The authenticated user.

    Returns:
        Success message.
    """
    # Clear cookies
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )

    # Log logout
    logger.info(f"User logged out: {current_user.email} (ID: {current_user.id})")

    return {"message": "Successfully logged out"}
