"""Test balance calculation fix for proper debt tracking."""

from decimal import Decimal
from unittest.mock import Mock

import pytest
from app.services.balance_service import balance_service


class TestBalanceCalculationFix:
    """Test that balance is correctly calculated as Payments - Sales."""

    def test_balance_with_full_payment(self):
        """Test balance when sale is fully paid."""
        db_mock = Mock()

        # Mock total sales = $100
        sales_query = Mock()
        sales_query.filter.return_value.scalar.return_value = Decimal("100.00")

        # Mock total payments = $100
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.balance_service.payment_crud.get_customer_payment_total",
                lambda db, customer_id: Decimal("100.00"),
            )

            # Mock the sales query
            db_mock.query.return_value = sales_query

            balance = balance_service.calculate_balance(db_mock, 1)

            # Balance should be 0 (100 payments - 100 sales)
            assert balance == Decimal("0.00")

    def test_balance_with_partial_payment(self):
        """Test balance when sale is partially paid."""
        db_mock = Mock()

        # Mock total sales = $100
        sales_query = Mock()
        sales_query.filter.return_value.scalar.return_value = Decimal("100.00")

        # Mock total payments = $60
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.balance_service.payment_crud.get_customer_payment_total",
                lambda db, customer_id: Decimal("60.00"),
            )

            # Mock the sales query
            db_mock.query.return_value = sales_query

            balance = balance_service.calculate_balance(db_mock, 1)

            # Balance should be -40 (60 payments - 100 sales = customer owes $40)
            assert balance == Decimal("-40.00")

    def test_balance_with_no_payment(self):
        """Test balance when sale has no payment."""
        db_mock = Mock()

        # Mock total sales = $100
        sales_query = Mock()
        sales_query.filter.return_value.scalar.return_value = Decimal("100.00")

        # Mock total payments = $0
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.balance_service.payment_crud.get_customer_payment_total",
                lambda db, customer_id: Decimal("0.00"),
            )

            # Mock the sales query
            db_mock.query.return_value = sales_query

            balance = balance_service.calculate_balance(db_mock, 1)

            # Balance should be -100 (0 payments - 100 sales = customer owes $100)
            assert balance == Decimal("-100.00")

    def test_balance_with_multiple_sales_and_payments(self):
        """Test balance with multiple sales and payments."""
        db_mock = Mock()

        # Mock total sales = $500 (e.g., 3 sales: $200, $150, $150)
        sales_query = Mock()
        sales_query.filter.return_value.scalar.return_value = Decimal("500.00")

        # Mock total payments = $350 (e.g., various partial payments)
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.balance_service.payment_crud.get_customer_payment_total",
                lambda db, customer_id: Decimal("350.00"),
            )

            # Mock the sales query
            db_mock.query.return_value = sales_query

            balance = balance_service.calculate_balance(db_mock, 1)

            # Balance should be -150 (350 payments - 500 sales = customer owes $150)
            assert balance == Decimal("-150.00")

    def test_balance_with_overpayment(self):
        """Test balance when customer has paid more than sales (has credit)."""
        db_mock = Mock()

        # Mock total sales = $100
        sales_query = Mock()
        sales_query.filter.return_value.scalar.return_value = Decimal("100.00")

        # Mock total payments = $150 (customer paid extra)
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.balance_service.payment_crud.get_customer_payment_total",
                lambda db, customer_id: Decimal("150.00"),
            )

            # Mock the sales query
            db_mock.query.return_value = sales_query

            balance = balance_service.calculate_balance(db_mock, 1)

            # Balance should be 50 (150 payments - 100 sales = customer has $50 credit)
            assert balance == Decimal("50.00")

    def test_balance_excludes_voided_sales(self):
        """Test that voided sales are not included in balance calculation."""
        db_mock = Mock()

        # The query should filter out voided sales
        sales_query = Mock()
        filter_mock = Mock()
        filter_mock.scalar.return_value = Decimal("100.00")  # Only non-voided sales
        sales_query.filter.return_value = filter_mock

        # Mock total payments = $100
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "app.services.balance_service.payment_crud.get_customer_payment_total",
                lambda db, customer_id: Decimal("100.00"),
            )

            # Mock the sales query
            db_mock.query.return_value = sales_query

            balance = balance_service.calculate_balance(db_mock, 1)

            # Verify that is_voided filter was applied
            sales_query.filter.assert_called()

            # Balance should be 0 (only counting non-voided sales)
            assert balance == Decimal("0.00")
