"""Expense related models."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ExpenseCategory(Base):
    """Model for expense categories."""

    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates="category"
    )


class Expense(Base):
    """Model for business expenses."""

    __tablename__ = "expenses"
    __table_args__ = (
        Index("ix_expenses_expense_date", "expense_date"),
        Index("ix_expenses_category_id", "category_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("expense_categories.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    payment_method: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # cash, transfer, card
    receipt_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    supplier_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    receipt_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    is_editable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    category: Mapped["ExpenseCategory"] = relationship(
        "ExpenseCategory", back_populates="expenses"
    )
    user: Mapped["User"] = relationship("User", back_populates="expenses")
