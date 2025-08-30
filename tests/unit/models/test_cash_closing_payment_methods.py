"""Tests for cash closing payment method breakdown."""

from datetime import date
from decimal import Decimal

from app.models.cash_closing import CashClosing


class TestCashClosingPaymentMethods:
    """Test payment method breakdown in cash closing."""

    def test_cash_closing_has_payment_method_fields(self):
        """Test that cash closing model has payment method breakdown fields."""
        closing = CashClosing()

        # Sales by payment method
        assert hasattr(closing, "sales_cash")
        assert hasattr(closing, "sales_credit")
        assert hasattr(closing, "sales_transfer")
        assert hasattr(closing, "sales_mixed")

        # Expenses by payment method
        assert hasattr(closing, "expenses_cash")
        assert hasattr(closing, "expenses_transfer")
        assert hasattr(closing, "expenses_card")

    def test_payment_method_defaults(self):
        """Test that payment method fields have proper defaults."""
        # When created with explicit defaults
        closing = CashClosing(
            closing_date=date.today(),
            opening_balance=Decimal("100.00"),
            sales_total=Decimal("0.00"),
            expenses_total=Decimal("0.00"),
            cash_count=Decimal("100.00"),
            expected_cash=Decimal("100.00"),
            cash_difference=Decimal("0.00"),
            sales_cash=Decimal("0.00"),
            sales_credit=Decimal("0.00"),
            sales_transfer=Decimal("0.00"),
            sales_mixed=Decimal("0.00"),
            expenses_cash=Decimal("0.00"),
            expenses_transfer=Decimal("0.00"),
            expenses_card=Decimal("0.00"),
            closed_by=1,
        )

        # All should be 0.00
        assert closing.sales_cash == Decimal("0.00")
        assert closing.sales_credit == Decimal("0.00")
        assert closing.sales_transfer == Decimal("0.00")
        assert closing.sales_mixed == Decimal("0.00")
        assert closing.expenses_cash == Decimal("0.00")
        assert closing.expenses_transfer == Decimal("0.00")
        assert closing.expenses_card == Decimal("0.00")

    def test_total_calculations_with_payment_methods(self):
        """Test that totals are correctly calculated from payment method breakdowns."""
        closing = CashClosing(
            closing_date=date.today(),
            opening_balance=Decimal("100.00"),
            sales_cash=Decimal("500.00"),
            sales_credit=Decimal("300.00"),
            sales_transfer=Decimal("200.00"),
            sales_mixed=Decimal("100.00"),
            expenses_cash=Decimal("50.00"),
            expenses_transfer=Decimal("30.00"),
            expenses_card=Decimal("20.00"),
            cash_count=Decimal("550.00"),
            closed_by=1,
        )

        # Calculate totals from payment methods
        expected_sales = Decimal("1100.00")  # 500 + 300 + 200 + 100
        expected_expenses = Decimal("100.00")  # 50 + 30 + 20

        assert closing.calculate_sales_total() == expected_sales
        assert closing.calculate_expenses_total() == expected_expenses

    def test_cash_calculation_only_includes_cash_transactions(self):
        """Test that expected cash calculation only includes cash transactions."""
        closing = CashClosing(
            closing_date=date.today(),
            opening_balance=Decimal("100.00"),
            sales_cash=Decimal("500.00"),
            sales_credit=Decimal("300.00"),  # Should not affect cash
            sales_transfer=Decimal("200.00"),  # Should not affect cash
            expenses_cash=Decimal("50.00"),
            expenses_transfer=Decimal("30.00"),  # Should not affect cash
            expenses_card=Decimal("20.00"),  # Should not affect cash
            cash_count=Decimal("550.00"),
            closed_by=1,
        )

        # Expected cash = opening + cash sales - cash expenses
        expected_cash = Decimal("100.00") + Decimal("500.00") - Decimal("50.00")
        assert closing.calculate_expected_cash_amount() == expected_cash
