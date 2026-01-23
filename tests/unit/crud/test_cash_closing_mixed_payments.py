"""Tests for mixed debt payments in cash closing daily summary."""

from datetime import date
from decimal import Decimal

import pytest
from app.crud.cash_closing import cash_closing
from app.models.customer import Customer
from app.models.payment import Payment, PaymentType
from app.models.user import User
from sqlalchemy.orm import Session


@pytest.fixture
def cashier_user(db_session: Session) -> User:
    """Create a cashier user for tests."""
    user = User(
        email="cashier@test.com",
        password_hash="hashed",
        full_name="Test Cashier",
        role="cashier",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def debt_customer(db_session: Session) -> Customer:
    """Create a customer with debt for tests."""
    customer = Customer(
        name="Debt Customer",
        email="debt@test.com",
        phone="1234567890",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


class TestMixedDebtPaymentsInDailySummary:
    """Tests for mixed debt payments breakdown in daily summary."""

    def test_mixed_payment_with_breakdown_columns(
        self, db_session: Session, debt_customer: Customer, cashier_user: User
    ):
        """Test mixed payment with breakdown columns is aggregated correctly."""
        # Arrange: Create a mixed payment with breakdown
        payment = Payment(
            customer_id=debt_customer.id,
            amount=Decimal("300.00"),
            payment_method="mixed",
            payment_type=PaymentType.payment,
            receipt_number="PAY-2025-MIXED",
            received_by_id=cashier_user.id,
            notes="Mixed payment (cash: $100.00, transfer: $150.00, card: $50.00)",
            cash_amount=Decimal("100.00"),
            transfer_amount=Decimal("150.00"),
            card_amount=Decimal("50.00"),
        )
        db_session.add(payment)
        db_session.commit()

        # Act
        summary = cash_closing.get_daily_summary(db_session, target_date=date.today())

        # Assert: Mixed payment components should be added to respective totals
        assert summary.debt_payments_cash == Decimal("100.00")
        assert summary.debt_payments_transfer == Decimal("150.00")
        assert summary.debt_payments_card == Decimal("50.00")
        assert summary.debt_payments_total == Decimal("300.00")

    def test_mixed_and_single_payments_combined(
        self, db_session: Session, debt_customer: Customer, cashier_user: User
    ):
        """Test that mixed and single payments are combined correctly."""
        # Arrange: Create a single cash payment
        single_payment = Payment(
            customer_id=debt_customer.id,
            amount=Decimal("200.00"),
            payment_method="cash",
            payment_type=PaymentType.payment,
            receipt_number="PAY-2025-SINGLE",
            received_by_id=cashier_user.id,
        )
        db_session.add(single_payment)

        # Create a mixed payment
        mixed_payment = Payment(
            customer_id=debt_customer.id,
            amount=Decimal("300.00"),
            payment_method="mixed",
            payment_type=PaymentType.payment,
            receipt_number="PAY-2025-MIXED",
            received_by_id=cashier_user.id,
            cash_amount=Decimal("100.00"),
            transfer_amount=Decimal("200.00"),
        )
        db_session.add(mixed_payment)
        db_session.commit()

        # Act
        summary = cash_closing.get_daily_summary(db_session, target_date=date.today())

        # Assert
        # Cash: $200 (single) + $100 (mixed) = $300
        assert summary.debt_payments_cash == Decimal("300.00")
        # Transfer: $200 (mixed only)
        assert summary.debt_payments_transfer == Decimal("200.00")
        # Total: $200 + $300 = $500
        assert summary.debt_payments_total == Decimal("500.00")

    def test_single_payment_methods_still_work(
        self, db_session: Session, debt_customer: Customer, cashier_user: User
    ):
        """Test that single payment methods still work correctly."""
        # Arrange: Create payments with different methods
        payments = [
            Payment(
                customer_id=debt_customer.id,
                amount=Decimal("100.00"),
                payment_method="cash",
                payment_type=PaymentType.payment,
                receipt_number="PAY-2025-00001",
                received_by_id=cashier_user.id,
            ),
            Payment(
                customer_id=debt_customer.id,
                amount=Decimal("200.00"),
                payment_method="transfer",
                payment_type=PaymentType.payment,
                reference_number="TRF-123",
                receipt_number="PAY-2025-00002",
                received_by_id=cashier_user.id,
            ),
            Payment(
                customer_id=debt_customer.id,
                amount=Decimal("50.00"),
                payment_method="card",
                payment_type=PaymentType.payment,
                reference_number="CARD-456",
                receipt_number="PAY-2025-00003",
                received_by_id=cashier_user.id,
            ),
        ]
        for p in payments:
            db_session.add(p)
        db_session.commit()

        # Act
        summary = cash_closing.get_daily_summary(db_session, target_date=date.today())

        # Assert
        assert summary.debt_payments_cash == Decimal("100.00")
        assert summary.debt_payments_transfer == Decimal("200.00")
        assert summary.debt_payments_card == Decimal("50.00")
        assert summary.debt_payments_total == Decimal("350.00")

    def test_voided_mixed_payment_excluded(
        self, db_session: Session, debt_customer: Customer, cashier_user: User
    ):
        """Test that voided mixed payments are NOT included in summary."""
        # Arrange: Create a voided mixed payment
        payment = Payment(
            customer_id=debt_customer.id,
            amount=Decimal("500.00"),
            payment_method="mixed",
            payment_type=PaymentType.payment,
            receipt_number="PAY-2025-VOIDED",
            received_by_id=cashier_user.id,
            cash_amount=Decimal("300.00"),
            transfer_amount=Decimal("200.00"),
            voided=True,
            void_reason="Test void",
        )
        db_session.add(payment)
        db_session.commit()

        # Act
        summary = cash_closing.get_daily_summary(db_session, target_date=date.today())

        # Assert: Voided payment should not be counted
        assert summary.debt_payments_cash == Decimal("0.00")
        assert summary.debt_payments_transfer == Decimal("0.00")
        assert summary.debt_payments_total == Decimal("0.00")
