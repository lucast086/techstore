"""Schemas for customer account management."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.customer_account import TransactionType


class CustomerAccountBase(BaseModel):
    """Base schema for customer accounts."""

    credit_limit: Decimal = Field(
        default=Decimal("0.00"), ge=0, description="Maximum credit allowed"
    )
    is_active: bool = Field(default=True, description="Whether account is active")
    notes: Optional[str] = Field(None, description="Account notes")


class CustomerAccountCreate(CustomerAccountBase):
    """Schema for creating customer account."""

    customer_id: int = Field(..., description="Customer ID")
    initial_balance: Optional[Decimal] = Field(
        default=Decimal("0.00"),
        description="Initial account balance (negative for credit)",
    )


class CustomerAccountUpdate(BaseModel):
    """Schema for updating customer account."""

    credit_limit: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    block_reason: Optional[str] = None
    blocked_until: Optional[datetime] = None


class CustomerAccountResponse(CustomerAccountBase):
    """Schema for customer account responses."""

    id: int
    customer_id: int
    customer_name: str
    account_balance: Decimal
    available_credit: Decimal
    total_sales: Decimal
    total_payments: Decimal
    last_transaction_date: Optional[datetime]
    last_payment_date: Optional[datetime]
    transaction_count: int
    is_blocked: bool
    blocked_until: Optional[datetime]
    block_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Computed properties
    has_debt: bool
    has_credit: bool
    is_settled: bool
    total_available_credit: Decimal
    remaining_credit_limit: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class CustomerAccountSummary(BaseModel):
    """Summary schema for customer accounts in lists."""

    id: int
    customer_id: int
    customer_name: str
    customer_phone: str
    account_balance: Decimal
    credit_limit: Decimal
    last_activity: Optional[datetime]
    is_active: bool
    status: str  # 'debt', 'credit', 'settled'

    class Config:
        """Pydantic config."""

        from_attributes = True


class CustomerTransactionBase(BaseModel):
    """Base schema for customer transactions."""

    transaction_type: TransactionType
    amount: Decimal = Field(gt=0, description="Transaction amount (always positive)")
    description: str = Field(..., max_length=200)
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None


class CustomerTransactionCreate(CustomerTransactionBase):
    """Schema for creating customer transaction."""

    customer_id: int
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Ensure amount has proper decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")
        return v


class CustomerTransactionResponse(CustomerTransactionBase):
    """Schema for transaction responses."""

    id: int
    customer_id: int
    account_id: int
    balance_before: Decimal
    balance_after: Decimal
    reference_type: Optional[str]
    reference_id: Optional[int]
    created_at: datetime
    created_by_id: int
    created_by_name: str

    # Computed
    is_debit: bool
    is_credit: bool
    impact_amount: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class AccountStatementRequest(BaseModel):
    """Request schema for account statements."""

    customer_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_details: bool = Field(default=True)


class AccountStatement(BaseModel):
    """Schema for customer account statements."""

    customer_id: int
    customer_name: str
    statement_date: datetime
    period_start: datetime
    period_end: datetime

    # Balances
    opening_balance: Decimal
    closing_balance: Decimal
    total_debits: Decimal
    total_credits: Decimal

    # Transaction summary
    transaction_count: int
    transactions: list[CustomerTransactionResponse]

    # Current status
    current_balance: Decimal
    credit_limit: Decimal
    available_credit: Decimal
    days_overdue: Optional[int] = None


class AccountsReceivableAging(BaseModel):
    """Schema for AR aging report."""

    customer_id: int
    customer_name: str
    total_outstanding: Decimal
    current: Decimal = Field(description="0-30 days")
    days_31_60: Decimal
    days_61_90: Decimal
    over_90_days: Decimal
    oldest_invoice_date: Optional[datetime]

    class Config:
        """Pydantic config."""

        from_attributes = True


class CreditApplicationRequest(BaseModel):
    """Request to apply customer credit to a sale."""

    customer_id: int
    sale_id: int
    amount: Decimal = Field(gt=0, description="Credit amount to apply")
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Ensure proper decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")
        return v


class AccountAdjustmentRequest(BaseModel):
    """Request for manual account adjustment."""

    customer_id: int
    adjustment_type: str = Field(pattern="^(credit|debit)$")
    amount: Decimal = Field(gt=0)
    reason: str = Field(min_length=10, max_length=200)
    notes: Optional[str] = None


class CreditApplicationResponse(BaseModel):
    """Response for credit application."""

    transaction: CustomerTransactionResponse
    amount_applied: Decimal
    success: bool
    message: str


class CreditAvailabilityResponse(BaseModel):
    """Response for credit availability check."""

    has_credit: bool
    available_amount: Decimal
    message: str


class UpdateCreditLimit(BaseModel):
    """Request to update credit limit."""

    credit_limit: Decimal = Field(ge=0, description="New credit limit")
    notes: Optional[str] = None


class AccountsReceivableSummary(BaseModel):
    """Summary of all accounts receivable."""

    total_accounts: int
    accounts_with_debt: int
    accounts_with_credit: int
    total_debt: Decimal
    total_credit: Decimal
    net_receivable: Decimal
    generated_at: datetime
