"""Tests for debt service."""

from decimal import Decimal
from unittest.mock import Mock

import pytest
from app.services.debt_service import debt_service


class TestDebtService:
    """Test debt service functionality."""

    def test_calculate_customer_total_debt_no_debt(self):
        """Test calculating debt when customer has no debt."""
        # Mock database and balance service
        db_mock = Mock()

        # Mock balance service to return positive balance (customer has credit)
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.debt_service.balance_service.calculate_balance",
                lambda db, customer_id: Decimal("50.00"),
            )

            result = debt_service.calculate_customer_total_debt(db_mock, 1)
            assert result == Decimal("0")

    def test_calculate_customer_total_debt_with_debt(self):
        """Test calculating debt when customer owes money."""
        # Mock database and balance service
        db_mock = Mock()

        # Mock balance service to return negative balance (customer owes money)
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.debt_service.balance_service.calculate_balance",
                lambda db, customer_id: Decimal("-75.00"),
            )

            result = debt_service.calculate_customer_total_debt(db_mock, 1)
            assert result == Decimal("75.00")

    def test_validate_partial_payment_valid(self):
        """Test validation of valid partial payment."""
        result = debt_service.validate_partial_payment(
            amount_paid=Decimal("50.00"),
            total_amount=Decimal("100.00"),
            payment_method="cash",
        )
        assert result == (True, "")

    def test_validate_partial_payment_none(self):
        """Test validation when amount_paid is None."""
        result = debt_service.validate_partial_payment(
            amount_paid=None, total_amount=Decimal("100.00"), payment_method="cash"
        )
        assert result == (True, "")

    def test_validate_partial_payment_negative(self):
        """Test validation of negative amount paid."""
        result = debt_service.validate_partial_payment(
            amount_paid=Decimal("-10.00"),
            total_amount=Decimal("100.00"),
            payment_method="cash",
        )
        assert result[0] is False
        assert "cannot be negative" in result[1]

    def test_validate_partial_payment_exceeds_total(self):
        """Test validation when amount paid exceeds total."""
        result = debt_service.validate_partial_payment(
            amount_paid=Decimal("150.00"),
            total_amount=Decimal("100.00"),
            payment_method="cash",
        )
        assert result[0] is False
        assert "cannot exceed total amount" in result[1]

    def test_get_debt_notification_message(self):
        """Test debt notification message generation."""
        # Mock database query
        db_mock = Mock()
        customer_mock = Mock()
        customer_mock.name = "John Doe"

        query_mock = Mock()
        query_mock.filter.return_value.first.return_value = customer_mock
        db_mock.query.return_value = query_mock

        # Mock total debt calculation
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.debt_service.debt_service.calculate_customer_total_debt",
                lambda db, customer_id: Decimal("125.00"),
            )

            message = debt_service.get_debt_notification_message(
                db_mock, 1, Decimal("50.00")
            )

            assert "Debt of $50.00 generated for John Doe" in message
            assert "Total customer debt: $125.00" in message
