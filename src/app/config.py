"""Configuration settings for TechStore SaaS."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@db:5432/techstore_db",
        description="PostgreSQL database URL",
    )
    TEST_DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@db:5432/techstore_db",
        description="PostgreSQL test database URL (same as main DB in dev)",
    )

    # Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Secret key for session signing and JWT tokens",
    )

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        default="your-jwt-secret-key-here-change-in-production",
        description="Secret key for JWT tokens",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRATION_HOURS: int = Field(
        default=8, description="JWT token expiration in hours"
    )
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(
        default=7, description="JWT refresh token expiration in days"
    )

    # Password Security
    BCRYPT_ROUNDS: int = Field(default=12, description="Bcrypt hashing rounds")

    # Rate Limiting
    LOGIN_RATE_LIMIT_PER_MINUTE: int = Field(
        default=5, description="Login attempts per minute"
    )
    LOGIN_RATE_LIMIT_PER_HOUR: int = Field(
        default=20, description="Login attempts per hour"
    )

    # Application
    app_name: str = Field(default="TechStore SaaS", description="Application name")
    debug: bool = Field(default=True, description="Debug mode")
    environment: str = Field(
        default="development", description="Environment (development/production)"
    )

    # CORS
    backend_cors_origins: list[str] = Field(
        default=["http://localhost:8000", "http://127.0.0.1:8000"],
        description="Allowed CORS origins",
    )

    # Pagination
    default_page_size: int = Field(default=20, description="Default pagination size")
    max_page_size: int = Field(default=100, description="Maximum pagination size")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
