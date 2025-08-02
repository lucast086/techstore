"""Base schemas for common functionality."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime
    updated_at: datetime


class ResponseSchema(BaseSchema, Generic[T]):
    """Base schema for API responses."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    meta: Optional[dict[str, Any]] = None


class ErrorResponse(BaseSchema):
    """Schema for error responses."""

    success: bool = False
    message: str
    errors: Optional[dict[str, Any]] = None


class PaginationParams(BaseSchema):
    """Schema for pagination parameters."""

    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size
