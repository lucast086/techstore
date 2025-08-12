"""Payment schemas for TechStore SaaS."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class PaymentType(str, Enum):
    """Payment type enumeration."""

    PAYMENT = "payment"
    ADVANCE_PAYMENT = "advance_payment"
    REFUND = "refund"


class PaymentMethodDetail(BaseModel):
    """Schema for individual payment method in mixed payments."""

    payment_method: str = Field(
        ..., pattern="^(cash|transfer|card)$", description="Payment method"
    )
    amount: Decimal = Field(
        ..., gt=0, decimal_places=2, description="Amount for this method"
    )
    reference_number: str | None = Field(
        None, max_length=100, description="Reference number for non-cash payments"
    )

    @field_validator("reference_number")
    @classmethod
    def validate_reference(cls, v: str | None, info) -> str | None:
        """Validate reference number is required for non-cash payments."""
        method = info.data.get("payment_method")
        if method in ["transfer", "card"] and not v:
            raise ValueError("Reference number required for transfer/card payments")
        return v


class PaymentCreate(BaseModel):
    """Schema for creating a payment."""

    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Payment amount")
    payment_method: str = Field(
        ..., pattern="^(cash|transfer|card|mixed)$", description="Payment method"
    )
    payment_type: PaymentType | None = Field(
        None, description="Type of payment (auto-determined if not provided)"
    )
    reference_number: str | None = Field(
        None, max_length=100, description="Reference number for non-cash payments"
    )
    notes: str | None = Field(None, description="Additional notes")
    payment_methods: list[PaymentMethodDetail] | None = Field(
        None, description="Details for mixed payment methods"
    )

    @field_validator("reference_number")
    @classmethod
    def validate_reference(cls, v: str | None, info) -> str | None:
        """Validate reference number is required for non-cash payments."""
        method = info.data.get("payment_method")
        if method in ["transfer", "card"] and not v:
            raise ValueError("Reference number required for transfer/card payments")
        return v

    @field_validator("payment_methods")
    @classmethod
    def validate_mixed_payments(
        cls, v: list[PaymentMethodDetail] | None, info
    ) -> list[PaymentMethodDetail] | None:
        """Validate mixed payment methods."""
        method = info.data.get("payment_method")
        amount = info.data.get("amount")

        if method == "mixed":
            if not v or len(v) < 2:
                raise ValueError("Mixed payment requires at least 2 payment methods")

            total = sum(pm.amount for pm in v)
            if total != amount:
                raise ValueError(
                    f"Sum of payment methods ({total}) must equal total amount ({amount})"
                )

        return v


class PaymentResponse(BaseModel):
    """Schema for payment responses."""

    id: int
    receipt_number: str
    customer_id: int
    customer_name: str
    sale_id: int | None = None
    amount: float
    payment_method: str
    payment_type: str = "payment"  # Default for backward compatibility
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
