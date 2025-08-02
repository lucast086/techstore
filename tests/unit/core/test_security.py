"""Tests for security utilities."""

from datetime import UTC, datetime, timedelta

import pytest
from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    validate_password,
    verify_password,
    verify_token_type,
)
from jose import JWTError, jwt


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_and_verify(self):
        """Test password hashing and verification."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        # Hash should be different from original
        assert hashed != password

        # Should verify correctly
        assert verify_password(password, hashed) is True

        # Wrong password should not verify
        assert verify_password("WrongPassword", hashed) is False

    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "SecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2

        # But both should verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestPasswordValidation:
    """Test password validation rules."""

    def test_valid_password(self):
        """Test valid password passes all checks."""
        valid, error = validate_password("SecurePass123!")
        assert valid is True
        assert error == ""

    def test_password_too_short(self):
        """Test password length validation."""
        valid, error = validate_password("Pass1!")
        assert valid is False
        assert "at least 8 characters" in error

    def test_password_no_uppercase(self):
        """Test uppercase requirement."""
        valid, error = validate_password("securepass123!")
        assert valid is False
        assert "uppercase letter" in error

    def test_password_no_lowercase(self):
        """Test lowercase requirement."""
        valid, error = validate_password("SECUREPASS123!")
        assert valid is False
        assert "lowercase letter" in error

    def test_password_no_number(self):
        """Test number requirement."""
        valid, error = validate_password("SecurePass!")
        assert valid is False
        assert "one number" in error

    def test_password_no_special_char(self):
        """Test special character requirement."""
        valid, error = validate_password("SecurePass123")
        assert valid is False
        assert "special character" in error


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "123", "email": "test@example.com", "role": "admin"}
        token = create_access_token(data)

        # Decode and verify
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "123", "email": "test@example.com", "role": "admin"}
        token = create_refresh_token(data)

        # Decode and verify
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

    def test_access_token_expiration(self):
        """Test access token has correct expiration."""
        data = {"sub": "123"}
        token = create_access_token(data)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=UTC)

        # Check expiration is approximately 8 hours
        diff = exp_time - iat_time
        assert 7.9 * 3600 < diff.total_seconds() < 8.1 * 3600

    def test_refresh_token_expiration(self):
        """Test refresh token has correct expiration."""
        data = {"sub": "123"}
        token = create_refresh_token(data)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=UTC)

        # Check expiration is approximately 30 days
        diff = exp_time - iat_time
        assert 29.9 * 24 * 3600 < diff.total_seconds() < 30.1 * 24 * 3600

    def test_custom_expiration(self):
        """Test token with custom expiration."""
        data = {"sub": "123"}
        custom_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta=custom_delta)

        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=UTC)

        # Check expiration is approximately 5 minutes
        diff = exp_time - iat_time
        assert 4.9 * 60 < diff.total_seconds() < 5.1 * 60

    def test_decode_valid_token(self):
        """Test decoding valid token."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)

        payload = decode_token(token)
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"

    def test_decode_invalid_token(self):
        """Test decoding invalid token raises error."""
        with pytest.raises(JWTError):
            decode_token("invalid-token")

    def test_decode_expired_token(self):
        """Test decoding expired token raises error."""
        data = {"sub": "123"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        with pytest.raises(JWTError):
            decode_token(token)

    def test_verify_token_type(self):
        """Test token type verification."""
        access_payload = {"type": "access", "sub": "123"}
        refresh_payload = {"type": "refresh", "sub": "123"}

        assert verify_token_type(access_payload, "access") is True
        assert verify_token_type(access_payload, "refresh") is False
        assert verify_token_type(refresh_payload, "refresh") is True
        assert verify_token_type(refresh_payload, "access") is False

        # Missing type
        assert verify_token_type({"sub": "123"}, "access") is False
