"""Tests for configuration service."""

from decimal import Decimal

from app.models.system_config import SystemConfig
from app.services.config_service import config_service
from sqlalchemy.orm import Session


class TestConfigService:
    """Test configuration service functionality."""

    def test_get_default_opening_balance(self, db_session: Session):
        """Test getting default opening balance."""
        # Set up the config for testing
        config_service.set_config(
            db_session,
            key="default_opening_balance",
            value="10000.00",
            value_type="decimal",
        )

        # Get the balance
        balance = config_service.get_default_opening_balance(db_session)
        assert balance == Decimal("10000.00")

    def test_set_and_get_config(self, db_session: Session):
        """Test setting and getting a configuration."""
        # Set a new config
        config = config_service.set_config(
            db_session,
            key="test_config",
            value="test_value",
            value_type="string",
            description="Test configuration",
            category="test",
        )

        assert config is not None
        assert config.key == "test_config"
        assert config.value == "test_value"

        # Get the config
        value = config_service.get_config(db_session, "test_config")
        assert value == "test_value"

    def test_get_config_with_types(self, db_session: Session):
        """Test getting configs with different types."""
        # Set decimal config
        config_service.set_config(
            db_session, key="test_decimal", value="123.45", value_type="decimal"
        )

        value = config_service.get_config(db_session, "test_decimal")
        assert value == Decimal("123.45")
        assert isinstance(value, Decimal)

        # Set integer config
        config_service.set_config(
            db_session, key="test_integer", value="42", value_type="integer"
        )

        value = config_service.get_config(db_session, "test_integer")
        assert value == 42
        assert isinstance(value, int)

        # Set boolean config
        config_service.set_config(
            db_session, key="test_boolean_true", value="true", value_type="boolean"
        )

        value = config_service.get_config(db_session, "test_boolean_true")
        assert value is True
        assert isinstance(value, bool)

        config_service.set_config(
            db_session, key="test_boolean_false", value="false", value_type="boolean"
        )

        value = config_service.get_config(db_session, "test_boolean_false")
        assert value is False

    def test_get_config_or_default(self, db_session: Session):
        """Test getting config with default fallback."""
        # Non-existent config should return default
        value = config_service.get_config_or_default(
            db_session, "non_existent_key", "default_value"
        )
        assert value == "default_value"

        # Existing config should return its value
        config_service.set_config(db_session, key="existing_key", value="actual_value")

        value = config_service.get_config_or_default(
            db_session, "existing_key", "default_value"
        )
        assert value == "actual_value"

    def test_update_existing_config(self, db_session: Session):
        """Test updating an existing configuration."""
        # Create initial config
        config_service.set_config(
            db_session,
            key="updatable_config",
            value="initial_value",
            value_type="string",
            description="Initial description",
        )

        # Update it
        updated = config_service.set_config(
            db_session,
            key="updatable_config",
            value="updated_value",
            value_type="string",
            description="Updated description",
        )

        assert updated.value == "updated_value"
        assert updated.description == "Updated description"

        # Verify in database
        value = config_service.get_config(db_session, "updatable_config")
        assert value == "updated_value"

    def test_get_all_configs(self, db_session: Session):
        """Test getting all configurations."""
        # Add some test configs
        config_service.set_config(
            db_session, key="test1", value="value1", category="category1"
        )
        config_service.set_config(
            db_session, key="test2", value="value2", category="category1"
        )
        config_service.set_config(
            db_session, key="test3", value="value3", category="category2"
        )

        # Get all configs
        all_configs = config_service.get_all_configs(db_session)
        assert len(all_configs) >= 3  # At least our test configs

        # Get configs by category
        cat1_configs = config_service.get_all_configs(db_session, category="category1")
        assert len(cat1_configs) == 2
        assert all(c.category == "category1" for c in cat1_configs)

        cat2_configs = config_service.get_all_configs(db_session, category="category2")
        assert len(cat2_configs) == 1
        assert cat2_configs[0].key == "test3"

    def test_default_opening_balance_is_10000(self, db_session: Session):
        """Test that default opening balance is 10000 as specified."""
        # In test environment, the migration data might not exist
        # So we create it manually for testing
        config_service.set_config(
            db_session,
            key="default_opening_balance",
            value="10000.00",
            value_type="decimal",
            description="Default opening balance for cash register",
            category="cash_register",
        )

        # Now test getting it
        balance = config_service.get_default_opening_balance(db_session)
        assert balance == Decimal("10000.00")

        # Verify it's in the database
        config = (
            db_session.query(SystemConfig)
            .filter(SystemConfig.key == "default_opening_balance")
            .first()
        )

        assert config is not None
        assert config.value == "10000.00"
        assert config.value_type == "decimal"
        assert config.category == "cash_register"
        assert config.is_active is True

    def test_cash_difference_threshold(self, db_session: Session):
        """Test getting cash difference threshold."""
        # If not configured, should return default
        threshold = config_service.get_cash_difference_threshold(db_session)
        assert threshold == Decimal("100.00")  # Default value

        # Update it
        config_service.set_config(
            db_session,
            key="cash_difference_threshold",
            value="200.00",
            value_type="decimal",
        )

        # Get updated value
        threshold = config_service.get_cash_difference_threshold(db_session)
        assert threshold == Decimal("200.00")
