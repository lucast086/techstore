"""Schemas for cash closing operations."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field, validator

from app.schemas.base import BaseSchema, TimestampSchema


class CashClosingBase(BaseSchema):
    """Base schema for cash closing operations."""

    closing_date: date = Field(..., description="Date of the closing")
    opening_balance: Decimal = Field(
        ..., ge=0, description="Cash balance at start of day"
    )
    sales_total: Decimal = Field(
        ..., ge=0, description="Total sales amount for the day"
    )
    expenses_total: Decimal = Field(
        default=Decimal("0.00"), ge=0, description="Total expenses for the day"
    )
    cash_count: Decimal = Field(..., ge=0, description="Actual cash counted at closing")
    notes: Optional[str] = Field(None, max_length=1000, description="Closing notes")


class CashClosingCreate(BaseSchema):
    """Schema for creating a new cash closing."""

    closing_date: date = Field(..., description="Date of the closing")
    opening_balance: Decimal = Field(
        ..., ge=0, description="Cash balance at start of day"
    )
    cash_count: Decimal = Field(..., ge=0, description="Actual cash counted at closing")
    notes: Optional[str] = Field(None, max_length=1000, description="Closing notes")

    @validator("closing_date")
    def validate_closing_date(cls, v: date) -> date:
        """Validate that closing date is not in the future."""
        if v > date.today():
            raise ValueError("Closing date cannot be in the future")
        return v


class CashClosingUpdate(BaseSchema):
    """Schema for updating a draft cash closing."""

    opening_balance: Optional[Decimal] = Field(None, ge=0)
    cash_count: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)

    @validator("opening_balance", "cash_count", pre=True)
    def validate_not_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Ensure monetary values are not negative."""
        if v is not None and v < 0:
            raise ValueError("Monetary values cannot be negative")
        return v


class CashClosingResponse(CashClosingBase, TimestampSchema):
    """Schema for cash closing response."""

    id: int
    expected_cash: Decimal = Field(..., description="Expected cash balance")
    cash_difference: Decimal = Field(
        ..., description="Difference between actual and expected"
    )
    closed_by: int = Field(..., description="ID of user who performed closing")
    closed_at: datetime = Field(..., description="Timestamp when closing was performed")
    is_finalized: bool = Field(..., description="Whether closing is finalized")
    closed_by_name: Optional[str] = Field(None, description="Name of user who closed")

    @property
    def status(self) -> str:
        """Get closing status as string."""
        return "Finalized" if self.is_finalized else "Draft"

    @property
    def is_balanced(self) -> bool:
        """Check if cash count matches expected amount within tolerance."""
        tolerance = Decimal("1.00")  # $1 tolerance
        return abs(self.cash_difference) <= tolerance


class CashClosingSummary(BaseSchema):
    """Schema for cash closing summary in lists."""

    id: int
    closing_date: date
    sales_total: Decimal
    cash_difference: Decimal
    is_finalized: bool
    closed_by_name: Optional[str] = None

    @property
    def status(self) -> str:
        """Get closing status as string."""
        return "Finalized" if self.is_finalized else "Draft"


class DailySummary(BaseSchema):
    """Schema for aggregated daily financial data."""

    date: date
    total_sales: Decimal = Field(
        default=Decimal("0.00"), description="Total sales for the day"
    )
    total_expenses: Decimal = Field(
        default=Decimal("0.00"), description="Total expenses for the day"
    )
    sales_count: int = Field(default=0, description="Number of sales transactions")
    expenses_count: int = Field(default=0, description="Number of expense entries")
    has_closing: bool = Field(default=False, description="Whether day has been closed")


class CashClosingFinalize(BaseSchema):
    """Schema for finalizing a cash closing."""

    notes: Optional[str] = Field(
        None, max_length=1000, description="Final closing notes"
    )


class CashClosingList(BaseSchema):
    """Schema for listing cash closings with pagination."""

    closings: list[CashClosingSummary]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool
