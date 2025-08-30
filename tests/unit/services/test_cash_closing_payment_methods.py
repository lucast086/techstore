"""Tests for cash closing service with payment method breakdown."""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from app.schemas.cash_closing import CashClosingCreate
from app.services.cash_closing_service import CashClosingService


class TestCashClosingServicePaymentMethods:
    """Test cash closing service with payment method breakdown."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = CashClosingService()
        self.db = Mock()

    def test_calculate_payment_method_breakdown(self):
        """Test calculation of payment method breakdown from sales and expenses."""
        # Mock sales by payment method
        mock_sales = [
            Mock(payment_method="cash", total_amount=Decimal("500.00")),
            Mock(payment_method="cash", total_amount=Decimal("100.00")),
            Mock(payment_method="credit", total_amount=Decimal("300.00")),
            Mock(payment_method="transfer", total_amount=Decimal("200.00")),
            Mock(payment_method="mixed", total_amount=Decimal("150.00")),
        ]

        # Mock expenses by payment method
        mock_expenses = [
            Mock(payment_method="cash", amount=Decimal("50.00")),
            Mock(payment_method="transfer", amount=Decimal("30.00")),
            Mock(payment_method="card", amount=Decimal("20.00")),
        ]

        breakdown = self.service.calculate_payment_breakdown(
            self.db, target_date=date.today(), sales=mock_sales, expenses=mock_expenses
        )

        # Verify sales breakdown
        assert breakdown.sales_cash == Decimal("600.00")  # 500 + 100
        assert breakdown.sales_credit == Decimal("300.00")
        assert breakdown.sales_transfer == Decimal("200.00")
        assert breakdown.sales_mixed == Decimal("150.00")

        # Verify expenses breakdown
        assert breakdown.expenses_cash == Decimal("50.00")
        assert breakdown.expenses_transfer == Decimal("30.00")
        assert breakdown.expenses_card == Decimal("20.00")

    def test_create_closing_with_payment_breakdown(self):
        """Test creating a cash closing with payment method breakdown."""
        closing_data = CashClosingCreate(
            closing_date=date.today(),
            opening_balance=Decimal("100.00"),
            sales_total=Decimal("1250.00"),
            sales_cash=Decimal("600.00"),
            sales_credit=Decimal("300.00"),
            sales_transfer=Decimal("200.00"),
            sales_mixed=Decimal("150.00"),
            expenses_total=Decimal("100.00"),
            expenses_cash=Decimal("50.00"),
            expenses_transfer=Decimal("30.00"),
            expenses_card=Decimal("20.00"),
            cash_count=Decimal("650.00"),
            notes="Test closing with payment breakdown",
        )

        with patch("app.crud.cash_closing.cash_closing.create") as mock_create:
            mock_create.return_value = Mock(
                id=1,
                closing_date=closing_data.closing_date,
                sales_cash=closing_data.sales_cash,
                sales_credit=closing_data.sales_credit,
                sales_transfer=closing_data.sales_transfer,
                sales_mixed=closing_data.sales_mixed,
                expenses_cash=closing_data.expenses_cash,
                expenses_transfer=closing_data.expenses_transfer,
                expenses_card=closing_data.expenses_card,
                expected_cash=Decimal("650.00"),
                cash_difference=Decimal("0.00"),
            )

            self.service.create_closing(self.db, closing_data, user_id=1)

            # Verify the create was called with payment breakdown
            mock_create.assert_called_once()
            call_args = mock_create.call_args[1]
            assert call_args["sales_cash"] == Decimal("600.00")
            assert call_args["sales_credit"] == Decimal("300.00")
            assert call_args["expenses_cash"] == Decimal("50.00")

    def test_daily_summary_includes_payment_breakdown(self):
        """Test that daily summary includes payment method breakdown."""
        with patch(
            "app.crud.cash_closing.cash_closing.get_daily_summary_with_breakdown"
        ) as mock_summary:
            mock_summary.return_value = Mock(
                sales_count=10,
                total_sales=Decimal("1250.00"),
                sales_cash=Decimal("600.00"),
                sales_credit=Decimal("300.00"),
                sales_transfer=Decimal("200.00"),
                sales_mixed=Decimal("150.00"),
                expense_count=3,
                total_expenses=Decimal("100.00"),
                expenses_cash=Decimal("50.00"),
                expenses_transfer=Decimal("30.00"),
                expenses_card=Decimal("20.00"),
            )

            summary = self.service.get_daily_summary_with_breakdown(
                self.db, target_date=date.today()
            )

            # Verify payment breakdown is included
            assert summary.sales_cash == Decimal("600.00")
            assert summary.sales_credit == Decimal("300.00")
            assert summary.expenses_cash == Decimal("50.00")
            assert summary.expenses_card == Decimal("20.00")
