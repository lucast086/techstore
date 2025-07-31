"""Tests for sales functionality."""

from datetime import datetime
from decimal import Decimal

import pytest
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.product import Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from sqlalchemy.orm import Session


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test_cashier@example.com",
        password_hash="hashed_password",
        full_name="Test Cashier",
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
        name="Test Customer",
        phone="1234567890",
        email="customer@example.com",
        created_by_id=test_user.id,
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def test_products(db_session: Session, test_user: User) -> list[Product]:
    """Create test products."""
    # Create a category first
    from app.models.product import Category

    category = Category(
        name="Electronics",
        description="Electronic products",
    )
    db_session.add(category)
    db_session.commit()

    products = [
        Product(
            sku="PROD001",
            name="Test Product 1",
            category_id=category.id,
            purchase_price=Decimal("50.00"),
            first_sale_price=Decimal("100.00"),
            second_sale_price=Decimal("95.00"),
            third_sale_price=Decimal("90.00"),
            current_stock=10,
            minimum_stock=2,
            created_by=test_user.id,
        ),
        Product(
            sku="PROD002",
            name="Test Product 2",
            category_id=category.id,
            purchase_price=Decimal("30.00"),
            first_sale_price=Decimal("60.00"),
            second_sale_price=Decimal("55.00"),
            third_sale_price=Decimal("50.00"),
            current_stock=5,
            minimum_stock=1,
            created_by=test_user.id,
        ),
    ]

    for product in products:
        db_session.add(product)

    db_session.commit()
    return products


