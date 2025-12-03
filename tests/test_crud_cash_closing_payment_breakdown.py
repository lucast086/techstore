"""Tests for cash closing CRUD payment method breakdown.

These tests verify that the cash closing calculation correctly separates
sales and payments by payment method, and calculates expected cash correctly.

TDD Red Phase: These tests should FAIL initially until implementation is complete.
"""

from datetime import date, datetime, time
from decimal import Decimal

import pytest
from app.crud.cash_closing import cash_closing
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.models.expense import Expense, ExpenseCategory
from app.models.payment import Payment, PaymentType
from app.models.sale import Sale
from app.utils.timezone import local_to_utc
from sqlalchemy.orm import Session


class TestGetDailySummarySalesByPaymentMethod:
    """Test that get_daily_summary correctly breaks down sales by payment method."""

    def _create_sale(
        self,
        db: Session,
        user_id: int,
        customer_id: int,
        total: Decimal,
        payment_method: str,
        sale_datetime: datetime,
        cash_amount: Decimal = None,
        transfer_amount: Decimal = None,
        credit_amount: Decimal = None,
    ) -> Sale:
        """Helper to create a sale with specific payment method."""
        import uuid

        invoice_num = f"INV-{sale_datetime.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        sale = Sale(
            invoice_number=invoice_num,
            customer_id=customer_id,
            user_id=user_id,
            subtotal=total,
            total_amount=total,
            paid_amount=total if payment_method != "credit" else Decimal("0.00"),
            payment_method=payment_method,
            payment_status="paid" if payment_method != "credit" else "pending",
            sale_date=sale_datetime,
            cash_amount=cash_amount,
            transfer_amount=transfer_amount,
            credit_amount=credit_amount,
        )
        db.add(sale)
        return sale

    @pytest.fixture
    def test_customer(self, db_session: Session) -> Customer:
        """Create a test customer."""
        customer = Customer(
            name="Test Customer",
            phone="1234567890",
            email="test@example.com",
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        return customer

    def test_sales_cash_only(self, db_session: Session, test_user, test_customer):
        """Test that cash sales are correctly summed in sales_cash."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("300.00"),
            "cash",
            utc_datetime,
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.sales_cash == Decimal(
            "800.00"
        ), f"Expected sales_cash=800.00, got {summary.sales_cash}"
        assert summary.total_sales == Decimal("800.00")

    def test_sales_transfer_only(self, db_session: Session, test_user, test_customer):
        """Test that transfer sales are correctly summed in sales_transfer."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("1000.00"),
            "transfer",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "transfer",
            utc_datetime,
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.sales_transfer == Decimal(
            "1500.00"
        ), f"Expected sales_transfer=1500.00, got {summary.sales_transfer}"
        assert summary.sales_cash == Decimal("0.00")

    def test_sales_credit_only(self, db_session: Session, test_user, test_customer):
        """Test that credit sales are correctly summed in sales_credit."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("2000.00"),
            "credit",
            utc_datetime,
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.sales_credit == Decimal(
            "2000.00"
        ), f"Expected sales_credit=2000.00, got {summary.sales_credit}"
        assert summary.sales_cash == Decimal("0.00")

    def test_sales_mixed_payment(self, db_session: Session, test_user, test_customer):
        """Test that mixed sales track cash and transfer portions separately."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("1000.00"),
            "mixed",
            utc_datetime,
            cash_amount=Decimal("600.00"),
            transfer_amount=Decimal("400.00"),
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.sales_mixed == Decimal(
            "1000.00"
        ), f"Expected sales_mixed=1000.00, got {summary.sales_mixed}"
        assert summary.sales_mixed_cash == Decimal(
            "600.00"
        ), f"Expected sales_mixed_cash=600.00, got {summary.sales_mixed_cash}"
        assert summary.sales_mixed_transfer == Decimal(
            "400.00"
        ), f"Expected sales_mixed_transfer=400.00, got {summary.sales_mixed_transfer}"

    def test_all_payment_methods_combined(
        self, db_session: Session, test_user, test_customer
    ):
        """Test that all payment methods are correctly calculated together."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("1000.00"),
            "transfer",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("2000.00"),
            "credit",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("800.00"),
            "mixed",
            utc_datetime,
            cash_amount=Decimal("500.00"),
            transfer_amount=Decimal("300.00"),
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.sales_cash == Decimal("500.00")
        assert summary.sales_transfer == Decimal("1000.00")
        assert summary.sales_credit == Decimal("2000.00")
        assert summary.sales_mixed == Decimal("800.00")
        assert summary.sales_mixed_cash == Decimal("500.00")
        assert summary.sales_mixed_transfer == Decimal("300.00")
        assert summary.total_sales == Decimal("4300.00")

    def test_voided_sales_excluded(self, db_session: Session, test_user, test_customer):
        """Test that voided sales are not included in payment method breakdown."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )
        voided_sale = self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("1000.00"),
            "cash",
            utc_datetime,
        )
        voided_sale.is_voided = True
        voided_sale.void_reason = "Test void"
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.sales_cash == Decimal(
            "500.00"
        ), "Voided sales should not be included"


