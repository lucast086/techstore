"""Pydantic schemas for supplier data validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    """Base schema for supplier data."""

    name: str = Field(..., min_length=1, max_length=200, description="Supplier name")
    contact_name: Optional[str] = Field(
        None, max_length=100, description="Contact person"
    )
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    address: Optional[str] = Field(None, description="Supplier address")
    is_active: bool = Field(True, description="Whether supplier is active")


class SupplierCreate(SupplierBase):
    """Schema for creating a new supplier."""

    pass


class SupplierUpdate(BaseModel):
    """Schema for updating a supplier."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierInDB(SupplierBase):
    """Schema for supplier data from database."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Supplier(SupplierInDB):
    """Schema for supplier API responses."""

    pass


class SupplierList(BaseModel):
    """Schema for supplier list responses."""

    items: list[Supplier]
    total: int
    page: int
    page_size: int
    pages: int
