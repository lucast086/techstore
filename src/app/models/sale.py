"""Sale and related models for sales management."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DECIMAL,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.payment import Payment
    from app.models.product import Product
    from app.models.user import User


class Sale(BaseModel):
    """Sale model for storing sales transactions.

    Attributes:
        invoice_number: Unique invoice identifier.
        customer_id: Optional customer ID (null for walk-in).
        user_id: ID of user who processed the sale.
        sale_date: Date and time of sale.
        subtotal: Total before discounts and taxes.
        discount_amount: Total discount applied.
        tax_amount: Total tax amount.
        total_amount: Final amount to pay.
        payment_status: Status (pending, partial, paid).
        payment_method: Method used (cash, credit, transfer, mixed).
        notes: Optional sale notes.
        is_voided: Whether sale was voided.
        void_reason: Reason for voiding if applicable.
        customer: Related customer (if any).
        user: User who processed the sale.
        items: List of sale items.
        payments: List of payments for this sale.
    """

    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    sale_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), index=True
    )
    subtotal: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal("0.00")
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal("0.00")
    )
    total_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal("0.00")
    )  # Total amount paid so far
    change_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal("0.00")
    )  # Change given if overpayment
    payment_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending, partial, paid
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # cash, credit, transfer, mixed
    # Mixed payment components (only used when payment_method is "mixed")
    cash_amount: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True, default=None
    )
    transfer_amount: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True, default=None
    )
    card_amount: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True, default=None
    )
    credit_amount: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True, default=None
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_voided: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    void_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer", backref="sales", lazy="joined"
    )
    user: Mapped["User"] = relationship("User", backref="sales", lazy="joined")
    items: Mapped[list["SaleItem"]] = relationship(
        "SaleItem",
        back_populates="sale",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", backref="sale", foreign_keys="Payment.sale_id"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_sale_date_status", "sale_date", "payment_status"),
        Index("idx_sale_customer_date", "customer_id", "sale_date"),
    )

    def __repr__(self) -> str:
        """String representation of Sale."""
        return f"<Sale {self.invoice_number}: ${self.total_amount}>"

    @property
    def is_credit_sale(self) -> bool:
        """Check if this is a credit sale."""
        return self.payment_method == "credit"

    @property
    def amount_paid(self) -> Decimal:
        """Calculate total amount paid."""
        return sum(payment.amount for payment in self.payments)

    @property
    def amount_due(self) -> Decimal:
        """Calculate remaining amount due."""
        return self.total_amount - self.paid_amount

    @property
    def balance_due(self) -> Decimal:
        """Calculate remaining balance due (alias for amount_due)."""
        return self.total_amount - self.paid_amount


class SaleItem(BaseModel):
    """Individual item in a sale transaction.

    Attributes:
        sale_id: ID of parent sale.
        product_id: ID of product sold.
        quantity: Quantity sold.
        unit_price: Price per unit at time of sale.
        discount_percentage: Discount percentage applied.
        discount_amount: Discount amount applied.
        total_price: Final price for this line item.
        sale: Parent sale relationship.
        product: Related product.
    """

    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    discount_percentage: Mapped[Decimal] = mapped_column(
        DECIMAL(5, 2), nullable=False, default=Decimal("0.00")
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, default=Decimal("0.00")
    )
    total_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    is_custom_price: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether custom price was used"
    )

    # Relationships
    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")
    product: Mapped["Product"] = relationship("Product", backref="sale_items")

    def __repr__(self) -> str:
        """String representation of SaleItem."""
        return f"<SaleItem {self.product_id} x{self.quantity}>"

    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal before discounts."""
        return self.unit_price * self.quantity

    @property
    def price_note(self) -> str:
        """Return note about pricing type."""
        return "Custom Price" if self.is_custom_price else ""
