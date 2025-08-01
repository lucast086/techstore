"""Pydantic schemas for warranty management."""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampSchema


class WarrantyStatus(str, Enum):
    """Valid warranty status values."""

    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"
    VOIDED = "voided"


class CoverageType(str, Enum):
    """Types of warranty coverage."""

    FULL = "full"
    PARTS_ONLY = "parts_only"
    LABOR_ONLY = "labor_only"
    LIMITED = "limited"


class WarrantyBase(BaseSchema):
    """Base schema for warranties."""

    coverage_type: CoverageType = Field(default=CoverageType.FULL)
    parts_warranty_days: int = Field(default=90, ge=0)
    labor_warranty_days: int = Field(default=30, ge=0)
    terms: Optional[str] = None
    exclusions: Optional[str] = None


class WarrantyCreate(WarrantyBase):
    """Schema for creating a warranty."""

    repair_id: int


class WarrantyUpdate(BaseSchema):
    """Schema for updating warranty details."""

    terms: Optional[str] = None
    exclusions: Optional[str] = None


class WarrantyVoid(BaseSchema):
    """Schema for voiding a warranty."""

    void_reason: str = Field(..., min_length=1)
    voided_by: int


class WarrantyClaimBase(BaseSchema):
    """Base schema for warranty claims."""

    issue_description: str = Field(..., min_length=1)
    parts_covered: bool = Field(default=False)
    labor_covered: bool = Field(default=False)


class WarrantyClaimCreate(WarrantyClaimBase):
    """Schema for creating a warranty claim."""

    warranty_id: int
    approved_by: Optional[int] = None


class WarrantyClaimUpdate(BaseSchema):
    """Schema for updating a warranty claim."""

    resolution_notes: Optional[str] = None
    approved: bool = Field(default=True)
    approved_by: Optional[int] = None


class WarrantyInDB(WarrantyBase, TimestampSchema):
    """Schema for warranty in database."""

    id: int
    repair_id: int
    warranty_number: str
    status: WarrantyStatus
    start_date: date
    parts_expiry_date: date
    labor_expiry_date: date
    void_reason: Optional[str] = None
    voided_at: Optional[datetime] = None
    voided_by: Optional[int] = None


class WarrantyClaimInDB(WarrantyClaimBase, TimestampSchema):
    """Schema for warranty claim in database."""

    id: int
    warranty_id: int
    repair_id: int
    claim_number: str
    claim_date: date
    resolution_notes: Optional[str] = None
    approved: bool
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None


class WarrantyResponse(WarrantyInDB):
    """Schema for warranty responses with related data."""

    repair_number: str
    customer_name: str
    device_type: str
    device_brand: str
    device_model: Optional[str] = None
    is_parts_valid: bool
    is_labor_valid: bool
    is_valid: bool
    days_remaining_parts: int
    days_remaining_labor: int
    voided_by_name: Optional[str] = None


class WarrantyClaimResponse(WarrantyClaimInDB):
    """Schema for warranty claim responses with related data."""

    warranty_number: str
    repair_number: str
    customer_name: str
    approved_by_name: Optional[str] = None


class WarrantyListResponse(BaseSchema):
    """Schema for warranty list responses."""

    id: int
    warranty_number: str
    repair_number: str
    customer_name: str
    device_type: str
    status: WarrantyStatus
    start_date: date
    parts_expiry_date: date
    labor_expiry_date: date
    is_valid: bool


class WarrantySearchParams(BaseSchema):
    """Schema for warranty search parameters."""

    q: Optional[str] = Field(None, description="Search query")
    status: Optional[WarrantyStatus] = None
    customer_id: Optional[int] = None
    expired: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """Calculate offset for pagination."""
        return (self.page - 1) * self.page_size


class WarrantyStatistics(BaseSchema):
    """Schema for warranty statistics."""

    total_warranties: int
    active_warranties: int
    expired_warranties: int
    claimed_warranties: int
    voided_warranties: int
    total_claims: int
    approved_claims: int
    claim_rate: float
    average_claim_days: Optional[float] = None


class WarrantyCheckRequest(BaseSchema):
    """Schema for checking warranty validity."""

    warranty_number: Optional[str] = None
    repair_number: Optional[str] = None
    customer_phone: Optional[str] = None

    @field_validator("warranty_number", "repair_number", "customer_phone")
    @classmethod
    def validate_at_least_one(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Ensure at least one search parameter is provided."""
        if not v and not any(values.values()):
            raise ValueError("At least one search parameter is required")
        return v


class WarrantyCheckResponse(BaseSchema):
    """Schema for warranty check response."""

    found: bool
    warranties: list[WarrantyResponse] = []
    message: Optional[str] = None
