"""System configuration model for storing application settings."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SystemConfig(BaseModel):
    """Model for system-wide configuration settings.

    This table stores key-value pairs for system configuration that can be
    modified at runtime without code changes.

    Attributes:
        key: Unique configuration key (e.g., 'default_opening_balance')
        value: Configuration value as string
        value_type: Type of the value (string, decimal, integer, boolean)
        description: Human-readable description of the setting
        is_active: Whether this configuration is currently active
        category: Category for grouping related settings (e.g., 'cash_register', 'sales')
    """

    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique configuration key",
    )
    value: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Configuration value (stored as string)"
    )
    value_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="string",
        comment="Type of value: string, decimal, integer, boolean",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Description of what this configuration does"
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True, comment="Category for grouping settings"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this configuration is active",
    )

    # Add unique constraint on key
    __table_args__ = (UniqueConstraint("key", name="uq_system_config_key"),)

    def __repr__(self) -> str:
        """String representation."""
        return f"<SystemConfig {self.key}={self.value}>"

    def get_value(self):
        """Get the value converted to its proper type."""
        if self.value_type == "decimal":
            return Decimal(self.value)
        elif self.value_type == "integer":
            return int(self.value)
        elif self.value_type == "boolean":
            return self.value.lower() in ("true", "1", "yes", "on")
        else:
            return self.value

    @classmethod
    def get_default_configs(cls) -> list[dict]:
        """Get default system configurations.

        Returns a list of default configurations that should be
        created when the system is first initialized.
        """
        return [
            {
                "key": "default_opening_balance",
                "value": "10000.00",
                "value_type": "decimal",
                "description": "Default opening balance for cash register",
                "category": "cash_register",
                "is_active": True,
            },
            {
                "key": "cash_difference_threshold",
                "value": "100.00",
                "value_type": "decimal",
                "description": "Maximum acceptable cash difference for closing",
                "category": "cash_register",
                "is_active": True,
            },
            {
                "key": "allow_negative_stock",
                "value": "false",
                "value_type": "boolean",
                "description": "Allow selling products with negative stock",
                "category": "inventory",
                "is_active": True,
            },
            {
                "key": "default_tax_rate",
                "value": "0.00",
                "value_type": "decimal",
                "description": "Default tax rate for new products (percentage)",
                "category": "sales",
                "is_active": True,
            },
        ]
