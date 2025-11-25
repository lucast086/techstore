"""Mixed payment method tests (without credit).

Tests cover FASE 2 mixed payments from test coverage plan:
- Cash + Card combination
- Cash + Transfer combination
- Card + Transfer combination
- Three method combination (Cash + Card + Transfer)

Note: These tests do NOT involve customer credit, only payment method combinations.
"""

from decimal import Decimal

import pytest
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.product import Category, Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from sqlalchemy.orm import Session


class TestMixedPayments:
    """Test mixed payment method scenarios (no credit involved)."""

    @pytest.fixture
    def test_category(self, db_session: Session) -> Category:
        """Create a test category."""
        category = Category(
            name="Test Products",
            description="Test category for unit tests",
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
            sku="PROD001",
            name="Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("50.00"),
            first_sale_price=Decimal("100.00"),
            second_sale_price=Decimal("100.00"),
            third_sale_price=Decimal("100.00"),
            tax_rate=Decimal("10.00"),  # 10% tax
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
    def registered_customer(self, db_session: Session) -> Customer:
        """Create a registered customer."""
        customer = Customer(
            name="John Doe",
            phone="555-1234",
            email="john@example.com",
            address="123 Main St",
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

        # Open cash register for today
        register = cash_closing.open_cash_register(
            db_session,
            target_date=get_local_today(),
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()
        return register

    # ========================================
    # MIXED PAYMENT TESTS (2.12 - 2.15)
    # ========================================

    def test_mixed_cash_and_card_full(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.12: Mixed payment - Cash + Card = Total.

        Scenario: Customer pays $60 cash + $50 card for $110 total
        """
        # Create sale with cash payment first
        # Note: Current system may need enhancement to support multiple payment methods
        # This test documents the expected behavior

        # Total: $110 (1 item @ $100 + 10% tax)
        # Payment: $60 cash + $50 card

        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",  # Primary payment method
            discount_amount=Decimal("0.00"),
            notes="Mixed payment: $60 cash + $50 card",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("60.00"),  # Cash portion
        )

        # Create sale (initially partial payment)
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Add second payment (card)
        from app.schemas.payment import PaymentCreate
        from app.services.payment_service import payment_service

        payment_data = PaymentCreate(
            amount=Decimal("50.00"),
            payment_method="card",
            reference_number="CARD123",
            notes="Second payment - card",
        )

        payment_service.process_payment(
            db=db_session,
            customer_id=registered_customer.id,
            sale_id=sale.id,
            payment_data=payment_data,
            user_id=test_user.id,
            allow_overpayment=True,
        )

        db_session.refresh(sale)

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"
        assert sale.balance_due == Decimal("0.00")

        # Check both payments exist
        payments = db_session.query(Payment).filter(Payment.sale_id == sale.id).all()
        assert len(payments) == 2

        payment_methods = [p.payment_method for p in payments]
        assert "cash" in payment_methods
        assert "card" in payment_methods

        total_paid = sum(p.amount for p in payments)
        assert total_paid == Decimal("110.00")

    def test_mixed_cash_and_transfer_full(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.13: Mixed payment - Cash + Transfer = Total.

        Scenario: Customer pays $40 cash + $70 transfer for $110 total
        """
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Mixed payment: $40 cash + $70 transfer",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("40.00"),  # Cash portion
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Add transfer payment
        from app.schemas.payment import PaymentCreate
        from app.services.payment_service import payment_service

        payment_data = PaymentCreate(
            amount=Decimal("70.00"),
            payment_method="transfer",
            reference_number="TRF789",
            notes="Transfer payment - TRF789",
        )

        payment_service.process_payment(
            db=db_session,
            customer_id=registered_customer.id,
            sale_id=sale.id,
            payment_data=payment_data,
            user_id=test_user.id,
            allow_overpayment=True,
        )

        db_session.refresh(sale)

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"

        # Check both payments
        payments = db_session.query(Payment).filter(Payment.sale_id == sale.id).all()
        assert len(payments) == 2

        payment_methods = [p.payment_method for p in payments]
        assert "cash" in payment_methods
        assert "transfer" in payment_methods

    def test_mixed_card_and_transfer_full(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.14: Mixed payment - Card + Transfer = Total.

        Scenario: Customer pays $55 card + $55 transfer for $110 total
        """
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="card",
            discount_amount=Decimal("0.00"),
            notes="Mixed payment: $55 card + $55 transfer",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("55.00"),  # Card portion
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Add transfer payment
        from app.schemas.payment import PaymentCreate
        from app.services.payment_service import payment_service

        payment_data = PaymentCreate(
            amount=Decimal("55.00"),
            payment_method="transfer",
            reference_number="TRF123",
            notes="Transfer payment",
        )

        payment_service.process_payment(
            db=db_session,
            customer_id=registered_customer.id,
            sale_id=sale.id,
            payment_data=payment_data,
            user_id=test_user.id,
            allow_overpayment=True,
        )

        db_session.refresh(sale)

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"

        # Check both payments
        payments = db_session.query(Payment).filter(Payment.sale_id == sale.id).all()
        assert len(payments) == 2

    def test_mixed_three_methods_full(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.15: Mixed payment - Cash + Card + Transfer = Total.

        Scenario: Customer pays $30 cash + $40 card + $40 transfer for $110 total
        """
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Mixed payment: $30 cash + $40 card + $40 transfer",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("30.00"),  # Cash portion
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Add card payment
        from app.schemas.payment import PaymentCreate
        from app.services.payment_service import payment_service

        payment_data_card = PaymentCreate(
            amount=Decimal("40.00"),
            payment_method="card",
            reference_number="CARD456",
            notes="Card payment",
        )

        payment_service.process_payment(
            db=db_session,
            customer_id=registered_customer.id,
            sale_id=sale.id,
            payment_data=payment_data_card,
            user_id=test_user.id,
            allow_overpayment=True,
        )

        # Add transfer payment
        payment_data_transfer = PaymentCreate(
            amount=Decimal("40.00"),
            payment_method="transfer",
            reference_number="TRF789",
            notes="Transfer payment",
        )

        payment_service.process_payment(
            db=db_session,
            customer_id=registered_customer.id,
            sale_id=sale.id,
            payment_data=payment_data_transfer,
            user_id=test_user.id,
            allow_overpayment=True,
        )

        db_session.refresh(sale)

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"

        # Check all three payments exist
        payments = db_session.query(Payment).filter(Payment.sale_id == sale.id).all()
        assert len(payments) == 3

        payment_methods = [p.payment_method for p in payments]
        assert "cash" in payment_methods
        assert "card" in payment_methods
        assert "transfer" in payment_methods

        total_paid = sum(p.amount for p in payments)
        assert total_paid == Decimal("110.00")