class TestGetDailySummaryDebtPayments:
    """Test that get_daily_summary correctly tracks debt payments by payment method."""

    @pytest.fixture
    def customer_with_account(self, db_session: Session, test_user) -> Customer:
        """Create a customer with an account that has debt."""
        customer = Customer(
            name="Debt Customer",
            phone="9876543210",
            email="debt@example.com",
        )
        db_session.add(customer)
        db_session.flush()

        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("1000.00"),
            available_credit=Decimal("0.00"),
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(customer)
        return customer

    def _create_debt_payment(
        self,
        db: Session,
        customer_id: int,
        user_id: int,
        amount: Decimal,
        payment_method: str,
        created_at: datetime,
    ) -> Payment:
        """Helper to create a debt payment."""
        import uuid

        receipt_num = f"REC-{created_at.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        payment = Payment(
            customer_id=customer_id,
            amount=amount,
            payment_method=payment_method,
            payment_type=PaymentType.payment,
            receipt_number=receipt_num,
            received_by_id=user_id,
            voided=False,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        payment.created_at = created_at
        db.commit()
        return payment

    def test_debt_payments_cash(
        self, db_session: Session, test_user, customer_with_account
    ):
        """Test that cash debt payments are correctly summed."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("300.00"),
            "cash",
            utc_datetime,
        )
        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("200.00"),
            "cash",
            utc_datetime,
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.debt_payments_cash == Decimal(
            "500.00"
        ), f"Expected debt_payments_cash=500.00, got {summary.debt_payments_cash}"

    def test_debt_payments_transfer(
        self, db_session: Session, test_user, customer_with_account
    ):
        """Test that transfer debt payments are correctly summed."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("500.00"),
            "transfer",
            utc_datetime,
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert (
            summary.debt_payments_transfer == Decimal("500.00")
        ), f"Expected debt_payments_transfer=500.00, got {summary.debt_payments_transfer}"

    def test_debt_payments_card(
        self, db_session: Session, test_user, customer_with_account
    ):
        """Test that card debt payments are correctly summed."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("750.00"),
            "card",
            utc_datetime,
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.debt_payments_card == Decimal(
            "750.00"
        ), f"Expected debt_payments_card=750.00, got {summary.debt_payments_card}"

    def test_debt_payments_all_methods(
        self, db_session: Session, test_user, customer_with_account
    ):
        """Test that all payment methods for debt payments are tracked."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("300.00"),
            "cash",
            utc_datetime,
        )
        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("400.00"),
            "transfer",
            utc_datetime,
        )
        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("250.00"),
            "card",
            utc_datetime,
        )
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.debt_payments_cash == Decimal("300.00")
        assert summary.debt_payments_transfer == Decimal("400.00")
        assert summary.debt_payments_card == Decimal("250.00")
        assert summary.debt_payments_total == Decimal("950.00")

    def test_voided_debt_payments_excluded(
        self, db_session: Session, test_user, customer_with_account
    ):
        """Test that voided debt payments are not included."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("300.00"),
            "cash",
            utc_datetime,
        )
        voided_payment = self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )
        voided_payment.voided = True
        voided_payment.void_reason = "Test void"
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.debt_payments_cash == Decimal(
            "300.00"
        ), "Voided payments should not be included"

    def test_advance_payments_not_counted_as_debt_payments(
        self, db_session: Session, test_user, customer_with_account
    ):
        """Test that advance payments (customer credit) are not counted as debt payments."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        self._create_debt_payment(
            db_session,
            customer_with_account.id,
            test_user.id,
            Decimal("300.00"),
            "cash",
            utc_datetime,
        )

        import uuid

        receipt_num = f"ADV-{utc_datetime.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        advance_payment = Payment(
            customer_id=customer_with_account.id,
            amount=Decimal("500.00"),
            payment_method="cash",
            payment_type=PaymentType.advance_payment,
            receipt_number=receipt_num,
            received_by_id=test_user.id,
            voided=False,
        )
        db_session.add(advance_payment)
        db_session.flush()
        advance_payment.created_at = utc_datetime
        db_session.commit()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert summary.debt_payments_cash == Decimal(
            "300.00"
        ), "Advance payments should not be counted as debt payments"


