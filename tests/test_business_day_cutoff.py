"""Tests for business day cutoff logic and pending register detection.

Tests cover:
- Business day calculation with 4 AM cutoff
- Pending cash register detection
- Operating with old registers (warning scenario)
- Sales across midnight boundary
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from app.crud.cash_closing import cash_closing
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.models.product import Category, Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.cash_closing_service import cash_closing_service
from app.utils.timezone import get_cash_register_business_day
from sqlalchemy.orm import Session


class TestBusinessDayCutoff:
    """Test business day calculation with 4 AM cutoff."""

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        """Create a test user."""
        user = User(
            email="cutoff@example.com",
            password_hash="hashedpass",
            full_name="Test User",
            role="admin",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def test_category(self, db_session: Session) -> Category:
        """Create a test category."""
        category = Category(
            name="Cutoff Test Category",
            description="Test category",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def test_product(self, db_session: Session, test_category: Category) -> Product:
        """Create a test product."""
        product = Product(
            sku="CUT001",
            name="Cutoff Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("50.00"),
            first_sale_price=Decimal("100.00"),
            second_sale_price=Decimal("100.00"),
            third_sale_price=Decimal("100.00"),
            tax_rate=Decimal("10.00"),
            current_stock=100,
            minimum_stock=10,
            is_active=True,
            is_service=False,
            created_by=1,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    @pytest.fixture
    def customer_with_account(self, db_session: Session) -> Customer:
        """Create customer with account."""
        customer = Customer(
            name="Cutoff Test Customer",
            phone="555-9999",
            email="cutofftest@example.com",
            is_active=True,
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)

        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("0.00"),
            credit_limit=Decimal("1000.00"),
            created_by_id=1,
        )
        db_session.add(account)
        db_session.commit()

        return customer

    def test_business_day_before_cutoff(self):
        """Test business day calculation before 4 AM cutoff.

        Expected: Returns previous calendar day.
        """
        # Mock time: 2025-11-13 02:30 AM (before 4 AM)
        mock_time = datetime(2025, 11, 13, 2, 30, 0, tzinfo=ZoneInfo("America/Lima"))

        with patch("app.utils.timezone.get_local_now", return_value=mock_time):
            business_day = get_cash_register_business_day()

            # Should return previous day (11-12) because it's before 4 AM
            assert business_day == date(2025, 11, 12)

    def test_business_day_after_cutoff(self):
        """Test business day calculation after 4 AM cutoff.

        Expected: Returns current calendar day.
        """
        # Mock time: 2025-11-13 04:30 AM (after 4 AM)
        mock_time = datetime(2025, 11, 13, 4, 30, 0, tzinfo=ZoneInfo("America/Lima"))

        with patch("app.utils.timezone.get_local_now", return_value=mock_time):
            business_day = get_cash_register_business_day()

            # Should return current day (11-13) because it's after 4 AM
            assert business_day == date(2025, 11, 13)

    def test_business_day_exactly_at_cutoff(self):
        """Test business day calculation exactly at 4 AM.

        Expected: Returns current calendar day (4 AM is after cutoff).
        """
        # Mock time: 2025-11-13 04:00 AM (exactly 4 AM)
        mock_time = datetime(2025, 11, 13, 4, 0, 0, tzinfo=ZoneInfo("America/Lima"))

        with patch("app.utils.timezone.get_local_now", return_value=mock_time):
            business_day = get_cash_register_business_day()

            # Should return current day because hour 4 is NOT < 4
            assert business_day == date(2025, 11, 13)

    def test_sale_after_midnight_uses_previous_day_register(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        customer_with_account: Customer,
    ):
        """Test that sales after midnight go to previous day's register.

        Scenario:
        - Open register for day 12
        - Mock time to 13th at 01:00 AM (before 4 AM cutoff)
        - Create sale
        - Sale should be accepted (goes to day 12 register)
        """
        # Open register for day 12
        register_date = date(2025, 11, 12)
        cash_closing.open_cash_register(
            db_session,
            target_date=register_date,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Mock time: Next day at 01:00 AM (before 4 AM cutoff)
        mock_time = datetime(2025, 11, 13, 1, 0, 0, tzinfo=ZoneInfo("America/Lima"))

        with patch("app.utils.timezone.get_local_now", return_value=mock_time):
            # Business day should still be 11-12
            assert get_cash_register_business_day() == date(2025, 11, 12)

            # Sale should be allowed
            sale_data = SaleCreate(
                customer_id=customer_with_account.id,
                items=[
                    SaleItemCreate(
                        product_id=test_product.id,
                        quantity=1,
                        unit_price=Decimal("100.00"),
                        price_tier="first",
                    )
                ],
            )
            sale = sale_crud.create_sale(
                db=db_session, sale_in=sale_data, user_id=test_user.id
            )

            # Sale should be created successfully
            assert sale.id is not None
            assert sale.total_amount == Decimal("110.00")


class TestPendingCashRegister:
    """Test pending cash register detection."""

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        """Create a test user."""
        user = User(
            email="pending@example.com",
            password_hash="hashedpass",
            full_name="Test User",
            role="admin",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_no_pending_register_when_closed(
        self, db_session: Session, test_user: User
    ):
        """Test no pending register when all are closed."""
        # Don't open any register
        result = cash_closing_service.check_pending_cash_register(db_session)

        assert result["has_pending"] is False

    def test_no_pending_register_same_day(self, db_session: Session, test_user: User):
        """Test no pending register when register is for today."""
        # Mock time: 2025-11-12 10:00 AM
        mock_time = datetime(2025, 11, 12, 10, 0, 0, tzinfo=ZoneInfo("America/Lima"))

        with patch("app.utils.timezone.get_local_now", return_value=mock_time):
            # Open register for today (11-12)
            today = get_cash_register_business_day()
            cash_closing.open_cash_register(
                db_session,
                target_date=today,
                opening_balance=Decimal("1000.00"),
                opened_by=test_user.id,
            )
            db_session.commit()

            # Check pending - should be False (register is for today)
            result = cash_closing_service.check_pending_cash_register(db_session)
            assert result["has_pending"] is False

    def test_pending_register_one_day_old(self, db_session: Session, test_user: User):
        """Test pending register detection - 1 day old (RED alert).

        Scenario:
        - Open register for day 12
        - Mock time to day 13 at 09:00 AM (after cutoff)
        - Should detect pending register with CRITICAL severity
        """
        # Open register for day 12
        register_date = date(2025, 11, 12)
        cash_closing.open_cash_register(
            db_session,
            target_date=register_date,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Mock time: Next day at 09:00 AM (after 4 AM cutoff)
        mock_time = datetime(2025, 11, 13, 9, 0, 0, tzinfo=ZoneInfo("America/Lima"))

        with patch("app.utils.timezone.get_local_now", return_value=mock_time):
            result = cash_closing_service.check_pending_cash_register(db_session)

            # Should detect pending register
            assert result["has_pending"] is True
            assert result["severity"] == "critical"  # Red from day 1
            assert result["blocking"] is False
            assert result["days_old"] == 1
            assert result["pending_date"] == register_date
            assert result["current_business_day"] == date(2025, 11, 13)
            assert "CAJA PENDIENTE" in result["message"]
            assert "1 día" in result["message"]

    def test_pending_register_multiple_days_old(
        self, db_session: Session, test_user: User
    ):
        """Test pending register detection - 3 days old (still RED).

        Scenario:
        - Open register for day 12
        - Mock time to day 15 at 09:00 AM
        - Should detect pending register with 3 days old
        """
        # Open register for day 12
        register_date = date(2025, 11, 12)
        cash_closing.open_cash_register(
            db_session,
            target_date=register_date,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Mock time: 3 days later at 09:00 AM
        mock_time = datetime(2025, 11, 15, 9, 0, 0, tzinfo=ZoneInfo("America/Lima"))

        with patch("app.utils.timezone.get_local_now", return_value=mock_time):
            result = cash_closing_service.check_pending_cash_register(db_session)

            assert result["has_pending"] is True
            assert result["severity"] == "critical"  # Still red
            assert result["days_old"] == 3
            assert "3 días" in result["message"]

    def test_pending_register_before_cutoff(self, db_session: Session, test_user: User):
        """Test pending register check before 4 AM cutoff.

        Scenario:
        - Open register for day 12
        - Mock time to day 13 at 02:00 AM (before cutoff)
        - Should NOT show as pending (still business day 12)
        """
        # Open register for day 12
        register_date = date(2025, 11, 12)
        cash_closing.open_cash_register(
            db_session,
            target_date=register_date,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Mock time: Next day at 02:00 AM (before 4 AM cutoff)
        mock_time = datetime(2025, 11, 13, 2, 0, 0, tzinfo=ZoneInfo("America/Lima"))

        with patch("app.utils.timezone.get_local_now", return_value=mock_time):
            # Business day is still 11-12
            assert get_cash_register_business_day() == date(2025, 11, 12)

            result = cash_closing_service.check_pending_cash_register(db_session)

            # Should NOT be pending (register is for current business day)
            assert result["has_pending"] is False
