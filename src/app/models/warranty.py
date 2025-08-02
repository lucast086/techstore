"""SQLAlchemy models for repair warranty management."""

from datetime import date
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class WarrantyStatus(str, PyEnum):
    """Valid warranty status values."""

    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"
    VOIDED = "voided"


class CoverageType(str, PyEnum):
    """Types of warranty coverage."""

    FULL = "full"
    PARTS_ONLY = "parts_only"
    LABOR_ONLY = "labor_only"
    LIMITED = "limited"


class Warranty(BaseModel):
    """Model for repair warranties."""

    __tablename__ = "warranties"

    id = Column(Integer, primary_key=True)
    repair_id = Column(
        Integer, ForeignKey("repairs.id", ondelete="CASCADE"), nullable=False
    )
    warranty_number = Column(String(20), unique=True, nullable=False, index=True)

    # Coverage details
    coverage_type = Column(
        Enum(CoverageType), default=CoverageType.FULL, nullable=False
    )
    parts_warranty_days = Column(Integer, default=90, nullable=False)
    labor_warranty_days = Column(Integer, default=30, nullable=False)

    # Dates
    start_date = Column(Date, nullable=False)
    parts_expiry_date = Column(Date, nullable=False)
    labor_expiry_date = Column(Date, nullable=False)

    # Status
    status = Column(Enum(WarrantyStatus), default=WarrantyStatus.ACTIVE, nullable=False)
    void_reason = Column(Text)
    voided_at = Column(DateTime)
    voided_by = Column(Integer, ForeignKey("users.id"))

    # Terms and conditions
    terms = Column(Text)
    exclusions = Column(Text)

    # Relationships
    repair = relationship("Repair", back_populates="warranty")
    claims = relationship(
        "WarrantyClaim", back_populates="warranty", cascade="all, delete-orphan"
    )
    voided_by_user = relationship("User", foreign_keys=[voided_by])

    def is_parts_valid(self, check_date: date = None) -> bool:
        """Check if parts warranty is still valid."""
        if self.status != WarrantyStatus.ACTIVE:
            return False
        check_date = check_date or date.today()
        return check_date <= self.parts_expiry_date

    def is_labor_valid(self, check_date: date = None) -> bool:
        """Check if labor warranty is still valid."""
        if self.status != WarrantyStatus.ACTIVE:
            return False
        check_date = check_date or date.today()
        return check_date <= self.labor_expiry_date

    def is_valid(self, check_date: date = None) -> bool:
        """Check if any warranty coverage is still valid."""
        return self.is_parts_valid(check_date) or self.is_labor_valid(check_date)


class WarrantyClaim(BaseModel):
    """Model for warranty claims."""

    __tablename__ = "warranty_claims"

    id = Column(Integer, primary_key=True)
    warranty_id = Column(
        Integer, ForeignKey("warranties.id", ondelete="CASCADE"), nullable=False
    )
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False)
    claim_number = Column(String(20), unique=True, nullable=False, index=True)

    # Claim details
    claim_date = Column(Date, nullable=False)
    issue_description = Column(Text, nullable=False)
    resolution_notes = Column(Text)

    # Coverage used
    parts_covered = Column(Boolean, default=False)
    labor_covered = Column(Boolean, default=False)

    # Status
    approved = Column(Boolean, default=True)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)

    # Relationships
    warranty = relationship("Warranty", back_populates="claims")
    repair = relationship("Repair", foreign_keys=[repair_id])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
