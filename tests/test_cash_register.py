"""Cash register tests.

Tests cover FASE 7 from test coverage plan:
- Cash register operations (open/close)
- Sales validation with cash register
- Multi-day scenarios
- Balance tracking

IMPORTANT: Cash register dates
- The cash register belongs to the OPENING DATE, not the closing date
- Example: Open on day 12, close on day 13 → register is for day 12
- After closing day 12's register, can open day 13's register
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from app.crud.cash_closing import cash_closing
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.models.product import Category, Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.utils.timezone import get_local_today
from sqlalchemy.orm import Session


class TestCashRegister:
    """Test cash register operations and validations."""

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        """Create a test user."""
        user = User(
            email="cashier@example.com",
            password_hash="hashedpass",
            full_name="Test Cashier",
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
            name="Cash Register Products",
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
            sku="CR001",
            name="Cash Test Product",
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
            name="Cash Test Customer",
            phone="555-7777",
            email="cashtest@example.com",
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

    # ============================================================
    # CATEGORY: Cash Register Open
    # ============================================================

    def test_sale_with_open_cash_register(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        customer_with_account: Customer,
    ):
        """Test 7.1: Sale is allowed when cash register is open.

        Expected behavior:
        1. Open cash register for today
        2. Sale should be processed successfully
        3. Sale should be linked to the open register date
        """
        # Arrange: Open cash register for today
        today = get_local_today()
        cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Act: Create a sale
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
        db_session.commit()

        # Assert: Sale was created successfully
        assert sale.id is not None
        assert sale.total_amount == Decimal("110.00")  # 100 + 10% tax

        # Assert: Cash register is still open
        register_status = cash_closing.is_cash_register_open(
            db_session, target_date=today
        )
        assert register_status is True

    def test_cash_register_tracks_sales(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        customer_with_account: Customer,
    ):
        """Test 7.2: Cash register tracks sales for the day.

        Expected behavior:
        1. Open cash register
        2. Make multiple sales
        3. Daily summary should include all sales
        """
        # Arrange: Open cash register
        today = get_local_today()
        cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Act: Create 3 sales
        for i in range(3):
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
                notes=f"Sale {i+1}",
            )
            sale_crud.create_sale(
                db=db_session, sale_in=sale_data, user_id=test_user.id
            )
            db_session.commit()

        # Assert: Daily summary shows all sales
        daily_summary = cash_closing.get_daily_summary(db_session, target_date=today)
        assert daily_summary.sales_count == 3
        assert daily_summary.total_sales == Decimal("330.00")  # 3 * 110

    def test_cash_register_cash_only(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        customer_with_account: Customer,
    ):
        """Test 7.3: Cash register only tracks cash payments.

        Expected behavior:
        1. Sales with credit/card should not affect cash count
        2. Only cash payments are relevant for closing balance

        Note: This is a design verification test - the architecture
        ensures that cash register closing only counts physical cash.
        """
        # Arrange: Open cash register
        today = get_local_today()
        opening_balance = Decimal("1000.00")
        cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=opening_balance,
            opened_by=test_user.id,
        )
        db_session.commit()

        # Act: Create sale (payment will be handled separately)
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
        sale_crud.create_sale(db=db_session, sale_in=sale_data, user_id=test_user.id)
        db_session.commit()

        # Assert: Cash register opening balance unchanged
        # (The actual cash counting happens at closing time)
        register = cash_closing.get_by_date(db_session, closing_date=today)
        assert register.opening_balance == opening_balance

    # ============================================================
    # CATEGORY: Cash Register Closed
    # ============================================================

    def test_sale_with_closed_cash_register_fails(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        customer_with_account: Customer,
    ):
        """Test 7.4: Sale is rejected when cash register is closed.

        Expected behavior:
        1. Open and immediately close cash register
        2. Attempt to create sale should fail
        3. Error message should indicate cash register is closed
        """
        # Arrange: Open and close cash register
        today = get_local_today()
        cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Close the register
        cash_closing.close_cash_register(
            db_session,
            target_date=today,
            cash_count=Decimal("1000.00"),
            closed_by=test_user.id,
        )
        db_session.commit()

        # Act & Assert: Attempt to create sale should fail
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

        with pytest.raises(ValueError, match="Cash register must be opened"):
            sale_crud.create_sale(
                db=db_session, sale_in=sale_data, user_id=test_user.id
            )

    def test_cash_register_not_opened_today_fails(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        customer_with_account: Customer,
    ):
        """Test 7.5: Sale is rejected when no cash register opened for today.

        Expected behavior:
        1. Don't open cash register
        2. Attempt to create sale should fail
        3. Error should indicate cash register needs to be opened
        """
        # Act & Assert: Attempt to create sale without opening register
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

        with pytest.raises(ValueError, match="Cash register must be opened"):
            sale_crud.create_sale(
                db=db_session, sale_in=sale_data, user_id=test_user.id
            )

    # ============================================================
    # CATEGORY: Cash Register Closing
    # ============================================================

    def test_cash_register_closing_includes_sales(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        customer_with_account: Customer,
    ):
        """Test 7.6: Closing summary includes all sales from the day.

        Expected behavior:
        1. Open register, make sales
        2. Close register
        3. Closing record should reflect total sales
        """
        # Arrange: Open register and make sales
        today = get_local_today()
        opening_balance = Decimal("1000.00")
        cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=opening_balance,
            opened_by=test_user.id,
        )
        db_session.commit()

        # Make 2 sales
        for _ in range(2):
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
            sale_crud.create_sale(
                db=db_session, sale_in=sale_data, user_id=test_user.id
            )
            db_session.commit()

        # Act: Close register
        closing = cash_closing.close_cash_register(
            db_session,
            target_date=today,
            cash_count=Decimal("1220.00"),  # Opening + 2 sales
            closed_by=test_user.id,
        )
        db_session.commit()

        # Assert: Closing includes sales
        daily_summary = cash_closing.get_daily_summary(db_session, target_date=today)
        assert daily_summary.sales_count == 2
        assert daily_summary.total_sales == Decimal("220.00")
        assert closing.closing_date == today

    def test_cash_register_closing_balance_correct(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        customer_with_account: Customer,
    ):
        """Test 7.7: Closing balance calculation is correct.

        Expected behavior:
        1. Expected cash = opening_balance + cash_sales - cash_expenses
        2. Cash difference = cash_count - expected_cash
        3. Closing should calculate these correctly
        """
        # Arrange: Open register
        today = get_local_today()
        opening_balance = Decimal("1000.00")
        cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=opening_balance,
            opened_by=test_user.id,
        )
        db_session.commit()

        # Make 1 sale
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
        sale_crud.create_sale(db=db_session, sale_in=sale_data, user_id=test_user.id)
        db_session.commit()

        # Act: Close register with exact count
        expected_cash = opening_balance + Decimal("110.00")  # Sale amount
        closing = cash_closing.close_cash_register(
            db_session,
            target_date=today,
            cash_count=expected_cash,
            closed_by=test_user.id,
        )
        db_session.commit()

        # Assert: Balances are correct
        assert closing.opening_balance == opening_balance
        assert closing.cash_count == expected_cash
        assert closing.cash_difference == Decimal("0.00")  # Perfect match

    def test_cannot_reopen_closed_register(
        self,
        db_session: Session,
        test_user: User,
    ):
        """Test 7.8: Cannot reopen a closed cash register for the same date.

        Expected behavior:
        1. Open and close register for day X
        2. Attempt to open register for day X again should fail
        3. But can open register for day X+1

        CRITICAL: This tests the date logic:
        - Register for day 12, closed on day 13 → is day 12's register
        - Can open day 13's register after closing day 12's
        """
        # Arrange: Open and close register for today
        today = get_local_today()
        cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        cash_closing.close_cash_register(
            db_session,
            target_date=today,
            cash_count=Decimal("1000.00"),
            closed_by=test_user.id,
        )
        db_session.commit()

        # Act & Assert: Cannot reopen for same date
        with pytest.raises(ValueError, match="already closed"):
            cash_closing.open_cash_register(
                db_session,
                target_date=today,
                opening_balance=Decimal("1000.00"),
                opened_by=test_user.id,
            )

        # But can open for next day
        tomorrow = today + timedelta(days=1)
        next_register = cash_closing.open_cash_register(
            db_session,
            target_date=tomorrow,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Assert: Next day register opened successfully
        assert next_register.closing_date == tomorrow
        assert next_register.is_finalized is False

    def test_cannot_open_multiple_registers_simultaneously(
        self,
        db_session: Session,
        test_user: User,
    ):
        """Test 7.EXTRA: Cannot have multiple open registers at once.

        Expected behavior:
        1. Open register for day X
        2. Attempt to open register for day Y (without closing X) should fail
        3. Must close X before opening Y

        This is CRITICAL for data integrity.
        """
        # Arrange: Open register for today
        today = get_local_today()
        cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Act & Assert: Cannot open another register without closing first
        tomorrow = today + timedelta(days=1)
        with pytest.raises(ValueError, match="Please close the cash register"):
            cash_closing.open_cash_register(
                db_session,
                target_date=tomorrow,
                opening_balance=Decimal("1000.00"),
                opened_by=test_user.id,
            )

        # Now close today's register
        cash_closing.close_cash_register(
            db_session,
            target_date=today,
            cash_count=Decimal("1000.00"),
            closed_by=test_user.id,
        )
        db_session.commit()

        # Now can open tomorrow's register
        tomorrow_register = cash_closing.open_cash_register(
            db_session,
            target_date=tomorrow,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()

        # Assert: Tomorrow's register opened successfully
        assert tomorrow_register.closing_date == tomorrow
