"""Test customer credit balance behavior for full payments."""

from decimal import Decimal

import pytest
from app.crud.payment import payment_crud
from app.models.customer import Customer
from app.models.product import Category, Product
from app.models.sale import Sale
from app.models.user import User
from app.services.balance_service import BalanceService
from sqlalchemy.orm import Session


class TestCustomerCreditBehavior:
    """Test customer credit handling in sales and payments."""

    @pytest.fixture
    def balance_service(self) -> BalanceService:
        """Create balance service instance."""
        return BalanceService()

    @pytest.fixture
    def test_category(self, db_session: Session) -> Category:
        """Create a test category."""
        category = Category(
            name="Test Category",
            description="Test category for unit tests",
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        """Create a test user."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def customer_with_credit(self, db_session: Session, test_user: User) -> Customer:
        """Create a customer with credit balance."""
        # Create customer
        customer = Customer(
            name="Test Customer",
            phone="1234567890",
            email="credit@test.com",
            created_by_id=test_user.id,
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)

        # Add advance payment to create credit balance
        payment_crud.create_payment(
            db_session,
            customer_id=customer.id,
            amount=Decimal("5000.00"),
            payment_method="cash",
            payment_type="advance_payment",
            notes="Initial credit",
            created_by=test_user.id,
        )
        db_session.commit()

        return customer

    def test_full_payment_behavior_current_system(
        self,
        db_session: Session,
        customer_with_credit: Customer,
        test_user: User,
        test_category: Category,
        balance_service: BalanceService,
    ):
        """Test current system behavior - understand how it works now."""
        # Check initial balance (should be $5000 credit)
        initial_balance = balance_service.calculate_balance(
            db_session, customer_with_credit.id
        )
        assert initial_balance == Decimal(
            "5000.00"
        ), f"Expected $5000 credit, got {initial_balance}"

        # Create a product
        product = Product(
            name="Test Product",
            sku="TEST001",
            price=Decimal("1000.00"),
            stock_quantity=10,
            category_id=test_category.id,
            is_active=True,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        # Create sale for $1000
        sale = Sale(
            customer_id=customer_with_credit.id,
            total_amount=Decimal("1000.00"),
            paid_amount=Decimal("1000.00"),
            payment_method="cash",
            user_id=test_user.id,
            is_voided=False,
        )
        db_session.add(sale)
        db_session.commit()

        # Check balance after sale
        balance_after_sale = balance_service.calculate_balance(
            db_session, customer_with_credit.id
        )
        print(f"Balance after sale: {balance_after_sale}")

        # In current system, the balance should be:
        # Initial: $5000 credit
        # After $1000 sale: $5000 - $1000 = $4000 credit
        assert balance_after_sale == Decimal(
            "4000.00"
        ), f"After sale, balance should be $4000, got {balance_after_sale}"

    def test_payment_with_credit_not_auto_applied(
        self,
        db_session: Session,
        customer_with_credit: Customer,
        test_user: User,
        balance_service: BalanceService,
    ):
        """Test if making a payment when customer has credit adds to credit instead of consuming it."""
        # Check initial credit balance
        initial_balance = balance_service.calculate_balance(
            db_session, customer_with_credit.id
        )
        assert initial_balance == Decimal("5000.00")

        # Make another payment of $2000
        payment_crud.create_payment(
            db_session,
            customer_id=customer_with_credit.id,
            amount=Decimal("2000.00"),
            payment_method="cash",
            payment_type="payment",
            notes="Additional payment",
            created_by=test_user.id,
        )
        db_session.commit()

        # Check balance after payment
        balance_after = balance_service.calculate_balance(
            db_session, customer_with_credit.id
        )

        # Should be $5000 + $2000 = $7000 credit
        assert balance_after == Decimal(
            "7000.00"
        ), f"Payment should increase credit to $7000, got {balance_after}"

    def test_explicit_credit_usage(
        self,
        db_session: Session,
        customer_with_credit: Customer,
        test_user: User,
        test_category: Category,
        balance_service: BalanceService,
    ):
        """Test explicit credit application to a sale."""
        # Create product
        product = Product(
            name="Test Product",
            sku="TEST002",
            price=Decimal("1000.00"),
            stock_quantity=10,
            category_id=test_category.id,
            is_active=True,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        # Create sale
        sale = Sale(
            customer_id=customer_with_credit.id,
            total_amount=Decimal("1000.00"),
            paid_amount=Decimal("0.00"),  # Not paid yet
            payment_method="account_credit",
            user_id=test_user.id,
            is_voided=False,
        )
        db_session.add(sale)
        db_session.commit()

        # Apply credit explicitly
        payment_crud.create_payment(
            db_session,
            customer_id=customer_with_credit.id,
            amount=Decimal("1000.00"),
            payment_method="credit",
            payment_type="credit_application",
            sale_id=sale.id,
            notes="Applied customer credit to sale",
            created_by=test_user.id,
        )
        db_session.commit()

        # Update sale as paid
        sale.paid_amount = Decimal("1000.00")
        db_session.commit()

        # Check balance after credit application
        balance_after = balance_service.calculate_balance(
            db_session, customer_with_credit.id
        )

        # Should be $5000 - $1000 = $4000 credit remaining
        # The credit_application type should reduce the balance
        print(f"Balance after credit application: {balance_after}")

        # Note: This test reveals how the current system works
        # We need to understand the actual behavior first
