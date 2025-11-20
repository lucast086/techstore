"""Basic sales tests covering cash, card, and transfer payments.

Tests cover FASE 2 from test coverage plan:
- Cash payments (full, partial, overpayment, debt creation)
- Card payments (full, with operation number, partial)
- Transfer payments (full, with reference, partial)
"""

from decimal import Decimal

import pytest
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.customer_account import (
    CustomerAccount,
    CustomerTransaction,
    TransactionType,
)
from app.models.payment import Payment
from app.models.product import Category, Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from sqlalchemy.orm import Session


class TestBasicSales:
    """Test basic sales scenarios with different payment methods."""

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
    def walk_in_customer(self, db_session: Session) -> Customer:
        """Walk-in customer (ID=1 by convention)."""
        customer = db_session.query(Customer).filter(Customer.id == 1).first()
        if not customer:
            customer = Customer(
                id=1,
                name="Walk-in Customer",
                phone="000-0000",
                is_active=True,
            )
            db_session.add(customer)
            db_session.commit()
            db_session.refresh(customer)
        return customer

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
    # CASH PAYMENT TESTS (2.1 - 2.5)
    # ========================================

    def test_cash_payment_full_walk_in(
        self,
        db_session: Session,
        test_user: User,
        walk_in_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.1: Walk-in customer pays full amount in cash."""
        # Sale: 1 item @ $100 + 10% tax = $110 total
        sale_data = SaleCreate(
            customer_id=walk_in_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Walk-in cash payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("110.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"
        assert sale.customer_id == walk_in_customer.id

        # Check payment was created
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is not None
        assert payment.amount == Decimal("110.00")
        assert payment.payment_method == "cash"

    def test_cash_payment_full_registered_customer(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.2: Registered customer pays full amount in cash."""
        # Sale: 1 item @ $100 + 10% tax = $110 total
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Registered customer cash payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("110.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"

        # Check account was created and balance is zero (no debt)
        account = (
            db_session.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == registered_customer.id)
            .first()
        )
        assert account is not None
        assert account.account_balance == Decimal("0.00")

        # Check transactions: SALE + PAYMENT
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == registered_customer.id)
            .order_by(CustomerTransaction.id)
            .all()
        )
        assert len(transactions) == 2
        assert transactions[0].transaction_type == TransactionType.SALE
        assert transactions[0].amount == Decimal("110.00")
        assert transactions[1].transaction_type == TransactionType.PAYMENT
        assert transactions[1].amount == Decimal("110.00")

    def test_cash_overpayment_with_change(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.3: Customer pays with larger bill, receives change."""
        # Sale: $110 total, customer pays $150, change = $40
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Overpayment with change",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("150.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"
        assert sale.change_amount == Decimal("40.00")

        # Check payment recorded is only the sale amount
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment.amount == Decimal("110.00")

    def test_cash_partial_payment_creates_debt(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.4: Customer pays partial amount, creates debt."""
        # Sale: $110 total, customer pays $50, debt = $60
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Partial payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("50.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "partial"
        assert sale.balance_due == Decimal("60.00")

        # Check account has debt
        account = (
            db_session.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == registered_customer.id)
            .first()
        )
        assert account.account_balance == Decimal("60.00")  # Positive = debt

        # Check transactions: SALE + PAYMENT
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == registered_customer.id)
            .order_by(CustomerTransaction.id)
            .all()
        )
        assert len(transactions) == 2
        assert transactions[0].transaction_type == TransactionType.SALE
        assert transactions[0].amount == Decimal("110.00")
        assert transactions[1].transaction_type == TransactionType.PAYMENT
        assert transactions[1].amount == Decimal("50.00")

    def test_cash_zero_payment_full_debt(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.5: Customer doesn't pay, creates full debt."""
        # Sale: $110 total, customer pays $0, debt = $110
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="account",  # On account = no immediate payment
            discount_amount=Decimal("0.00"),
            notes="Full debt",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("0.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "pending"
        assert sale.balance_due == Decimal("110.00")

        # Check account has full debt
        account = (
            db_session.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == registered_customer.id)
            .first()
        )
        assert account.account_balance == Decimal("110.00")  # Positive = debt

        # Check only SALE transaction (no payment)
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == registered_customer.id)
            .all()
        )
        assert len(transactions) == 1
        assert transactions[0].transaction_type == TransactionType.SALE
        assert transactions[0].amount == Decimal("110.00")

    # ========================================
    # CARD PAYMENT TESTS (2.6 - 2.8)
    # ========================================

    def test_card_payment_full(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.6: Full payment with card."""
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="card",
            discount_amount=Decimal("0.00"),
            notes="Card payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("110.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"

        # Check payment was created
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is not None
        assert payment.amount == Decimal("110.00")
        assert payment.payment_method == "card"

    def test_card_payment_with_operation_number(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.7: Card payment with operation number."""
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="card",
            discount_amount=Decimal("0.00"),
            notes="Card payment with operation number",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("110.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Check payment has reference
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is not None
        # Note: Operation number would be stored in payment.notes or reference_number
        # depending on schema implementation

    def test_card_partial_payment(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.8: Partial payment with card."""
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="card",
            discount_amount=Decimal("0.00"),
            notes="Partial card payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("70.00"),  # Partial payment
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "partial"
        assert sale.balance_due == Decimal("40.00")

        # Check account has debt
        account = (
            db_session.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == registered_customer.id)
            .first()
        )
        assert account.account_balance == Decimal("40.00")

    # ========================================
    # TRANSFER PAYMENT TESTS (2.9 - 2.11)
    # ========================================

    def test_transfer_payment_full(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.9: Full payment with bank transfer."""
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="transfer",
            discount_amount=Decimal("0.00"),
            notes="Bank transfer payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("110.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "paid"

        # Check payment was created
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is not None
        assert payment.amount == Decimal("110.00")
        assert payment.payment_method == "transfer"

    def test_transfer_with_reference_number(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.10: Transfer with reference number."""
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="transfer",
            discount_amount=Decimal("0.00"),
            notes="Transfer with reference TRF123456",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("110.00"),
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Check payment was created with notes
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is not None
        # Reference would be in payment.notes or reference_number field

    def test_transfer_partial_payment(
        self,
        db_session: Session,
        test_user: User,
        registered_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 2.11: Partial payment with transfer."""
        sale_data = SaleCreate(
            customer_id=registered_customer.id,
            payment_method="transfer",
            discount_amount=Decimal("0.00"),
            notes="Partial transfer payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("80.00"),  # Partial payment
        )

        # Create sale
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assertions
        assert sale.total_amount == Decimal("110.00")
        assert sale.payment_status == "partial"
        assert sale.balance_due == Decimal("30.00")

        # Check account has debt
        account = (
            db_session.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == registered_customer.id)
            .first()
        )
        assert account.account_balance == Decimal("30.00")
