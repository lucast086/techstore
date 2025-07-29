"""Customer model for TechStore SaaS."""

from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Customer(BaseModel):
    """Customer model for storing customer information.

    Attributes:
        name: Customer's full name.
        phone: Primary phone number (required).
        phone_secondary: Secondary phone number (optional).
        email: Customer's email address (optional).
        address: Customer's physical address (optional).
        notes: Additional notes about the customer (optional).
        is_active: Whether the customer is active (soft delete).
        created_by_id: ID of user who created this customer.
        created_by: Relationship to User who created this customer.
    """

    __tablename__ = "customers"

    # Primary key is inherited from BaseModel
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    phone_secondary = Column(String(20), nullable=True, index=True)
    email = Column(String(100), nullable=True, index=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", backref="created_customers")

    # Indexes for search performance
    __table_args__ = (
        Index("idx_customer_search", "name", "phone", "phone_secondary"),
        Index("idx_customer_active_name", "is_active", "name"),
    )

    def __repr__(self):
        """String representation of Customer."""
        return f"<Customer {self.name} - {self.phone}>"

    @property
    def display_phones(self):
        """Return formatted phone display."""
        phones = [self.phone]
        if self.phone_secondary:
            phones.append(self.phone_secondary)
        return " / ".join(phones)

    @property
    def search_string(self):
        """Concatenated string for search optimization."""
        parts = [self.name, self.phone]
        if self.phone_secondary:
            parts.append(self.phone_secondary)
        if self.email:
            parts.append(self.email)
        return " ".join(parts).lower()

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "phone_secondary": self.phone_secondary,
            "email": self.email,
            "address": self.address,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by.full_name if self.created_by else None,
        }
