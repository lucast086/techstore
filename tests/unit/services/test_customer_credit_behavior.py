"""Test customer credit balance behavior for full payments."""

from decimal import Decimal

import pytest
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.models.product import Category, Product
from app.models.user import User
from app.schemas.payment import PaymentCreate
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.customer import customer_service
from sqlalchemy.orm import Session


class TestCustomerCreditFullPayment:
    """Test that customer credit is not automatically deducted on full payments."""

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
    def customer_with_credit(self, db_session: Session, test_user: User) -> Customer:
        """Create a customer with credit balance."""
        customer = Customer(
            name="Test Customer",
            phone="1234567890",
            email="credit@test.com",
        )
        db_session.add(customer)
        db_session.flush()

        # Create customer account with credit
        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("-5000.00"),  # Customer has $5000 credit
            available_credit=Decimal("5000.00"),
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(customer)
        return customer

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

    def test_full_payment_does_not_use_credit_automatically(
        self, db_session: Session, test_user: User, test_category: Category
    ):
        """Test that paying in full doesn't automatically use customer credit."""
        # Create customer with credit first
        customer_with_credit = self.customer_with_credit(db_session, test_user)

        # Initial balance: -$5000 (credit)
        initial_balance = customer_with_credit.account.account_balance
        assert initial_balance == Decimal("-5000.00")

        # Create a product for testing
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

        # Create a sale for $1000
        sale_data = SaleCreate(
            customer_id=customer_with_credit.id,
            items=[
                SaleItemCreate(
                    product_id=product.id,
                    quantity=1,
                    is_custom_price=False,
                )
            ],
            payment_method="cash",
            cash_amount=Decimal("1000.00"),
            amount_paid=Decimal("1000.00"),
        )

        # Create the sale
        sale = sale_crud.create(db=db_session, sale=sale_data, user_id=test_user.id)

        # Refresh customer to get updated balance
        db_session.refresh(customer_with_credit)

        # Assert: Customer credit should remain unchanged
        # The full payment should NOT deduct from credit
        assert customer_with_credit.account.account_balance == Decimal("-5000.00"), (
            f"Customer credit changed from {initial_balance} to {customer_with_credit.account.account_balance}. "
            "Credit should not be used when payment is made in full."
        )

        # Assert: Sale should be fully paid
        assert sale.paid_amount == Decimal("1000.00")
        assert sale.total_amount == Decimal("1000.00")

    def test_partial_payment_still_creates_debt(
        self, db_session: Session, test_user: User, test_category: Category
    ):
        """Test that partial payments create debt without using credit automatically."""
        # Create customer with credit first
        customer_with_credit = self.customer_with_credit(db_session, test_user)

        # Create a product for testing
        product = Product(
            name="Test Product 2",
            sku="TEST002",
            price=Decimal("2000.00"),
            stock_quantity=10,
            category_id=test_category.id,
            is_active=True,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        # Create a sale for $2000, pay only $1500
        sale_data = SaleCreate(
            customer_id=customer_with_credit.id,
            items=[
                SaleItemCreate(
                    product_id=product.id,
                    quantity=1,
                    is_custom_price=False,
                )
            ],
            payment_method="cash",
            cash_amount=Decimal("1500.00"),
            amount_paid=Decimal("1500.00"),
        )

        # Create the sale
        sale_crud.create(db=db_session, sale=sale_data, user_id=test_user.id)

        # Refresh customer
        db_session.refresh(customer_with_credit)

        # Assert: Customer should have debt added, credit unchanged
        # Initial: -$5000 (credit)
        # After sale: -$5000 + $500 (debt) = -$4500
        assert customer_with_credit.account.account_balance == Decimal(
            "-4500.00"
        ), "Partial payment should create debt, not use credit automatically"

    def test_explicit_credit_usage(
        self, db_session: Session, test_user: User, test_category: Category
    ):
        """Test that credit is only used when explicitly requested."""
        # Create customer with credit first
        customer_with_credit = self.customer_with_credit(db_session, test_user)

        # Create a product for testing
        product = Product(
            name="Test Product 3",
            sku="TEST003",
            price=Decimal("1000.00"),
            stock_quantity=10,
            category_id=test_category.id,
            is_active=True,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        # Create a sale with explicit credit usage
        sale_data = SaleCreate(
            customer_id=customer_with_credit.id,
            items=[
                SaleItemCreate(
                    product_id=product.id,
                    quantity=1,
                    is_custom_price=False,
                )
            ],
            payment_method="mixed",  # Mixed payment to use credit
            cash_amount=Decimal("0.00"),
            credit_amount=Decimal("1000.00"),  # Explicitly using credit
            amount_paid=Decimal("1000.00"),
        )

        # Create the sale
        sale_crud.create(db=db_session, sale=sale_data, user_id=test_user.id)

        # Refresh customer
        db_session.refresh(customer_with_credit)

        # Assert: Credit should be reduced
        # Initial: -$5000, Used: $1000, Final: -$4000
        assert customer_with_credit.account.account_balance == Decimal(
            "-4000.00"
        ), "Credit should only be used when explicitly requested"

    def test_payment_create_does_not_auto_apply_credit(
        self, db_session: Session, test_user: User
    ):
        """Test that creating a payment doesn't automatically apply credit."""
        # Create customer with credit first
        customer_with_credit = self.customer_with_credit(db_session, test_user)

        # Create payment for customer account
        payment_data = PaymentCreate(
            customer_id=customer_with_credit.id,
            amount=Decimal("2000.00"),
            payment_method="cash",
            payment_type="payment",
            notes="Manual payment test",
        )

        # Process payment
        customer_service.create_payment(
            db=db_session, payment_data=payment_data, created_by=test_user.id
        )

        # Refresh customer
        db_session.refresh(customer_with_credit)

        # Assert: Payment should reduce debt, not consume credit
        # Initial: -$5000 (credit), Payment: -$2000, Final: -$7000
        assert customer_with_credit.account.account_balance == Decimal(
            "-7000.00"
        ), "Payment should increase credit, not be consumed by existing credit"
