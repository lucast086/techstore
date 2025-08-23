"""Tests for POS web interface sales functionality."""

from decimal import Decimal

import pytest
from app.models.customer import Customer
from app.models.product import Category, Product
from app.models.sale import Sale
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="pos_test@example.com",
        password_hash="hashed_password",
        full_name="POS Test User",
        role="technician",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_customer(db_session: Session, test_user: User) -> Customer:
    """Create a test customer."""
    customer = Customer(
        name="POS Test Customer",
        phone="5551234567",
        email="pos_customer@example.com",
        account_balance=Decimal("0"),
        created_by_id=test_user.id,
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def test_product(db_session: Session, test_user: User) -> Product:
    """Create a test product."""
    # Create category first
    category = Category(
        name="Test Category",
        description="Category for testing",
    )
    db_session.add(category)
    db_session.commit()

    product = Product(
        name="Test POS Product",
        sku="POS001",
        category_id=category.id,
        current_stock=50,
        minimum_stock=5,
        first_cost=Decimal("50.00"),
        first_sale_price=Decimal("100.00"),
        created_by_id=test_user.id,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def authenticated_client(
    test_client: TestClient, test_user: User, db_session: Session
) -> TestClient:
    """Create an authenticated test client."""
    # Set up authentication cookie
    test_client.cookies.set("access_token", f"test_token_{test_user.id}")
    return test_client


class TestPOSWebInterface:
    """Test POS web interface functionality."""

    def test_pos_form_default_amount_received_is_zero(
        self, authenticated_client: TestClient, test_product: Product
    ):
        """Test that POS form has amount_received defaulting to 0."""
        response = authenticated_client.get("/sales/pos")
        assert response.status_code == 200

        # Check that the form contains the amount_received field with value="0"
        assert 'id="amount_received"' in response.text
        assert 'value="0"' in response.text
        assert 'name="amount_received"' in response.text

    def test_checkout_with_zero_amount_received(
        self,
        authenticated_client: TestClient,
        db_session: Session,
        test_customer: Customer,
        test_product: Product,
    ):
        """Test checkout with amount_received = 0 creates partial payment."""
        # Prepare form data for checkout
        form_data = {
            "customer_id": str(test_customer.id),
            "payment_method": "cash",
            "amount_received": "0",  # Explicitly set to 0
            "product_id_0": str(test_product.id),
            "product_name_0": test_product.name,
            "quantity_0": "1",
            "unit_price_0": "100.00",
            "notes": "Test sale with zero payment",
        }

        response = authenticated_client.post(
            "/sales/pos/checkout",
            data=form_data,
            follow_redirects=False,
        )

        # Should redirect after successful sale
        assert response.status_code in [302, 303]

        # Verify sale was created with partial payment
        sale = (
            db_session.query(Sale).filter(Sale.customer_id == test_customer.id).first()
        )

        assert sale is not None
        assert sale.amount_paid == Decimal("0")
        assert sale.payment_status == "partial"

        # Total should be 100 + 16% tax = 116
        expected_total = Decimal("100.00") * Decimal("1.16")
        assert sale.total_amount == expected_total
        assert sale.amount_due == expected_total

        # Verify customer balance shows debt
        db_session.refresh(test_customer)
        assert test_customer.account_balance == -expected_total

    def test_checkout_without_amount_received_defaults_to_zero(
        self,
        authenticated_client: TestClient,
        db_session: Session,
        test_customer: Customer,
        test_product: Product,
    ):
        """Test checkout without specifying amount_received defaults to 0."""
        # Prepare form data without amount_received
        form_data = {
            "customer_id": str(test_customer.id),
            "payment_method": "cash",
            # Not including amount_received field
            "product_id_0": str(test_product.id),
            "product_name_0": test_product.name,
            "quantity_0": "2",
            "unit_price_0": "100.00",
            "notes": "Test sale without amount specified",
        }

        response = authenticated_client.post(
            "/sales/pos/checkout",
            data=form_data,
            follow_redirects=False,
        )

        # Should redirect after successful sale
        assert response.status_code in [302, 303]

        # Verify sale was created
        sale = (
            db_session.query(Sale).filter(Sale.customer_id == test_customer.id).first()
        )

        assert sale is not None

        # Total should be 200 + 16% tax = 232
        expected_total = Decimal("200.00") * Decimal("1.16")

        # With our fix, amount_paid should be 0 when not specified
        assert sale.amount_paid == Decimal("0")
        assert sale.payment_status == "partial"
        assert sale.amount_due == expected_total

        # Verify customer balance shows debt
        db_session.refresh(test_customer)
        assert test_customer.account_balance == -expected_total
