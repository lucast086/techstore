"""Expense related schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ExpenseCategoryBase(BaseModel):
    """Base schema for expense categories."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ExpenseCategoryCreate(ExpenseCategoryBase):
    """Schema for creating an expense category."""

    pass


class ExpenseCategoryUpdate(BaseModel):
    """Schema for updating an expense category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ExpenseCategoryResponse(ExpenseCategoryBase):
    """Schema for expense category response."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ExpenseCategoryList(BaseModel):
    """Schema for expense category dropdown list."""

    id: int
    name: str

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Expense Schemas
class ExpenseBase(BaseModel):
    """Base schema for expenses."""

    category_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: str = Field(..., min_length=1)
    expense_date: date = Field(default_factory=date.today)
    payment_method: str = Field(..., pattern="^(cash|transfer|card)$")
    receipt_number: Optional[str] = Field(None, max_length=100)
    supplier_name: Optional[str] = Field(None, max_length=200)

    @field_validator("expense_date")
    @classmethod
    def validate_not_future(cls, v: date) -> date:
        """Ensure expense date is not in the future."""
        if v > date.today():
            raise ValueError("Expense date cannot be in the future")
        return v


class ExpenseCreate(ExpenseBase):
    """Schema for creating an expense."""

    pass


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense."""

    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    description: Optional[str] = Field(None, min_length=1)
    payment_method: Optional[str] = Field(None, pattern="^(cash|transfer|card)$")
    receipt_number: Optional[str] = Field(None, max_length=100)
    supplier_name: Optional[str] = Field(None, max_length=200)


class ExpenseResponse(ExpenseBase):
    """Schema for expense response."""

    id: int
    category_name: str
    created_by: int
    created_by_name: str
    is_editable: bool
    receipt_file_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ExpenseFilter(BaseModel):
    """Schema for expense filtering."""

    date_from: Optional[date] = None
    date_to: Optional[date] = None
    category_id: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None


class ExpenseSummary(BaseModel):
    """Schema for expense summary (daily closing)."""

    total_amount: Decimal
    expense_count: int
    by_category: dict[str, Decimal]
    by_payment_method: dict[str, Decimal]
