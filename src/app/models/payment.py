"""Payment model for TechStore SaaS."""

import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PaymentType(enum.Enum):
    """Payment type enumeration."""

    PAYMENT = "payment"  # Regular payment for debt
    ADVANCE_PAYMENT = "advance_payment"  # Advance payment (credit)
    REFUND = "refund"  # Refund to customer


class Payment(BaseModel):
    """Payment model for recording customer payments.

    Attributes:
        customer_id: ID of the customer making the payment.
        amount: Payment amount.
        payment_method: Method of payment (cash, transfer, card).
        reference_number: Reference number for non-cash payments.
        notes: Additional notes about the payment.
        receipt_number: Unique receipt number.
        received_by_id: ID of user who recorded the payment.
        voided: Whether the payment has been voided.
        void_reason: Reason for voiding the payment.
        voided_by_id: ID of user who voided the payment.
        voided_at: Timestamp when payment was voided.
    """

    __tablename__ = "payments"

    # Primary key is inherited from BaseModel
    id = Column(Integer, primary_key=True, index=True)

    # Payment details
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sale_id = Column(
        Integer, ForeignKey("sales.id"), nullable=True
    )  # For sale-specific payments
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, transfer, card
    payment_type = Column(
        Enum(PaymentType), nullable=False, default=PaymentType.PAYMENT
    )  # payment, advance_payment, refund
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Receipt info
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)

    # Audit
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    voided = Column(Boolean, default=False)
    void_reason = Column(Text, nullable=True)
    voided_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    voided_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", backref="payments")
    received_by = relationship("User", foreign_keys=[received_by_id])
    voided_by = relationship("User", foreign_keys=[voided_by_id])

    # Indexes for performance
    __table_args__ = (
        Index("idx_payment_customer", "customer_id", "voided"),
        Index("idx_payment_date", "created_at", "voided"),
    )

    def __repr__(self):
        """String representation of Payment."""
        return f"<Payment {self.receipt_number} - ${self.amount}>"

    @property
    def formatted_amount(self):
        """Return formatted amount display."""
        return f"${self.amount:,.2f}"

    @property
    def is_valid(self):
        """Check if payment is valid (not voided)."""
        return not self.voided

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "receipt_number": self.receipt_number,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else None,
            "sale_id": self.sale_id,
            "amount": float(self.amount),
            "payment_method": self.payment_method,
            "payment_type": self.payment_type.value if self.payment_type else "payment",
            "reference_number": self.reference_number,
            "notes": self.notes,
            "received_by": self.received_by.full_name if self.received_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "voided": self.voided,
            "void_reason": self.void_reason,
            "voided_by": self.voided_by.full_name if self.voided_by else None,
            "voided_at": self.voided_at.isoformat() if self.voided_at else None,
        }
