"""Authentication schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import validate_password


class TokenData(BaseModel):
    """Schema for token data extracted from JWT."""

    username: str | None = None


class LoginRequest(BaseModel):
    """Schema for login request.

    Attributes:
        email: User's email address.
        password: User's password.
    """

    email: EmailStr
    password: str = Field(..., min_length=1)

    model_config = {
        "json_schema_extra": {
            "example": {"email": "admin@techstore.com", "password": "SecurePass123!"}
        }
    }


class TokenResponse(BaseModel):
    """Schema for token response.

    Attributes:
        access_token: JWT access token.
        refresh_token: JWT refresh token.
        token_type: Token type (always "bearer").
        expires_in: Access token expiration time in seconds.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 28800,
            }
        }
    }


class TokenPayload(BaseModel):
    """Schema for JWT token payload.

    Attributes:
        sub: Subject (user ID).
        email: User's email.
        role: User's role.
        exp: Expiration timestamp.
        iat: Issued at timestamp.
        type: Token type (access or refresh).
    """

    sub: int
    email: str
    role: str
    exp: datetime
    iat: datetime
    type: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request.

    Attributes:
        refresh_token: The refresh token to use.
    """

    refresh_token: str

    model_config = {
        "json_schema_extra": {
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    }


class UserResponse(BaseModel):
    """Schema for user response (public info).

    Attributes:
        id: User ID.
        email: User's email.
        full_name: User's full name.
        role: User's role.
        is_active: Whether the user is active.
        last_login: Last login timestamp.
        created_at: Creation timestamp.
    """

    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    last_login: datetime | None = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "admin@techstore.com",
                "full_name": "Admin User",
                "role": "admin",
                "is_active": True,
                "last_login": "2024-01-27T10:30:00Z",
                "created_at": "2024-01-01T00:00:00Z",
            }
        },
    }


class UserCreate(BaseModel):
    """Schema for creating a new user.

    Attributes:
        email: User's email address.
        password: User's password (must meet security requirements).
        full_name: User's full name.
        role: User's role (admin or technician).
    """

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., pattern="^(admin|technician)$")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        is_valid, error_message = validate_password(v)
        if not is_valid:
            raise ValueError(error_message)
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "technician@techstore.com",
                "password": "SecurePass123!",
                "full_name": "John Technician",
                "role": "technician",
            }
        }
    }


class PasswordChange(BaseModel):
    """Schema for password change request.

    Attributes:
        current_password: User's current password.
        new_password: User's new password.
    """

    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password meets security requirements."""
        is_valid, error_message = validate_password(v)
        if not is_valid:
            raise ValueError(error_message)
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "OldSecurePass123!",
                "new_password": "NewSecurePass456!",
            }
        }
    }
