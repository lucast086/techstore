"""Customer schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerBase(BaseModel):
    """Base customer schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)
    phone_secondary: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Ensure name is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

    @field_validator("phone", "phone_secondary")
    @classmethod
    def phone_format(cls, v: str | None) -> str | None:
        """Validate and clean phone numbers."""
        if v:
            # Remove common formatting characters
            cleaned = "".join(filter(lambda x: x.isdigit() or x == "+", v))
            if len(cleaned) < 7:  # Minimum reasonable phone length
                raise ValueError("El número de teléfono es muy corto")
            return v.strip()
        return v


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""

    pass


class CustomerUpdate(BaseModel):
    """Schema for updating an existing customer."""

    name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, min_length=1, max_length=20)
    phone_secondary: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class CustomerInDB(CustomerBase):
    """Schema for customer stored in database."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: int | None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class CustomerResponse(CustomerInDB):
    """Schema for customer API responses."""

    created_by_name: str | None = None
    balance: float = 0.0  # Will be calculated
    transaction_count: int = 0  # Will be calculated


class CustomerList(BaseModel):
    """Schema for paginated customer list responses."""

    customers: list[CustomerResponse]
    total: int
    page: int
    per_page: int


class CustomerSearch(BaseModel):
    """Schema for customer search requests."""

    query: str = Field(..., min_length=1)
    include_inactive: bool = False
    limit: int = Field(20, ge=1, le=100)
