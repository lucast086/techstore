"""Pydantic schemas for repair management."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampSchema


class RepairStatus(str, Enum):
    """Valid repair status values."""

    RECEIVED = "received"
    DIAGNOSING = "diagnosing"
    APPROVED = "approved"
    REPAIRING = "repairing"
    TESTING = "testing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PhotoType(str, Enum):
    """Valid photo types."""

    BEFORE = "before"
    DURING = "during"
    AFTER = "after"


class RepairPartBase(BaseSchema):
    """Base schema for repair parts."""

    part_name: str = Field(..., min_length=1, max_length=200)
    part_cost: Decimal = Field(..., ge=0, decimal_places=2)
    quantity: int = Field(default=1, ge=1)
    supplier: Optional[str] = Field(None, max_length=100)


class RepairPartCreate(RepairPartBase):
    """Schema for creating repair parts."""

    pass


class RepairPartResponse(RepairPartBase):
    """Schema for repair part responses."""

    id: int
    repair_id: int
    created_at: datetime


class RepairPhotoBase(BaseSchema):
    """Base schema for repair photos."""

    photo_url: str = Field(..., max_length=500)
    photo_type: Optional[PhotoType] = None
    description: Optional[str] = None


class RepairPhotoCreate(RepairPhotoBase):
    """Schema for creating repair photos."""

    pass


class RepairPhotoResponse(RepairPhotoBase):
    """Schema for repair photo responses."""

    id: int
    repair_id: int
    uploaded_by: Optional[int] = None
    created_at: datetime


class RepairStatusHistoryBase(BaseSchema):
    """Base schema for repair status history."""

    status: RepairStatus
    notes: Optional[str] = None


class RepairStatusHistoryCreate(RepairStatusHistoryBase):
    """Schema for creating status history entries."""

    changed_by: Optional[int] = None


class RepairStatusHistoryResponse(RepairStatusHistoryBase):
    """Schema for status history responses."""

    id: int
    repair_id: int
    changed_by: Optional[int] = None
    created_at: datetime
    user_name: Optional[str] = None


class RepairBase(BaseSchema):
    """Base schema for repairs."""

    customer_id: int
    device_type: str = Field(..., min_length=1, max_length=50)
    device_brand: str = Field(..., min_length=1, max_length=50)
    device_model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    problem_description: str = Field(..., min_length=1)
    device_condition: Optional[str] = None
    accessories_received: Optional[str] = None
    estimated_completion: Optional[date] = None
    warranty_days: int = Field(default=30, ge=0)
    is_express: bool = Field(default=False)


class RepairCreate(RepairBase):
    """Schema for creating a repair order."""

    assigned_technician: Optional[int] = None
    received_by: Optional[int] = None

    @field_validator("device_type", "device_brand")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """Ensure fields are not empty after stripping."""
        if not value or not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()


class RepairUpdate(BaseSchema):
    """Schema for updating repair details."""

    device_model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    device_condition: Optional[str] = None
    accessories_received: Optional[str] = None
    estimated_completion: Optional[date] = None
    assigned_technician: Optional[int] = None


class RepairDiagnosis(BaseSchema):
    """Schema for adding diagnosis to repair."""

    diagnosis_notes: str = Field(..., min_length=1)
    estimated_cost: Decimal = Field(..., ge=0, decimal_places=2)
    labor_cost: Decimal = Field(..., ge=0, decimal_places=2)
    parts_cost: Decimal = Field(..., ge=0, decimal_places=2)
    parts: Optional[list[RepairPartCreate]] = None


class RepairStatusUpdate(BaseSchema):
    """Schema for updating repair status."""

    status: RepairStatus
    notes: Optional[str] = None


class RepairComplete(BaseSchema):
    """Schema for completing a repair."""

    final_cost: Decimal = Field(..., ge=0, decimal_places=2)
    repair_notes: Optional[str] = None
    warranty_days: int = Field(default=30, ge=0)


class RepairDeliver(BaseSchema):
    """Schema for delivering a repair."""

    delivered_by: int
    customer_signature: Optional[str] = None
    delivery_notes: Optional[str] = None


class RepairInDB(RepairBase, TimestampSchema):
    """Schema for repair in database."""

    id: int
    repair_number: str
    status: RepairStatus
    diagnosis_notes: Optional[str] = None
    repair_notes: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    final_cost: Optional[Decimal] = None
    labor_cost: Optional[Decimal] = None
    parts_cost: Optional[Decimal] = None
    received_date: datetime
    completed_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    warranty_expires: Optional[date] = None
    received_by: Optional[int] = None
    delivered_by: Optional[int] = None
    sale_id: Optional[int] = None
    customer_approved: bool
    approval_date: Optional[datetime] = None


class RepairResponse(RepairInDB):
    """Schema for repair responses with related data."""

    customer_name: str
    customer_phone: str
    technician_name: Optional[str] = None
    receiver_name: Optional[str] = None
    deliverer_name: Optional[str] = None
    parts: list[RepairPartResponse] = []
    photos: list[RepairPhotoResponse] = []
    status_history: list[RepairStatusHistoryResponse] = []
    amount_due: Optional[Decimal] = None


class RepairListResponse(BaseSchema):
    """Schema for repair list responses."""

    id: int
    repair_number: str
    customer_name: str
    device_type: str
    device_brand: str
    device_model: Optional[str] = None
    status: RepairStatus
    received_date: datetime
    estimated_completion: Optional[date] = None
    is_express: bool
    technician_name: Optional[str] = None


class RepairSearchParams(BaseSchema):
    """Schema for repair search parameters."""

    q: Optional[str] = Field(None, description="Search query")
    status: Optional[RepairStatus] = None
    technician_id: Optional[int] = None
    device_type: Optional[str] = None
    device_brand: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_express: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """Calculate offset for pagination."""
        return (self.page - 1) * self.page_size


class RepairStatistics(BaseSchema):
    """Schema for repair statistics."""

    total_repairs: int
    pending_repairs: int
    completed_repairs: int
    delivered_repairs: int
    express_repairs: int
    average_repair_time_days: Optional[float] = None
    total_revenue: Decimal
    pending_revenue: Decimal
