"""Service for managing system configurations."""

import logging
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.system_config import SystemConfig

logger = logging.getLogger(__name__)


class ConfigService:
    """Service for managing system configurations."""

    def get_config(self, db: Session, key: str) -> Optional[Any]:
        """Get a configuration value by key.

        Args:
            db: Database session
            key: Configuration key

        Returns:
            The configuration value converted to its proper type, or None if not found
        """
        config = (
            db.query(SystemConfig)
            .filter(SystemConfig.key == key, SystemConfig.is_active.is_(True))
            .first()
        )

        if config:
            return config.get_value()
        return None

    def get_config_or_default(self, db: Session, key: str, default: Any) -> Any:
        """Get a configuration value or return a default if not found.

        Args:
            db: Database session
            key: Configuration key
            default: Default value to return if config not found

        Returns:
            The configuration value or the default
        """
        value = self.get_config(db, key)
        return value if value is not None else default

    def set_config(
        self,
        db: Session,
        key: str,
        value: Any,
        value_type: str = "string",
        description: str = None,
        category: str = None,
    ) -> SystemConfig:
        """Set or update a configuration value.

        Args:
            db: Database session
            key: Configuration key
            value: Configuration value
            value_type: Type of the value (string, decimal, integer, boolean)
            description: Optional description
            category: Optional category

        Returns:
            The created or updated configuration
        """
        # Convert value to string for storage
        str_value = str(value)

        # Check if config exists
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()

        if config:
            # Update existing
            config.value = str_value
            config.value_type = value_type
            if description:
                config.description = description
            if category:
                config.category = category
            config.is_active = True
            logger.info(f"Updated config {key} = {str_value}")
        else:
            # Create new
            config = SystemConfig(
                key=key,
                value=str_value,
                value_type=value_type,
                description=description,
                category=category,
                is_active=True,
            )
            db.add(config)
            logger.info(f"Created config {key} = {str_value}")

        db.commit()
        db.refresh(config)
        return config

    def get_default_opening_balance(self, db: Session) -> Decimal:
        """Get the default opening balance for cash register.

        Args:
            db: Database session

        Returns:
            The default opening balance, defaults to 10000.00 if not configured
        """
        return self.get_config_or_default(
            db, "default_opening_balance", Decimal("10000.00")
        )

    def get_cash_difference_threshold(self, db: Session) -> Decimal:
        """Get the cash difference threshold for validations.

        Args:
            db: Database session

        Returns:
            The threshold amount, defaults to 100.00 if not configured
        """
        return self.get_config_or_default(
            db, "cash_difference_threshold", Decimal("100.00")
        )

    def get_all_configs(self, db: Session, category: str = None) -> list[SystemConfig]:
        """Get all active configurations, optionally filtered by category.

        Args:
            db: Database session
            category: Optional category filter

        Returns:
            List of active configurations
        """
        query = db.query(SystemConfig).filter(SystemConfig.is_active.is_(True))

        if category:
            query = query.filter(SystemConfig.category == category)

        return query.order_by(SystemConfig.category, SystemConfig.key).all()


# Create singleton instance
config_service = ConfigService()
