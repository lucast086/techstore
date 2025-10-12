"""Database model for repair deposits (señas/adelantos)."""

from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DepositStatus(str, Enum):
    """Status of a repair deposit."""

    ACTIVE = "active"  # Deposit is active and can be applied
    APPLIED = "applied"  # Deposit has been applied to a sale
    REFUNDED = "refunded"  # Deposit has been refunded
    VOIDED = "voided"  # Deposit has been voided (cancelled)


class PaymentMethod(str, Enum):
    """Payment methods for deposits."""

    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    CHECK = "check"
    OTHER = "other"


class RepairDeposit(BaseModel):
    """Model for tracking deposits/payments on repairs."""

    __tablename__ = "repair_deposits"

    id = Column(Integer, primary_key=True, index=True)

    # References
    repair_id = Column(
        Integer, ForeignKey("repairs.id", ondelete="CASCADE"), nullable=False
    )
    customer_id = Column(
        Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False
    )
    sale_id = Column(
        Integer, ForeignKey("sales.id", ondelete="SET NULL"), nullable=True
    )  # Link when applied to sale

    # Deposit details
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(
        SQLEnum(PaymentMethod), nullable=False, default=PaymentMethod.CASH
    )
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)

    # Status tracking
    status = Column(
        SQLEnum(DepositStatus), nullable=False, default=DepositStatus.ACTIVE, index=True
    )

    # Refund details (if applicable)
    refunded_amount = Column(Numeric(10, 2), nullable=True)
    refund_date = Column(DateTime, nullable=True)
    refund_reason = Column(Text, nullable=True)
    refunded_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Transaction reference for customer account
    transaction_id = Column(
        Integer,
        ForeignKey("customer_transactions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Notes
    notes = Column(Text, nullable=True)

    # Audit fields
    received_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )

    # Relationships
    repair = relationship("Repair", back_populates="deposits")
    customer = relationship("Customer", backref="repair_deposits")
    sale = relationship("Sale", backref="applied_deposits")
    received_by = relationship(
        "User", foreign_keys=[received_by_id], backref="deposits_received"
    )
    refunded_by = relationship(
        "User", foreign_keys=[refunded_by_id], backref="deposits_refunded"
    )
    transaction = relationship("CustomerTransaction", backref="deposit")

    def __repr__(self):
        return f"<RepairDeposit(id={self.id}, repair_id={self.repair_id}, amount={self.amount}, status={self.status})>"
