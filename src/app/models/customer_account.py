"""Customer account models for accounts receivable system."""

import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.utils.timezone import get_utc_now

if TYPE_CHECKING:
    pass


class TransactionType(str, enum.Enum):
    """Types of customer account transactions."""

    SALE = "sale"  # Increases debt
    PAYMENT = "payment"  # Reduces debt
    CREDIT_NOTE = "credit_note"  # Reduces debt
    DEBIT_NOTE = "debit_note"  # Increases debt
    CREDIT_APPLICATION = "credit_application"  # Uses available credit
    OPENING_BALANCE = "opening_balance"  # Initial balance setup
    ADJUSTMENT = "adjustment"  # Manual adjustments
    REPAIR_DEPOSIT = "repair_deposit"  # Deposit for repair (credit to customer)
    VOID_SALE = "void_sale"  # Reverses a voided sale (reduces debt)


class CustomerAccount(BaseModel):
    """Customer account ledger for tracking balances.

    This model maintains the current account state for each customer.
    Balance convention:
    - Negative balance: Customer has credit (we owe them)
    - Positive balance: Customer owes us (accounts receivable)
    - Zero balance: Account is settled

    Attributes:
        customer_id: FK to customer
        credit_limit: Maximum credit allowed (0 = no credit)
        available_credit: Pre-paid credit available for use
        account_balance: Current balance (+ = owes, - = has credit)
        total_sales: Lifetime sales amount
        total_payments: Lifetime payments received
        last_transaction_date: Date of last activity
        is_active: Whether account can be used
        blocked_until: Temporary block date
        block_reason: Reason for blocking
    """

    __tablename__ = "customer_accounts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Customer relationship (one-to-one)
    customer_id = Column(
        Integer, ForeignKey("customers.id"), unique=True, nullable=False
    )

    # Credit management
    credit_limit = Column(DECIMAL(10, 2), default=0, nullable=False)
    available_credit = Column(DECIMAL(10, 2), default=0, nullable=False)

    # Current balance (+ = debt, - = credit)
    account_balance = Column(DECIMAL(10, 2), default=0, nullable=False, index=True)

    # Lifetime totals for reporting
    total_sales = Column(DECIMAL(12, 2), default=0, nullable=False)
    total_payments = Column(DECIMAL(12, 2), default=0, nullable=False)
    total_credit_notes = Column(DECIMAL(12, 2), default=0, nullable=False)
    total_debit_notes = Column(DECIMAL(12, 2), default=0, nullable=False)

    # Activity tracking
    last_transaction_date = Column(DateTime, nullable=True)
    last_payment_date = Column(DateTime, nullable=True)
    transaction_count = Column(Integer, default=0, nullable=False)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    blocked_until = Column(DateTime, nullable=True)
    block_reason = Column(Text, nullable=True)

    # Audit fields
    notes = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="account", uselist=False)
    transactions = relationship(
        "CustomerTransaction", back_populates="account", lazy="dynamic"
    )
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])

    # Indexes
    __table_args__ = (
        Index("idx_customer_account_balance", "account_balance", "is_active"),
        Index("idx_customer_account_activity", "last_transaction_date", "is_active"),
    )

    def __repr__(self):
        """String representation."""
        return f"<CustomerAccount {self.customer_id}: Balance={self.account_balance}>"

    @property
    def has_debt(self) -> bool:
        """Check if customer has outstanding debt."""
        return self.account_balance > 0

    @property
    def has_credit(self) -> bool:
        """Check if customer has credit balance."""
        return self.account_balance < 0

    @property
    def is_settled(self) -> bool:
        """Check if account is settled (zero balance)."""
        return self.account_balance == 0

    @property
    def total_available_credit(self) -> Decimal:
        """Total credit available (prepaid + credit limit)."""
        # If balance is negative (credit), add to available credit
        balance_credit = (
            abs(self.account_balance) if self.account_balance < 0 else Decimal(0)
        )
        return self.available_credit + balance_credit

    @property
    def remaining_credit_limit(self) -> Decimal:
        """Remaining credit limit available."""
        if self.account_balance > 0:  # Has debt
            return max(Decimal(0), self.credit_limit - self.account_balance)
        return self.credit_limit

    @property
    def is_blocked(self) -> bool:
        """Check if account is currently blocked."""
        if self.blocked_until:
            utc_now = get_utc_now()
            # Handle both timezone-aware and naive datetimes
            blocked_until = self.blocked_until
            if blocked_until.tzinfo is None:
                # If blocked_until is naive, assume it's UTC
                from zoneinfo import ZoneInfo

                blocked_until = blocked_until.replace(tzinfo=ZoneInfo("UTC"))
            return blocked_until > utc_now
        return False


