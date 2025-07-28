"""Security utilities for authentication and authorization."""

import re
from datetime import UTC, datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)

# Password validation regex
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify.
        hashed_password: The hashed password to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: The plain text password to hash.

    Returns:
        The hashed password.
    """
    return pwd_context.hash(password)


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements.

    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character (@$!%*?&)

    Args:
        password: The password to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    if not re.search(r"[@$!%*?&]", password):
        return False, "Password must contain at least one special character (@$!%*?&)"

    return True, ""


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data: The data to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        The encoded JWT token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token.

    Args:
        data: The data to encode in the token.

    Returns:
        The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token.

    Args:
        token: The JWT token to decode.

    Returns:
        The decoded token payload.

    Raises:
        JWTError: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise


def verify_token_type(payload: dict[str, Any], expected_type: str) -> bool:
    """Verify the token type matches expected type.

    Args:
        payload: The decoded token payload.
        expected_type: The expected token type ("access" or "refresh").

    Returns:
        True if the token type matches, False otherwise.
    """
    return payload.get("type") == expected_type
