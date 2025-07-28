"""Base model class for TechStore SaaS."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    # Generate table names automatically from class names
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name (lowercase, plural)."""
        return cls.__name__.lower() + "s"


class TimestampMixin:
    """Mixin to add timestamp fields to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp",
    )


class BaseModel(Base, TimestampMixin):
    """
    Base model class with common fields and functionality.

    Provides:
    - Auto-generated table names
    - Created/updated timestamp tracking
    - Common utility methods
    - Consistent model structure

    All business models should inherit from this class.
    """

    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """String representation of model instance."""
        class_name = self.__class__.__name__
        if hasattr(self, "id"):
            return f"<{class_name}(id={self.id})>"
        return f"<{class_name}()>"
