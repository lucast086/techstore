"""Product pricing and inventory tests.

Tests cover FASE 3 from test coverage plan:
- Manual price override scenarios
- Multiple products in same sale
- Physical products vs services
- Stock validation
"""

from decimal import Decimal

import pytest
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.product import Category, Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from sqlalchemy.orm import Session


class TestProductPricing:
    """Test product pricing and multiple product scenarios."""

    @pytest.fixture
    def test_category(self, db_session: Session) -> Category:
        """Create a test category."""
        category = Category(
            name="Electronics",
            description="Electronic products",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def test_product(self, db_session: Session, test_category: Category) -> Product:
        """Create a test product with known price."""
        product = Product(
            sku="ELEC001",
            name="Laptop",
            category_id=test_category.id,
            purchase_price=Decimal("500.00"),
            first_sale_price=Decimal("1000.00"),
            second_sale_price=Decimal("900.00"),
            third_sale_price=Decimal("800.00"),
            tax_rate=Decimal("10.00"),  # 10% tax
            current_stock=50,
            minimum_stock=5,
            is_active=True,
            is_service=False,
            created_by=1,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    @pytest.fixture
    def test_product_2(self, db_session: Session, test_category: Category) -> Product:
        """Create a second test product."""
        product = Product(
            sku="ELEC002",
            name="Mouse",
            category_id=test_category.id,
            purchase_price=Decimal("10.00"),
            first_sale_price=Decimal("25.00"),
            second_sale_price=Decimal("20.00"),
            third_sale_price=Decimal("15.00"),
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
    def service_product(self, db_session: Session, test_category: Category) -> Product:
        """Create a service product (no stock tracking)."""
        product = Product(
            sku="SRV001",
            name="Computer Repair Service",
            category_id=test_category.id,
            purchase_price=Decimal("0.00"),
            first_sale_price=Decimal("50.00"),
            second_sale_price=Decimal("50.00"),
            third_sale_price=Decimal("50.00"),
            tax_rate=Decimal("10.00"),
            current_stock=0,  # Services don't track stock
            minimum_stock=0,
            is_active=True,
            is_service=True,  # This is a service
            created_by=1,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    @pytest.fixture
    def registered_customer(self, db_session: Session) -> Customer:
        """Create a registered customer."""
        customer = Customer(
            name="Jane Smith",
            phone="555-5678",
            email="jane@example.com",
            address="456 Oak St",
            is_active=True,
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        return customer

    @pytest.fixture
    def open_cash_register(self, db_session: Session, test_user: User):
        """Ensure cash register is open for testing."""
        from app.crud.cash_closing import cash_closing
        from app.utils.timezone import get_local_today

        register = cash_closing.open_cash_register(
            db_session,
            target_date=get_local_today(),
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()
        return register

    # ========================================
    # MANUAL PRICE OVERRIDE TESTS (3.1 - 3.5)
    # ========================================

    def test_manual_price_override_single_product(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 3.1: Modify price of a single product in cart.

        Scenario: Product catalog price is $1000, but we sell it for $950
        """
        # Product has first_sale_price = $1000
        # We override to $950
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Manual price override to $950",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("950.00"),  # Manual override
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("1045.00"),  # $950 + 10% tax = $1045
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify the manual price was used
        assert len(sale.items) == 1
        assert sale.items[0].unit_price == Decimal("950.00")
        assert sale.subtotal == Decimal("950.00")
        # Tax: $950 * 10% = $95
        assert sale.tax_amount == Decimal("95.00")
        # Total: $950 + $95 = $1045
        assert sale.total_amount == Decimal("1045.00")
        assert sale.payment_status == "paid"

    def test_manual_price_higher_than_original(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 3.2: Manual price higher than catalog price.

        Scenario: Catalog price $1000, but we sell for $1200 (premium customer)
        """
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Premium customer price",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("1200.00"),  # Higher than catalog
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("1320.00"),  # $1200 + 10% = $1320
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        assert sale.items[0].unit_price == Decimal("1200.00")
        assert sale.total_amount == Decimal("1320.00")

    def test_manual_price_lower_than_original(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 3.3: Manual price lower than catalog (discount).

        Scenario: Catalog $1000, sell for $700 (clearance)
        """
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Clearance sale",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("700.00"),  # Lower than catalog
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("770.00"),  # $700 + 10% = $770
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        assert sale.items[0].unit_price == Decimal("700.00")
        assert sale.subtotal == Decimal("700.00")
        assert sale.total_amount == Decimal("770.00")

    def test_manual_price_zero(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 3.4: Manual price of $0 (free product/giveaway).

        Scenario: Give away product for free (promotional)
        """
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Promotional giveaway",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("0.00"),  # Free
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("0.00"),
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        assert sale.items[0].unit_price == Decimal("0.00")
        assert sale.subtotal == Decimal("0.00")
        assert sale.tax_amount == Decimal("0.00")
        assert sale.total_amount == Decimal("0.00")

    def test_manual_price_with_tax_calculation(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 3.5: Verify tax calculation on manual price.

        Scenario: Manual price $850, verify 10% tax = $85, total = $935
        """
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Tax calculation test",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("850.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("935.00"),
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        assert sale.subtotal == Decimal("850.00")
        assert sale.tax_amount == Decimal("85.00")
        assert sale.total_amount == Decimal("935.00")

    # ========================================
    # MULTIPLE PRODUCTS TESTS (3.6 - 3.10)
    # ========================================

    def test_multiple_products_same_item(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 3.6: Multiple units of the same product.

        Scenario: Buy 5 laptops @ $1000 each
        """
        initial_stock = test_product.current_stock

        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Bulk purchase - 5 laptops",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=5,  # Buy 5 units
                    unit_price=Decimal("1000.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("5500.00"),  # 5 * $1000 * 1.10 = $5500
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify calculations
        assert len(sale.items) == 1
        assert sale.items[0].quantity == 5
        assert sale.subtotal == Decimal("5000.00")  # 5 * $1000
        assert sale.tax_amount == Decimal("500.00")  # 10% of $5000
        assert sale.total_amount == Decimal("5500.00")

        # Verify stock was reduced
        db_session.refresh(test_product)
        assert test_product.current_stock == initial_stock - 5

    def test_multiple_different_products(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        test_product_2: Product,
        open_cash_register,
    ):
        """Test 3.7: Multiple different products in one sale.

        Scenario: Buy 1 laptop ($1000) + 2 mice ($25 each)
        """
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Mixed products sale",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,  # Laptop
                    quantity=1,
                    unit_price=Decimal("1000.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                ),
                SaleItemCreate(
                    product_id=test_product_2.id,  # Mouse
                    quantity=2,
                    unit_price=Decimal("25.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                ),
            ],
            amount_paid=Decimal("1155.00"),  # ($1000 + $50) * 1.10 = $1155
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify multiple items
        assert len(sale.items) == 2
        assert sale.subtotal == Decimal("1050.00")  # $1000 + $50
        assert sale.tax_amount == Decimal("105.00")  # 10%
        assert sale.total_amount == Decimal("1155.00")

    def test_mixed_physical_and_service_products(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        service_product: Product,
        open_cash_register,
    ):
        """Test 3.8: Mix physical products and services.

        Scenario: Laptop ($1000) + Repair Service ($50)
        """
        initial_laptop_stock = test_product.current_stock

        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Product + Service",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,  # Physical product
                    quantity=1,
                    unit_price=Decimal("1000.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                ),
                SaleItemCreate(
                    product_id=service_product.id,  # Service
                    quantity=1,
                    unit_price=Decimal("50.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                ),
            ],
            amount_paid=Decimal("1155.00"),  # ($1000 + $50) * 1.10
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify sale
        assert len(sale.items) == 2
        assert sale.total_amount == Decimal("1155.00")

        # Verify stock: laptop reduced, service unchanged
        db_session.refresh(test_product)
        db_session.refresh(service_product)
        assert test_product.current_stock == initial_laptop_stock - 1
        assert service_product.current_stock == 0  # Services don't track stock

    def test_product_without_sufficient_stock(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 3.9: Attempt to sell more than available stock (should fail).

        Scenario: Product has 50 in stock, try to sell 100
        """
        # Product has 50 units in stock
        assert test_product.current_stock == 50

        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Oversell attempt",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=100,  # More than available
                    unit_price=Decimal("1000.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("110000.00"),
        )

        # Should raise error
        with pytest.raises(ValueError) as excinfo:
            sale_crud.create_sale(
                db=db_session, sale_in=sale_data, user_id=test_user.id
            )

        assert "Insufficient stock" in str(excinfo.value)

    def test_service_product_no_stock_validation(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        service_product: Product,
        open_cash_register,
    ):
        """Test 3.10: Services ignore stock validation.

        Scenario: Service product with 0 stock can be sold any quantity
        """
        # Service has 0 stock but is_service=True
        assert service_product.current_stock == 0
        assert service_product.is_service is True

        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Multiple services",
            items=[
                SaleItemCreate(
                    product_id=service_product.id,
                    quantity=10,  # Can sell any quantity for services
                    unit_price=Decimal("50.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("550.00"),  # 10 * $50 * 1.10 = $550
        )

        # Should succeed (services don't check stock)
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        assert sale.total_amount == Decimal("550.00")
        assert sale.payment_status == "paid"