class TestSaleCRUD:
    """Test CRUD operations for sales."""

    def test_generate_invoice_number(self, db_session: Session):
        """Test invoice number generation."""
        invoice_number = sale_crud.generate_invoice_number(db_session)

        assert invoice_number.startswith(f"INV-{datetime.now().year}-")
        assert len(invoice_number) == 14  # INV-YYYY-00001

    def test_create_cash_sale(
        self, db_session: Session, test_user: User, test_products: list[Product]
    ):
        """Test creating a cash sale."""
        sale_data = SaleCreate(
            payment_method="cash",
            items=[
                SaleItemCreate(
                    product_id=test_products[0].id,
                    quantity=2,
                    unit_price=test_products[0].first_sale_price,
                ),
                SaleItemCreate(
                    product_id=test_products[1].id,
                    quantity=1,
                    unit_price=test_products[1].first_sale_price,
                ),
            ],
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        assert sale.invoice_number.startswith("INV-")
        assert sale.user_id == test_user.id
        assert sale.payment_method == "cash"
        assert sale.payment_status == "paid"
        assert len(sale.items) == 2
        assert sale.subtotal == Decimal("260.00")  # (100*2) + (60*1)
        # Tax would be calculated on each product's tax rate
        # For now we're using flat 16% tax rate
        expected_tax = Decimal("260.00") * Decimal("0.16")
        assert sale.tax_amount == expected_tax  # 16% tax
        assert sale.total_amount == Decimal("260.00") + expected_tax

        # Check inventory was updated
        db_session.refresh(test_products[0])
        db_session.refresh(test_products[1])
        assert test_products[0].current_stock == 8  # 10 - 2
        assert test_products[1].current_stock == 4  # 5 - 1

    def test_create_credit_sale(
        self,
        db_session: Session,
        test_user: User,
        test_customer: Customer,
        test_products: list[Product],
    ):
        """Test creating a credit sale."""
        sale_data = SaleCreate(
            customer_id=test_customer.id,
            payment_method="credit",
            items=[
                SaleItemCreate(
                    product_id=test_products[0].id,
                    quantity=1,
                    unit_price=test_products[0].first_sale_price,
                ),
            ],
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        assert sale.customer_id == test_customer.id
        assert sale.payment_method == "credit"
        assert sale.payment_status == "pending"
        assert sale.amount_due == sale.total_amount

    def test_create_sale_with_discount(
        self, db_session: Session, test_user: User, test_products: list[Product]
    ):
        """Test creating a sale with discounts."""
        sale_data = SaleCreate(
            payment_method="cash",
            discount_amount=Decimal("10.00"),  # Sale-level discount
            items=[
                SaleItemCreate(
                    product_id=test_products[0].id,
                    quantity=1,
                    unit_price=test_products[0].first_sale_price,
                    discount_percentage=Decimal("10.00"),  # 10% item discount
                ),
            ],
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Item: 100 - 10% = 90
        # Sale discount: 10
        # Subtotal after discounts: 90 - 10 = 80
        # Tax: 80 * 0.16 = 12.80
        # Total: 80 + 12.80 = 92.80
        assert sale.items[0].total_price == Decimal("90.00")
        assert sale.discount_amount == Decimal("10.00")
        expected_total = (Decimal("90.00") - Decimal("10.00")) * Decimal("1.16")
        assert sale.total_amount == expected_total

    def test_create_sale_insufficient_stock(
        self, db_session: Session, test_user: User, test_products: list[Product]
    ):
        """Test creating a sale with insufficient stock."""
        sale_data = SaleCreate(
            payment_method="cash",
            items=[
                SaleItemCreate(
                    product_id=test_products[0].id,
                    quantity=20,  # More than available (10)
                    unit_price=test_products[0].first_sale_price,
                ),
            ],
        )

        with pytest.raises(ValueError, match="Insufficient stock"):
            sale_crud.create_sale(
                db=db_session, sale_in=sale_data, user_id=test_user.id
            )

    def test_void_sale(
        self, db_session: Session, test_user: User, test_products: list[Product]
    ):
        """Test voiding a sale."""
        # Create a sale first
        sale_data = SaleCreate(
            payment_method="cash",
            items=[
                SaleItemCreate(
                    product_id=test_products[0].id,
                    quantity=2,
                    unit_price=test_products[0].first_sale_price,
                ),
            ],
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Check stock was reduced
        db_session.refresh(test_products[0])
        assert test_products[0].current_stock == 8

        # Void the sale
        voided_sale = sale_crud.void_sale(
            db=db_session,
            sale_id=sale.id,
            reason="Test void reason",
            user_id=test_user.id,
        )

        assert voided_sale.is_voided is True
        assert voided_sale.void_reason == "Test void reason"
        assert voided_sale.payment_status == "voided"

        # Check stock was restored
        db_session.refresh(test_products[0])
        assert test_products[0].current_stock == 10

    def test_search_products(self, db_session: Session, test_products: list[Product]):
        """Test product search for POS."""
        # Search by name
        results = sale_crud.search_products(db_session, query="Test Product")
        assert len(results) == 2

        # Search by SKU
        results = sale_crud.search_products(db_session, query="PROD001")
        assert len(results) == 1
        assert results[0].sku == "PROD001"

    def test_get_sales_summary(
        self, db_session: Session, test_user: User, test_products: list[Product]
    ):
        """Test sales summary calculation."""
        # Create multiple sales
        for i in range(3):
            sale_data = SaleCreate(
                payment_method="cash" if i < 2 else "credit",
                items=[
                    SaleItemCreate(
                        product_id=test_products[0].id,
                        quantity=1,
                        unit_price=Decimal("100.00"),
                    ),
                ],
            )
            sale_crud.create_sale(
                db=db_session, sale_in=sale_data, user_id=test_user.id
            )

        summary = sale_crud.get_sales_summary(db_session)

        assert summary["total_count"] == 3
        # Each sale is 100 + 16% tax = 116
        expected_per_sale = Decimal("100.00") * Decimal("1.16")
        assert summary["total_sales"] == expected_per_sale * 3
        assert summary["cash_sales"] == expected_per_sale * 2
        assert summary["credit_sales"] == expected_per_sale
        assert summary["average_sale"] == expected_per_sale
