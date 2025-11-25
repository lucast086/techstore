"""Pydantic schemas for repair deposits."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DepositStatus(str, Enum):
    """Status of a repair deposit."""

    ACTIVE = "active"
    APPLIED = "applied"
    REFUNDED = "refunded"
    VOIDED = "voided"


class PaymentMethod(str, Enum):
    """Payment methods for deposits."""

    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    CHECK = "check"
    OTHER = "other"


class DepositBase(BaseModel):
    """Base schema for deposit data."""

    amount: Decimal = Field(..., gt=0, description="Deposit amount")
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount has at most 2 decimal places."""
        if v and v.as_tuple().exponent < -2:
            raise ValueError("Amount can have at most 2 decimal places")
        return v


class DepositCreate(DepositBase):
    """Schema for creating a new deposit."""

    repair_id: int = Field(..., description="ID of the repair")
    customer_id: int = Field(..., description="ID of the customer")


class DepositUpdate(BaseModel):
    """Schema for updating deposit information."""

    notes: Optional[str] = Field(None, max_length=500)
    # Status updates are handled through specific endpoints (refund, void, apply)


class DepositRefund(BaseModel):
    """Schema for refunding a deposit."""

    refund_amount: Optional[Decimal] = Field(
        None, gt=0, description="Amount to refund (defaults to full amount)"
    )
    refund_reason: str = Field(..., min_length=1, max_length=500)

    @field_validator("refund_amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount has at most 2 decimal places."""
        if v and v.as_tuple().exponent < -2:
            raise ValueError("Amount can have at most 2 decimal places")
        return v


class DepositResponse(BaseModel):
    """Schema for deposit response."""

    id: int
    repair_id: int
    customer_id: int
    sale_id: Optional[int]
    amount: Decimal
    payment_method: PaymentMethod
    receipt_number: str
    status: DepositStatus
    refunded_amount: Optional[Decimal]
    refund_date: Optional[datetime]
    refund_reason: Optional[str]
    transaction_id: Optional[int]
    notes: Optional[str]
    received_by_id: int
    created_at: datetime
    updated_at: datetime

    # Additional computed fields
    customer_name: Optional[str] = None
    repair_number: Optional[str] = None
    received_by_name: Optional[str] = None
    refunded_by_name: Optional[str] = None

    model_config = {"from_attributes": True}


class DepositSummary(BaseModel):
    """Summary of deposits for a repair."""

    repair_id: int
    total_deposits: Decimal = Field(default=Decimal("0.00"))
    active_deposits: Decimal = Field(default=Decimal("0.00"))
    applied_deposits: Decimal = Field(default=Decimal("0.00"))
    refunded_deposits: Decimal = Field(default=Decimal("0.00"))
    deposit_count: int = Field(default=0)
    deposits: list[DepositResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class DepositListParams(BaseModel):
    """Parameters for listing deposits."""

    repair_id: Optional[int] = None
    customer_id: Optional[int] = None
    status: Optional[DepositStatus] = None
    payment_method: Optional[PaymentMethod] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
