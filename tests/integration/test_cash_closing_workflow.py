"""Tests for cash closing workflow with pending registers."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from app.crud.cash_closing import cash_closing
from app.models.cash_closing import CashClosing
from app.models.user import User
from app.services.cash_closing_service import cash_closing_service
from sqlalchemy.orm import Session


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="cashier@test.com",
        password_hash="hashed",
        full_name="Test Cashier",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestCashClosingWithPendingRegisters:
    """Test cash closing workflow with pending registers from previous days."""

    def test_cannot_open_new_register_with_pending(
        self, db_session: Session, test_user: User
    ):
        """Test that new register cannot be opened if there's a pending one."""
        yesterday = date.today() - timedelta(days=1)
        today = date.today()

        # Open register for yesterday
        yesterday_register = cash_closing.open_cash_register(
            db_session,
            target_date=yesterday,
            opening_balance=Decimal("100.00"),
            opened_by=test_user.id,
        )
        assert yesterday_register is not None
        assert yesterday_register.closing_date == yesterday
        assert yesterday_register.is_finalized is False

        # Try to open register for today - should fail
        with pytest.raises(ValueError) as exc_info:
            cash_closing.open_cash_register(
                db_session,
                target_date=today,
                opening_balance=Decimal("200.00"),
                opened_by=test_user.id,
            )

        assert "Cannot open new cash register" in str(exc_info.value)
        assert yesterday.strftime("%Y-%m-%d") in str(exc_info.value)

    def test_can_close_pending_register_next_day(
        self, db_session: Session, test_user: User
    ):
        """Test that pending register can be closed on a different day."""
        yesterday = date.today() - timedelta(days=1)

        # Open register for yesterday
        cash_closing.open_cash_register(
            db_session,
            target_date=yesterday,
            opening_balance=Decimal("100.00"),
            opened_by=test_user.id,
        )

        # Close it today (but it should maintain yesterday's date)
        from app.schemas.cash_closing import CashClosingCreate

        closing_data = CashClosingCreate(
            closing_date=yesterday,  # Must use the original date
            opening_balance=Decimal("100.00"),
            cash_count=Decimal("250.00"),
            notes="Closing yesterday's register today",
        )

        closed_register = cash_closing_service.create_closing(
            db=db_session,
            closing_data=closing_data,
            user_id=test_user.id,
        )

        # Verify the closing maintains the original date
        assert closed_register.closing_date == yesterday
        assert closed_register.cash_count == Decimal("250.00")

        # Verify closed_at is today (for audit)
        db_closing = cash_closing.get_by_date(db_session, closing_date=yesterday)
        assert db_closing.closing_date == yesterday
        # closed_at will be today's timestamp, but closing_date remains yesterday

    def test_can_open_today_after_closing_yesterday(
        self, db_session: Session, test_user: User
    ):
        """Test that today's register can be opened after closing yesterday's."""
        yesterday = date.today() - timedelta(days=1)
        today = date.today()

        # Open and close yesterday's register
        cash_closing.open_cash_register(
            db_session,
            target_date=yesterday,
            opening_balance=Decimal("100.00"),
            opened_by=test_user.id,
        )

        # Finalize it
        db_closing = cash_closing.get_by_date(db_session, closing_date=yesterday)
        db_closing.is_finalized = True
        db_closing.cash_count = Decimal("150.00")
        db_closing.sales_total = Decimal("50.00")
        db_closing.expenses_total = Decimal("0.00")
        db_closing.expected_cash = Decimal("150.00")
        db_closing.cash_difference = Decimal("0.00")
        db_session.commit()

        # Now should be able to open today's register
        today_register = cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=Decimal("150.00"),
            opened_by=test_user.id,
        )

        assert today_register is not None
        assert today_register.closing_date == today
        assert today_register.is_finalized is False

    def test_get_unfinalized_register(self, db_session: Session, test_user: User):
        """Test getting unfinalized register from any date."""
        three_days_ago = date.today() - timedelta(days=3)
        two_days_ago = date.today() - timedelta(days=2)

        # Create multiple registers
        # Open one from 3 days ago (leave it open)
        cash_closing.open_cash_register(
            db_session,
            target_date=three_days_ago,
            opening_balance=Decimal("100.00"),
            opened_by=test_user.id,
        )

        # Check that we can find the unfinalized register
        unfinalized = cash_closing.get_unfinalized_register(db_session)
        assert unfinalized is not None
        assert unfinalized.closing_date == three_days_ago
        assert unfinalized.is_finalized is False

        # Close it
        unfinalized.is_finalized = True
        unfinalized.cash_count = Decimal("100.00")
        unfinalized.sales_total = Decimal("0.00")
        unfinalized.expenses_total = Decimal("0.00")
        unfinalized.expected_cash = Decimal("100.00")
        unfinalized.cash_difference = Decimal("0.00")
        db_session.commit()

        # Now there should be no unfinalized registers
        unfinalized = cash_closing.get_unfinalized_register(db_session)
        assert unfinalized is None

        # Open another one for 2 days ago
        cash_closing.open_cash_register(
            db_session,
            target_date=two_days_ago,
            opening_balance=Decimal("100.00"),
            opened_by=test_user.id,
        )

        # Should find the new unfinalized one
        unfinalized = cash_closing.get_unfinalized_register(db_session)
        assert unfinalized is not None
        assert unfinalized.closing_date == two_days_ago

    def test_service_get_pending_cash_register(
        self, db_session: Session, test_user: User
    ):
        """Test service method for getting pending cash register."""
        yesterday = date.today() - timedelta(days=1)

        # Initially no pending register
        pending = cash_closing_service.get_pending_cash_register(db_session)
        assert pending is None

        # Open register for yesterday
        cash_closing.open_cash_register(
            db_session,
            target_date=yesterday,
            opening_balance=Decimal("100.00"),
            opened_by=test_user.id,
        )

        # Now should find the pending register
        pending = cash_closing_service.get_pending_cash_register(db_session)
        assert pending is not None
        assert pending.closing_date == yesterday
        assert pending.is_finalized is False

        # Close it
        db_closing = cash_closing.get_by_date(db_session, closing_date=yesterday)
        db_closing.is_finalized = True
        db_closing.cash_count = Decimal("100.00")
        db_closing.sales_total = Decimal("0.00")
        db_closing.expenses_total = Decimal("0.00")
        db_closing.expected_cash = Decimal("100.00")
        db_closing.cash_difference = Decimal("0.00")
        db_session.commit()

        # Should no longer find pending register
        pending = cash_closing_service.get_pending_cash_register(db_session)
        assert pending is None

    def test_multiple_pending_registers_returns_most_recent(
        self, db_session: Session, test_user: User
    ):
        """Test that when multiple registers are pending, the most recent is returned."""
        five_days_ago = date.today() - timedelta(days=5)
        three_days_ago = date.today() - timedelta(days=3)

        # Create older unfinalized register
        older_register = CashClosing(
            closing_date=five_days_ago,
            opening_balance=Decimal("50.00"),
            sales_total=Decimal("0.00"),
            expenses_total=Decimal("0.00"),
            cash_count=Decimal("50.00"),
            expected_cash=Decimal("50.00"),
            cash_difference=Decimal("0.00"),
            opened_at=datetime.now(),
            opened_by=test_user.id,
            closed_by=test_user.id,
            is_finalized=False,
        )
        db_session.add(older_register)

        # Create newer unfinalized register
        newer_register = CashClosing(
            closing_date=three_days_ago,
            opening_balance=Decimal("100.00"),
            sales_total=Decimal("0.00"),
            expenses_total=Decimal("0.00"),
            cash_count=Decimal("100.00"),
            expected_cash=Decimal("100.00"),
            cash_difference=Decimal("0.00"),
            opened_at=datetime.now(),
            opened_by=test_user.id,
            closed_by=test_user.id,
            is_finalized=False,
        )
        db_session.add(newer_register)
        db_session.commit()

        # Should return the most recent unfinalized (3 days ago)
        unfinalized = cash_closing.get_unfinalized_register(db_session)
        assert unfinalized is not None
        assert unfinalized.closing_date == three_days_ago
