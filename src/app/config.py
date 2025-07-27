"""Configuration settings for TechStore SaaS."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@db:5432/techstore_db",
        description="PostgreSQL database URL",
    )

    # Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Secret key for session signing and JWT tokens",
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
