"""Supplier model for product suppliers."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import ProductSupplier


class Supplier(BaseModel):
    """Supplier model for managing product suppliers.

    Attributes:
        name: Supplier company name.
        contact_name: Contact person name.
        email: Contact email address.
        phone: Contact phone number.
        address: Supplier address.
        is_active: Whether supplier is active.
        products: Products supplied by this supplier.
    """

    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    contact_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    products: Mapped[list["ProductSupplier"]] = relationship(
        "ProductSupplier", backref="supplier"
    )

    def __repr__(self) -> str:
        """String representation of Supplier."""
        return f"<Supplier {self.name}>"