class TestCloseCashRegisterExpectedCash:
    """Test that close_cash_register calculates expected_cash correctly."""

    @pytest.fixture
    def test_customer(self, db_session: Session) -> Customer:
        """Create a test customer."""
        customer = Customer(
            name="Test Customer",
            phone="1234567890",
            email="test@example.com",
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        return customer

    @pytest.fixture
    def customer_with_account(self, db_session: Session, test_user) -> Customer:
        """Create a customer with an account for debt payments."""
        customer = Customer(
            name="Account Customer",
            phone="5555555555",
            email="account@example.com",
        )
        db_session.add(customer)
        db_session.flush()

        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("1000.00"),
            available_credit=Decimal("0.00"),
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(customer)
        return customer

    @pytest.fixture
    def expense_category(self, db_session: Session) -> ExpenseCategory:
        """Create an expense category."""
        category = ExpenseCategory(
            name="Test Category",
            description="For testing",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    def _create_sale(
        self,
        db: Session,
        user_id: int,
        customer_id: int,
        total: Decimal,
        payment_method: str,
        sale_datetime: datetime,
        cash_amount: Decimal = None,
        transfer_amount: Decimal = None,
    ) -> Sale:
        """Helper to create a sale."""
        import uuid

        invoice_num = f"INV-{sale_datetime.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        sale = Sale(
            invoice_number=invoice_num,
            customer_id=customer_id,
            user_id=user_id,
            subtotal=total,
            total_amount=total,
            paid_amount=total if payment_method != "credit" else Decimal("0.00"),
            payment_method=payment_method,
            payment_status="paid" if payment_method != "credit" else "pending",
            sale_date=sale_datetime,
            cash_amount=cash_amount,
            transfer_amount=transfer_amount,
        )
        db.add(sale)
        return sale

    def _create_expense(
        self,
        db: Session,
        user_id: int,
        category_id: int,
        amount: Decimal,
        payment_method: str,
        expense_date: date,
    ) -> Expense:
        """Helper to create an expense."""
        expense = Expense(
            category_id=category_id,
            amount=amount,
            description="Test expense",
            expense_date=expense_date,
            payment_method=payment_method,
            created_by=user_id,
            is_editable=True,
        )
        db.add(expense)
        return expense

    def _create_debt_payment(
        self,
        db: Session,
        customer_id: int,
        user_id: int,
        amount: Decimal,
        payment_method: str,
        created_at: datetime,
    ) -> Payment:
        """Helper to create a debt payment."""
        import uuid

        receipt_num = f"REC-{created_at.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        payment = Payment(
            customer_id=customer_id,
            amount=amount,
            payment_method=payment_method,
            payment_type=PaymentType.payment,
            receipt_number=receipt_num,
            received_by_id=user_id,
            voided=False,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        payment.created_at = created_at
        db.commit()
        return payment

    def test_expected_cash_only_includes_cash_sales(
        self, db_session: Session, test_user, test_customer
    ):
        """Test that expected_cash only includes cash sales, not transfer or credit."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)
        opening_balance = Decimal("1000.00")

        cash_closing.open_cash_register(
            db_session,
            target_date=test_date,
            opening_balance=opening_balance,
            opened_by=test_user.id,
        )

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("1000.00"),
            "transfer",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("2000.00"),
            "credit",
            utc_datetime,
        )
        db_session.commit()

        result = cash_closing.close_cash_register(
            db_session,
            target_date=test_date,
            cash_count=Decimal("1500.00"),
            closed_by=test_user.id,
        )

        expected = opening_balance + Decimal("500.00")
        assert result.expected_cash == expected, (
            f"Expected cash should be {expected} (opening + cash sales only), "
            f"got {result.expected_cash}"
        )

    def test_expected_cash_includes_mixed_cash_portion(
        self, db_session: Session, test_user, test_customer
    ):
        """Test that expected_cash includes cash portion from mixed payments."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)
        opening_balance = Decimal("1000.00")

        cash_closing.open_cash_register(
            db_session,
            target_date=test_date,
            opening_balance=opening_balance,
            opened_by=test_user.id,
        )

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("1000.00"),
            "mixed",
            utc_datetime,
            cash_amount=Decimal("600.00"),
            transfer_amount=Decimal("400.00"),
        )
        db_session.commit()

        result = cash_closing.close_cash_register(
            db_session,
            target_date=test_date,
            cash_count=Decimal("2100.00"),
            closed_by=test_user.id,
        )

        expected = opening_balance + Decimal("500.00") + Decimal("600.00")
        assert result.expected_cash == expected, (
            f"Expected cash should be {expected} (opening + cash sales + mixed cash), "
            f"got {result.expected_cash}"
        )

    def test_expected_cash_includes_debt_payments_cash(
        self,
        db_session: Session,
        test_user,
        test_customer,
        customer_with_account,
    ):
        """Test that expected_cash includes cash debt payments."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)
        opening_balance = Decimal("1000.00")

        cash_closing.open_cash_register(
            db_session,
            target_date=test_date,
            opening_balance=opening_balance,
            opened_by=test_user.id,
        )

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )

        receipt_num = f"REC-{utc_datetime.strftime('%Y%m%d%H%M%S')}-001"
        payment = Payment(
            customer_id=customer_with_account.id,
            amount=Decimal("300.00"),
            payment_method="cash",
            payment_type=PaymentType.payment,
            receipt_number=receipt_num,
            received_by_id=test_user.id,
            voided=False,
        )
        db_session.add(payment)
        db_session.flush()
        payment.created_at = utc_datetime
        db_session.commit()

        result = cash_closing.close_cash_register(
            db_session,
            target_date=test_date,
            cash_count=Decimal("1800.00"),
            closed_by=test_user.id,
        )

        expected = opening_balance + Decimal("500.00") + Decimal("300.00")
        assert result.expected_cash == expected, (
            f"Expected cash should be {expected} "
            f"(opening + cash sales + cash debt payments), "
            f"got {result.expected_cash}"
        )

    def test_expected_cash_subtracts_cash_expenses(
        self,
        db_session: Session,
        test_user,
        test_customer,
        expense_category,
    ):
        """Test that expected_cash subtracts cash expenses."""
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)
        opening_balance = Decimal("1000.00")

        cash_closing.open_cash_register(
            db_session,
            target_date=test_date,
            opening_balance=opening_balance,
            opened_by=test_user.id,
        )

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )

        self._create_expense(
            db_session,
            test_user.id,
            expense_category.id,
            Decimal("100.00"),
            "cash",
            test_date,
        )
        self._create_expense(
            db_session,
            test_user.id,
            expense_category.id,
            Decimal("200.00"),
            "transfer",
            test_date,
        )
        db_session.commit()

        result = cash_closing.close_cash_register(
            db_session,
            target_date=test_date,
            cash_count=Decimal("1400.00"),
            closed_by=test_user.id,
        )

        expected = opening_balance + Decimal("500.00") - Decimal("100.00")
        assert result.expected_cash == expected, (
            f"Expected cash should be {expected} "
            f"(opening + cash sales - cash expenses only), "
            f"got {result.expected_cash}"
        )

    def test_full_expected_cash_calculation(
        self,
        db_session: Session,
        test_user,
        test_customer,
        customer_with_account,
        expense_category,
    ):
        """Test complete expected_cash calculation with all components.

        Expected cash formula:
        opening_balance
        + sales_cash
        + sales_mixed_cash
        + debt_payments_cash
        - expenses_cash
        """
        test_date = date.today()
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)
        opening_balance = Decimal("1000.00")

        cash_closing.open_cash_register(
            db_session,
            target_date=test_date,
            opening_balance=opening_balance,
            opened_by=test_user.id,
        )

        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("500.00"),
            "cash",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("1000.00"),
            "transfer",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("2000.00"),
            "credit",
            utc_datetime,
        )
        self._create_sale(
            db_session,
            test_user.id,
            test_customer.id,
            Decimal("800.00"),
            "mixed",
            utc_datetime,
            cash_amount=Decimal("500.00"),
            transfer_amount=Decimal("300.00"),
        )

        receipt_num = f"REC-{utc_datetime.strftime('%Y%m%d%H%M%S')}-001"
        cash_debt_payment = Payment(
            customer_id=customer_with_account.id,
            amount=Decimal("300.00"),
            payment_method="cash",
            payment_type=PaymentType.payment,
            receipt_number=receipt_num,
            received_by_id=test_user.id,
            voided=False,
        )
        db_session.add(cash_debt_payment)
        db_session.flush()
        cash_debt_payment.created_at = utc_datetime

        receipt_num2 = f"REC-{utc_datetime.strftime('%Y%m%d%H%M%S')}-002"
        transfer_debt_payment = Payment(
            customer_id=customer_with_account.id,
            amount=Decimal("400.00"),
            payment_method="transfer",
            payment_type=PaymentType.payment,
            receipt_number=receipt_num2,
            received_by_id=test_user.id,
            voided=False,
        )
        db_session.add(transfer_debt_payment)
        db_session.flush()
        transfer_debt_payment.created_at = utc_datetime

        self._create_expense(
            db_session,
            test_user.id,
            expense_category.id,
            Decimal("150.00"),
            "cash",
            test_date,
        )
        self._create_expense(
            db_session,
            test_user.id,
            expense_category.id,
            Decimal("200.00"),
            "transfer",
            test_date,
        )
        db_session.commit()

        expected = (
            opening_balance
            + Decimal("500.00")
            + Decimal("500.00")
            + Decimal("300.00")
            - Decimal("150.00")
        )

        result = cash_closing.close_cash_register(
            db_session,
            target_date=test_date,
            cash_count=expected,
            closed_by=test_user.id,
        )

        assert result.expected_cash == expected, (
            f"Expected cash should be {expected}, got {result.expected_cash}. "
            "Formula: opening_balance + sales_cash + sales_mixed_cash + "
            "debt_payments_cash - expenses_cash"
        )
        assert result.cash_difference == Decimal("0.00"), (
            f"Cash difference should be 0 when count matches expected, "
            f"got {result.cash_difference}"
        )


class TestDailySummarySchemaFields:
    """Test that DailySummary schema has all required fields for payment breakdown."""

    def test_daily_summary_has_mixed_payment_fields(
        self, db_session: Session, test_user
    ):
        """Test that DailySummary includes sales_mixed_cash and sales_mixed_transfer."""
        test_date = date.today()

        summary = cash_closing.get_daily_summary(db_session, target_date=test_date)

        assert hasattr(
            summary, "sales_mixed_cash"
        ), "DailySummary should have sales_mixed_cash field"
        assert hasattr(
            summary, "sales_mixed_transfer"
        ), "DailySummary should have sales_mixed_transfer field"
