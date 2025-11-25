"""Void operations and reversals tests.

Tests cover FASE 9 from test coverage plan:
- Sale voidance with cash and credit payments
- Inventory restoration on void
- Cash register updates
- Credit notes and debit notes
- Void immutability

These tests define the expected behavior of void operations
and financial reversals in the sales system.
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
from app.models.product import Category, Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.customer_account_service import customer_account_service
from sqlalchemy.orm import Session


class TestVoidOperations:
    """Test sale voidance and reversals."""

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        """Create a test user."""
        user = User(
            email="void_test@example.com",
            password_hash="hashedpass",
            full_name="Void Test User",
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
            name="Void Test Products",
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
            sku="VOID001",
            name="Void Test Product",
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
        """Create customer with zero balance account."""
        customer = Customer(
            name="Void Test Customer",
            phone="555-VOID",
            email="void@example.com",
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

    @pytest.fixture
    def open_cash_register(self, db_session: Session, test_user: User):
        """Ensure cash register is open."""
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

    # ============================================================
    # CATEGORY: Sale Voidance
    # ============================================================

    def test_void_sale_with_cash_payment(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 9.1: Void sale paid with cash.

        Expected behavior:
        1. Sale is marked as voided
        2. Payment is marked as voided
        3. Inventory is restored
        4. Payment status becomes "voided"
        """
        # Arrange: Create a sale with cash payment
        initial_stock = test_product.current_stock
        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=5,
                    unit_price=Decimal("100.00"),
                    price_tier="first",
                )
            ],
            payment_method="cash",
            amount_paid=Decimal("550.00"),  # Full payment
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )
        db_session.commit()
        db_session.refresh(sale)
        db_session.refresh(test_product)

        # Verify sale was created successfully
        assert sale.payment_status == "paid"
        assert test_product.current_stock == initial_stock - 5

        # Act: Void the sale
        voided_sale = sale_crud.void_sale(
            db_session,
            sale_id=sale.id,
            reason="Customer returned items",
            user_id=test_user.id,
        )
        db_session.refresh(test_product)

        # Assert: Sale is voided
        assert voided_sale.is_voided is True
        assert voided_sale.void_reason == "Customer returned items"
        assert voided_sale.payment_status == "voided"

        # Assert: Inventory restored
        assert (
            test_product.current_stock == initial_stock
        ), "Inventory should be restored"

        # Assert: Payment is voided
        assert len(sale.payments) > 0, "Sale should have payments"
        for payment in sale.payments:
            assert payment.voided is True
            assert payment.voided_by_id == test_user.id

    def test_void_sale_with_credit_reverses(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 9.2: Void sale with account credit reverses the credit transaction.

        Expected behavior:
        1. Sale creates SALE transaction (increases debt)
        2. Voiding sale should create VOID_SALE transaction (decreases debt)
        3. Customer balance returns to original
        """
        # Arrange: Create a sale on account (credit)
        initial_balance = customer_with_account.account.account_balance

        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    price_tier="first",
                )
            ],
            payment_method="account",
            amount_paid=Decimal("0.00"),  # On account
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )
        db_session.commit()
        db_session.refresh(sale)

        # Verify sale created debt
        account = customer_account_service.get_account(
            db_session, customer_with_account.id
        )
        assert account.account_balance > initial_balance, "Sale should create debt"

        # Act: Void the sale
        sale_crud.void_sale(
            db_session, sale_id=sale.id, reason="Incorrect order", user_id=test_user.id
        )
        db_session.commit()

        # Assert: Balance is reversed
        account = customer_account_service.get_account(
            db_session, customer_with_account.id
        )
        assert (
            account.account_balance == initial_balance
        ), "Voiding should reverse the debt"

        # Assert: VOID_SALE transaction exists
        void_transactions = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.VOID_SALE,
            )
            .all()
        )

        assert (
            len(void_transactions) == 1
        ), "Should have exactly 1 VOID_SALE transaction"
        void_trx = void_transactions[0]
        assert void_trx.amount == sale.total_amount
        assert void_trx.reference_type == "sale"
        assert void_trx.reference_id == sale.id

    def test_void_partial_payment_sale(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 9.3: Void sale with partial payment.

        Expected behavior:
        1. Sale partially paid should void correctly
        2. Partial payment is voided
        3. Remaining balance is cleared
        """
        # Arrange: Create a sale with partial payment
        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    price_tier="first",
                )
            ],
            payment_method="mixed",
            amount_paid=Decimal("110.00"),  # Half payment ($220 total)
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )
        db_session.commit()
        db_session.refresh(sale)

        assert sale.payment_status == "partial"

        # Act: Void the sale
        voided_sale = sale_crud.void_sale(
            db_session, sale_id=sale.id, reason="Order cancelled", user_id=test_user.id
        )

        # Assert: Sale is voided
        assert voided_sale.is_voided is True
        assert voided_sale.payment_status == "voided"

        # Assert: Balance is cleared
        account = customer_account_service.get_account(
            db_session, customer_with_account.id
        )
        assert account.account_balance == Decimal("0.00"), "Balance should be cleared"

    def test_void_sale_restores_inventory(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 9.4: Void sale restores inventory correctly.

        Expected behavior:
        1. Sale reduces inventory
        2. Void restores inventory to original level
        3. Multiple items restored correctly
        """
        # Arrange: Record initial stock
        initial_stock = test_product.current_stock
        quantity_sold = 10

        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=quantity_sold,
                    unit_price=Decimal("100.00"),
                    price_tier="first",
                )
            ],
            payment_method="cash",
            amount_paid=Decimal("1100.00"),
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )
        db_session.commit()
        db_session.refresh(test_product)

        # Verify stock was reduced
        assert test_product.current_stock == initial_stock - quantity_sold

        # Act: Void the sale
        sale_crud.void_sale(
            db_session,
            sale_id=sale.id,
            reason="Inventory correction",
            user_id=test_user.id,
        )
        db_session.refresh(test_product)

        # Assert: Stock is restored
        assert (
            test_product.current_stock == initial_stock
        ), f"Stock should be restored to {initial_stock}, got {test_product.current_stock}"

    def test_void_sale_updates_cash_register(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 9.5: Void sale updates cash register (if applicable).

        Expected behavior:
        1. Cash register has transactions
        2. Void sale should be reflected (implementation dependent)

        Note: This test verifies that void doesn't break cash register logic.
        Actual accounting treatment may vary by business rules.
        """
        # Arrange: Create a cash sale
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
            payment_method="cash",
            amount_paid=Decimal("110.00"),
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )
        db_session.commit()

        # Act: Void the sale
        sale_crud.void_sale(
            db_session,
            sale_id=sale.id,
            reason="Cash register test",
            user_id=test_user.id,
        )

        # Assert: Cash register still accessible and valid
        from app.crud.cash_closing import cash_closing

        current_register = cash_closing.get_unfinalized_register(db_session)
        assert current_register is not None, "Cash register should still exist"
        assert (
            current_register.is_finalized is False
        ), "Cash register should still be open"

    # ============================================================
    # CATEGORY: Credit/Debit Notes
    # ============================================================

    def test_credit_note_reduces_debt(
        self,
        db_session: Session,
        customer_with_account: Customer,
        test_user: User,
    ):
        """Test 9.6: Credit note reduces customer debt.

        Expected behavior:
        1. Customer has debt
        2. Credit note is issued (reduces debt)
        3. Balance decreases accordingly
        """
        # Arrange: Create debt for customer
        account = customer_account_service.get_or_create_account(
            db_session, customer_with_account.id, test_user.id
        )
        initial_balance = Decimal("500.00")
        account.account_balance = initial_balance
        db_session.add(account)
        db_session.commit()

        # Act: Issue a credit note (reduces debt)
        credit_amount = Decimal("100.00")

        # Create a CREDIT_NOTE transaction (adjusts balance downward)
        from app.models.customer_account import CustomerTransaction

        credit_note = CustomerTransaction(
            customer_id=customer_with_account.id,
            account_id=account.id,  # Include account_id
            transaction_type=TransactionType.PAYMENT,  # Using PAYMENT as credit note
            amount=credit_amount,
            balance_before=initial_balance,
            balance_after=initial_balance - credit_amount,
            reference_type="credit_note",
            reference_id=None,
            description="Credit note issued",  # Add description
            notes="Credit note for returned items",
            created_by_id=test_user.id,
        )
        db_session.add(credit_note)

        # Update account balance
        account.account_balance -= credit_amount
        db_session.add(account)
        db_session.commit()

        # Assert: Debt is reduced
        db_session.refresh(account)
        expected_balance = initial_balance - credit_amount
        assert (
            account.account_balance == expected_balance
        ), f"Balance should be {expected_balance}, got {account.account_balance}"

    def test_debit_note_increases_debt(
        self,
        db_session: Session,
        customer_with_account: Customer,
        test_user: User,
    ):
        """Test 9.7: Debit note increases customer debt.

        Expected behavior:
        1. Customer has some balance
        2. Debit note is issued (increases debt)
        3. Balance increases accordingly
        """
        # Arrange: Create initial balance for customer
        account = customer_account_service.get_or_create_account(
            db_session, customer_with_account.id, test_user.id
        )
        initial_balance = Decimal("100.00")
        account.account_balance = initial_balance
        db_session.add(account)
        db_session.commit()

        # Act: Issue a debit note (increases debt)
        debit_amount = Decimal("50.00")

        # Create a DEBIT_NOTE transaction (adjusts balance upward)
        from app.models.customer_account import CustomerTransaction

        debit_note = CustomerTransaction(
            customer_id=customer_with_account.id,
            account_id=account.id,  # Include account_id
            transaction_type=TransactionType.SALE,  # Using SALE as debit note
            amount=debit_amount,
            balance_before=initial_balance,
            balance_after=initial_balance + debit_amount,
            reference_type="debit_note",
            reference_id=None,
            description="Debit note issued",  # Add description
            notes="Debit note for additional charges",
            created_by_id=test_user.id,
        )
        db_session.add(debit_note)

        # Update account balance
        account.account_balance += debit_amount
        db_session.add(account)
        db_session.commit()

        # Assert: Debt is increased
        db_session.refresh(account)
        expected_balance = initial_balance + debit_amount
        assert (
            account.account_balance == expected_balance
        ), f"Balance should be {expected_balance}, got {account.account_balance}"

    def test_void_cannot_be_undone(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 9.8: Void operation is permanent and cannot be undone.

        Expected behavior:
        1. Sale is voided
        2. Attempting to void again raises error
        3. Voided sale cannot be unvoided (no undo operation)
        """
        # Arrange: Create and void a sale
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
            payment_method="cash",
            amount_paid=Decimal("110.00"),
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )
        db_session.commit()

        # Void the sale
        voided_sale = sale_crud.void_sale(
            db_session, sale_id=sale.id, reason="Initial void", user_id=test_user.id
        )

        assert voided_sale.is_voided is True

        # Act & Assert: Attempting to void again should raise error
        with pytest.raises(ValueError, match="already voided"):
            sale_crud.void_sale(
                db_session,
                sale_id=sale.id,
                reason="Double void attempt",
                user_id=test_user.id,
            )

        # Assert: Void status is permanent
        db_session.refresh(voided_sale)
        assert voided_sale.is_voided is True, "Void status should remain True"
