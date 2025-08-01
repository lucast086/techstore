"""Repair and related models for repair management."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DECIMAL,
    Boolean,
    Date,
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
    from app.models.user import User


class Repair(BaseModel):
    """Repair model for storing device repair orders.

    Attributes:
        repair_number: Unique repair order identifier.
        customer_id: Customer ID (required).
        device_type: Type of device (phone, laptop, tablet, etc).
        device_brand: Brand of the device.
        device_model: Model of the device.
        serial_number: Device serial number if available.
        problem_description: Description of the problem.
        device_condition: Physical condition notes.
        accessories_received: List of accessories received.
        status: Current repair status.
        diagnosis_notes: Technician's diagnosis notes.
        repair_notes: Notes about the repair work done.
        estimated_cost: Estimated repair cost.
        final_cost: Final cost after repair.
        labor_cost: Cost of labor.
        parts_cost: Cost of parts used.
        received_date: When repair was received.
        estimated_completion: Estimated completion date.
        completed_date: Actual completion timestamp.
        delivered_date: When device was delivered.
        warranty_days: Warranty period in days.
        warranty_expires: Warranty expiration date.
        assigned_technician: ID of assigned technician.
        received_by: ID of user who received the repair.
        delivered_by: ID of user who delivered the device.
        is_express: Whether this is an express/session repair.
        customer_approved: Whether customer approved the repair.
        approval_date: When customer approved.
    """

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique repair ID",
    )

    # Unique repair number
    repair_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique repair order number",
    )

    # Customer relationship
    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Customer ID",
    )

    # Device information
    device_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of device (phone, laptop, etc)",
    )
    device_brand: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Device brand",
    )
    device_model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Device model",
    )
    serial_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Device serial number",
    )

    # Problem and condition
    problem_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Description of the problem",
    )
    device_condition: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Physical condition notes",
    )
    accessories_received: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="List of accessories received",
    )

    # Status and workflow
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="received",
        index=True,
        comment="Current repair status",
    )
    diagnosis_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Technician's diagnosis",
    )
    repair_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Notes about repair work",
    )

    # Cost tracking
    estimated_cost: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Estimated repair cost",
    )
    final_cost: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Final repair cost",
    )
    labor_cost: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Labor cost component",
    )
    parts_cost: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
        comment="Parts cost component",
    )

    # Dates and timestamps
    received_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="When repair was received",
    )
    estimated_completion: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Estimated completion date",
    )
    completed_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Actual completion timestamp",
    )
    delivered_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When device was delivered",
    )

    # Warranty
    warranty_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
        comment="Warranty period in days",
    )
    warranty_expires: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Warranty expiration date",
    )

    # User relationships
    assigned_technician: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Assigned technician ID",
    )
    received_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who received the repair",
    )
    delivered_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who delivered the device",
    )

    # Flags
    is_express: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Express/session repair flag",
    )
    customer_approved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Customer approval flag",
    )
    approval_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When customer approved",
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="repairs",
        lazy="joined",
    )
    technician: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_technician],
        lazy="select",
    )
    receiver: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[received_by],
        lazy="select",
    )
    deliverer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[delivered_by],
        lazy="select",
    )
    status_history: Mapped[list["RepairStatusHistory"]] = relationship(
        "RepairStatusHistory",
        back_populates="repair",
        cascade="all, delete-orphan",
        lazy="select",
    )
    parts: Mapped[list["RepairPart"]] = relationship(
        "RepairPart",
        back_populates="repair",
        cascade="all, delete-orphan",
        lazy="select",
    )
    photos: Mapped[list["RepairPhoto"]] = relationship(
        "RepairPhoto",
        back_populates="repair",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        """String representation of repair."""
        return f"<Repair(number={self.repair_number}, device={self.device_brand} {self.device_model})>"


class RepairStatusHistory(BaseModel):
    """Model for tracking repair status changes."""

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique status history ID",
    )

    # Foreign keys
    repair_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("repairs.id", ondelete="CASCADE"),
        nullable=False,
        comment="Related repair ID",
    )
    changed_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who changed status",
    )

    # Status information
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Status value",
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Status change notes",
    )

    # Relationships
    repair: Mapped["Repair"] = relationship(
        "Repair",
        back_populates="status_history",
    )
    user: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="select",
    )


class RepairPart(BaseModel):
    """Model for tracking parts used in repairs."""

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique part usage ID",
    )

    # Foreign key
    repair_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("repairs.id", ondelete="CASCADE"),
        nullable=False,
        comment="Related repair ID",
    )

    # Part information
    part_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Part name/description",
    )
    part_cost: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Cost of the part",
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Quantity used",
    )
    supplier: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Part supplier",
    )

    # Relationships
    repair: Mapped["Repair"] = relationship(
        "Repair",
        back_populates="parts",
    )


class RepairPhoto(BaseModel):
    """Model for storing repair-related photos."""

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique photo ID",
    )

    # Foreign keys
    repair_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("repairs.id", ondelete="CASCADE"),
        nullable=False,
        comment="Related repair ID",
    )
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who uploaded photo",
    )

    # Photo information
    photo_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Photo URL/path",
    )
    photo_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Photo type (before/during/after)",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Photo description",
    )

    # Relationships
    repair: Mapped["Repair"] = relationship(
        "Repair",
        back_populates="photos",
    )
    user: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="select",
    )


# Create indexes
Index("idx_repairs_customer", Repair.customer_id)
Index("idx_repairs_status", Repair.status)
Index("idx_repairs_number", Repair.repair_number)
Index("idx_repairs_received", Repair.received_date)
Index("idx_repair_status_history_repair", RepairStatusHistory.repair_id)