class CustomerTransaction(BaseModel):
    """Individual customer account transactions.

    This model maintains an immutable audit trail of all transactions.
    Each transaction updates the customer's account balance.

    Attributes:
        customer_id: FK to customer
        transaction_type: Type of transaction
        amount: Transaction amount (always positive)
        balance_before: Account balance before transaction
        balance_after: Account balance after transaction
        reference_type: Type of related document (sale, payment, etc.)
        reference_id: ID of related document
        description: Human-readable description
        transaction_date: When transaction occurred
        created_by_id: User who created transaction
    """

    __tablename__ = "customer_transactions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Customer and account
    customer_id = Column(
        Integer, ForeignKey("customers.id"), nullable=False, index=True
    )
    account_id = Column(Integer, ForeignKey("customer_accounts.id"), nullable=False)

    # Transaction details
    transaction_type = Column(
        Enum(
            TransactionType,
            values_callable=lambda x: [e.value for e in x],
            name="transactiontype",
        ),
        nullable=False,
        index=True,
    )
    amount = Column(DECIMAL(10, 2), nullable=False)

    # Balance tracking (for audit trail)
    balance_before = Column(DECIMAL(10, 2), nullable=False)
    balance_after = Column(DECIMAL(10, 2), nullable=False)

    # Reference to source document
    reference_type = Column(String(50), nullable=True)  # 'sale', 'payment', etc.
    reference_id = Column(Integer, nullable=True)

    # Description and notes
    description = Column(String(200), nullable=False)
    notes = Column(Text, nullable=True)

    # Transaction metadata
    transaction_date = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Note: created_at and updated_at are inherited from BaseModel via TimestampMixin
    # which already includes server_default=func.now()
    # Since transactions are immutable, updated_at should never change from created_at

    # Relationships
    customer = relationship("Customer", backref="account_transactions")
    account = relationship("CustomerAccount", back_populates="transactions")
    created_by = relationship("User", backref="customer_transactions")

    # Indexes for performance
    __table_args__ = (
        Index("idx_customer_trans_date", "customer_id", "transaction_date"),
        Index("idx_customer_trans_type", "customer_id", "transaction_type"),
        Index("idx_customer_trans_ref", "reference_type", "reference_id"),
        # Ensure transactions are immutable
        UniqueConstraint("id", "created_at", name="uq_transaction_immutable"),
    )

    def __repr__(self):
        """String representation."""
        return (
            f"<CustomerTransaction {self.id}: {self.transaction_type} "
            f"${self.amount} -> Balance: {self.balance_after}>"
        )

    @property
    def is_debit(self) -> bool:
        """Check if transaction increases debt."""
        return self.transaction_type in [
            TransactionType.SALE,
            TransactionType.DEBIT_NOTE,
        ]

    @property
    def is_credit(self) -> bool:
        """Check if transaction reduces debt."""
        return self.transaction_type in [
            TransactionType.PAYMENT,
            TransactionType.CREDIT_NOTE,
        ]

    @property
    def impact_amount(self) -> Decimal:
        """Get amount with proper sign for balance calculation."""
        if self.is_debit:
            return self.amount  # Positive increases debt
        else:
            return -self.amount  # Negative reduces debt
