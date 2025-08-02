"""Cash closing models for daily financial management."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DECIMAL,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class CashClosing(BaseModel):
    """Model for daily cash register closings.

    Attributes:
        closing_date: Date of the closing (unique per day).
        opening_balance: Cash balance at start of day.
        sales_total: Total sales amount for the day.
        expenses_total: Total expenses for the day.
        cash_count: Actual cash counted at closing.
        expected_cash: Calculated expected cash balance.
        cash_difference: Difference between expected and actual.
        notes: Optional closing notes or observations.
        closed_by: ID of user who performed the closing.
        closed_at: Timestamp when closing was performed.
        is_finalized: Whether closing is finalized (immutable).
        user: Relationship to user who closed.
    """

    __tablename__ = "cash_closings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    closing_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="Date of the closing"
    )
    opening_balance: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="Opening cash balance"
    )
    sales_total: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="Total sales for the day"
    )
    expenses_total: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Total expenses",
    )
    cash_count: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="Actual cash counted"
    )
    expected_cash: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="Expected cash balance"
    )
    cash_difference: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, comment="Difference (actual - expected)"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Closing notes or observations"
    )
    opened_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="When cash register was opened"
    )
    opened_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, comment="User who opened"
    )
    closed_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="User who closed"
    )
    closed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        comment="Closing time",
    )
    is_finalized: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether closing is final"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", backref="cash_closings", lazy="joined")

    # Constraints
    __table_args__ = (UniqueConstraint("closing_date", name="uq_cash_closing_date"),)

    def __repr__(self) -> str:
        """String representation of CashClosing."""
        return f"<CashClosing {self.closing_date}: ${self.cash_count}>"

    @property
    def is_balanced(self) -> bool:
        """Check if cash count matches expected amount within tolerance."""
        tolerance = Decimal("1.00")  # $1 tolerance
        return abs(self.cash_difference) <= tolerance

    @property
    def status(self) -> str:
        """Get closing status as string."""
        if self.is_finalized:
            return "Finalized"
        return "Draft"

    def calculate_expected_cash(self) -> Decimal:
        """Calculate expected cash balance."""
        return self.opening_balance + self.sales_total - self.expenses_total

    def calculate_difference(self) -> Decimal:
        """Calculate cash difference (actual - expected)."""
        return self.cash_count - self.expected_cash
