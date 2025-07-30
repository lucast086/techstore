"""Payment schemas for TechStore SaaS."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class PaymentCreate(BaseModel):
    """Schema for creating a payment."""

    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Payment amount")
    payment_method: str = Field(
        ..., pattern="^(cash|transfer|card)$", description="Payment method"
    )
    reference_number: str | None = Field(
        None, max_length=100, description="Reference number for non-cash payments"
    )
    notes: str | None = Field(None, description="Additional notes")

    @field_validator("reference_number")
    @classmethod
    def validate_reference(cls, v: str | None, info) -> str | None:
        """Validate reference number is required for non-cash payments."""
        method = info.data.get("payment_method")
        if method in ["transfer", "card"] and not v:
            raise ValueError("Reference number required for transfer/card payments")
        return v


class PaymentResponse(BaseModel):
    """Schema for payment responses."""

    id: int
    receipt_number: str
    customer_id: int
    customer_name: str
    amount: float
    payment_method: str
    reference_number: str | None
    notes: str | None
    received_by: str
    created_at: datetime
    voided: bool
    void_reason: str | None = None
    voided_by: str | None = None
    voided_at: datetime | None = None

    model_config = {"from_attributes": True}


class PaymentVoid(BaseModel):
    """Schema for voiding a payment."""

    void_reason: str = Field(
        ..., min_length=10, description="Reason for voiding the payment"
    )


class PaymentListResponse(BaseModel):
    """Schema for listing payments."""

    items: list[PaymentResponse]
    total: int
    page: int
    size: int
    pages: int
