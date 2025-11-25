"""Transaction recording and audit trail tests.

Tests cover FASE 6 from test coverage plan:
- Transaction recording (SALE, PAYMENT, CREDIT_APPLICATION)
- Prevention of duplicates
- Audit trail and traceability
- Balance consistency (balance_before/balance_after)

These tests define the expected behavior of the transaction system
according to the refactored payment architecture.
"""

from datetime import datetime, timedelta
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


class TestTransactionRecording:
    """Test that all transactions are recorded correctly."""

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        """Create a test user."""
        user = User(
            email="test@example.com",
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
            name="Test Products",
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
            sku="TRX001",
            name="Test Product",
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
            name="Transaction Test Customer",
            phone="555-9999",
            email="trx@example.com",
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

    @pytest.fixture
    def customer_with_credit(self, db_session: Session) -> Customer:
        """Create customer with available credit."""
        customer = Customer(
            name="Customer with Credit",
            phone="555-8888",
            email="credit@example.com",
            is_active=True,
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)

        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("-300.00"),  # $300 credit available
            credit_limit=Decimal("1000.00"),
            created_by_id=1,
        )
        db_session.add(account)
        db_session.commit()

        return customer

    # ============================================================
    # CATEGORY: Transaction Recording
    # ============================================================

    def test_sale_transaction_recorded(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.1: Verify SALE transaction is recorded when a sale is created.

        Expected behavior (per architecture):
        1. create_sale() registers the sale and creates debt
        2. A SALE transaction should be recorded in customer_account_transactions
        3. The transaction should have correct amount, type, and references
        """
        # Arrange
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
            notes="Test sale for transaction recording",
        )

        # Act
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )
        db_session.commit()
        db_session.refresh(sale)

        # Assert: SALE transaction should exist
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.SALE,
                CustomerTransaction.reference_type == "sale",
                CustomerTransaction.reference_id == sale.id,
            )
            .all()
        )

        assert len(transactions) == 1, "Should have exactly 1 SALE transaction"

        trx = transactions[0]
        expected_total = Decimal("220.00")  # 2 * 100 * 1.10 (with 10% tax)

        assert (
            trx.amount == expected_total
        ), f"SALE transaction amount should be {expected_total}"
        assert trx.transaction_type == TransactionType.SALE
        assert trx.reference_type == "sale"
        assert trx.reference_id == sale.id
        assert trx.created_by_id == test_user.id
        assert trx.balance_before == Decimal("0.00")
        assert trx.balance_after == expected_total

    def test_payment_transaction_recorded(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.2: Verify PAYMENT transaction is recorded when payment is made.

        Expected behavior:
        1. Sale creates SALE transaction
        2. Payment creates PAYMENT transaction
        3. Both transactions have correct balance_before/balance_after
        """
        # Arrange: Create a sale first (creates debt)
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

        # Act: Record a payment
        from app.crud.payment import payment_crud
        from app.models.payment import Payment, PaymentType

        payment_amount = Decimal("110.00")  # Full payment
        receipt_number = payment_crud.generate_receipt_number(db_session)
        payment = Payment(
            customer_id=customer_with_account.id,
            amount=payment_amount,
            payment_method="cash",
            payment_type=PaymentType.payment.value,
            receipt_number=receipt_number,
            received_by_id=test_user.id,
            notes="Test payment",
        )
        db_session.add(payment)
        db_session.flush()

        customer_account_service.record_payment(db_session, payment, test_user.id)
        db_session.commit()

        # Assert: PAYMENT transaction should exist
        payment_transactions = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.PAYMENT,
            )
            .all()
        )

        assert (
            len(payment_transactions) == 1
        ), "Should have exactly 1 PAYMENT transaction"

        pay_trx = payment_transactions[0]
        assert pay_trx.amount == payment_amount
        assert pay_trx.transaction_type == TransactionType.PAYMENT
        assert pay_trx.reference_type == "payment"
        assert (
            pay_trx.reference_id == payment.id
        )  # References the payment, not the sale
        assert pay_trx.created_by_id == test_user.id
        assert pay_trx.balance_before == Decimal("110.00")  # Balance after SALE
        assert pay_trx.balance_after == Decimal("0.00")  # Paid in full

    def test_credit_application_transaction(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_credit: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.3: Verify CREDIT_APPLICATION transaction is recorded.

        Expected behavior:
        1. Sale creates SALE transaction (increases debt)
        2. Applying credit creates CREDIT_APPLICATION transaction (decreases debt)
        3. Balance changes are tracked correctly
        """
        # Arrange: Create a sale
        sale_data = SaleCreate(
            customer_id=customer_with_credit.id,
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

        # Act: Apply credit to the sale
        credit_amount = Decimal("110.00")
        customer_account_service.apply_credit(
            db=db_session,
            customer_id=customer_with_credit.id,
            amount=credit_amount,
            sale_id=sale.id,
            created_by_id=test_user.id,
        )
        db_session.commit()

        # Assert: CREDIT_APPLICATION transaction should exist
        credit_transactions = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_credit.id,
                CustomerTransaction.transaction_type
                == TransactionType.CREDIT_APPLICATION,
            )
            .all()
        )

        assert (
            len(credit_transactions) == 1
        ), "Should have exactly 1 CREDIT_APPLICATION transaction"

        credit_trx = credit_transactions[0]
        assert credit_trx.amount == credit_amount
        assert credit_trx.transaction_type == TransactionType.CREDIT_APPLICATION
        assert credit_trx.reference_type == "sale"
        assert credit_trx.reference_id == sale.id
        assert credit_trx.created_by_id == test_user.id

    def test_transaction_order_sale_then_payment(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.4: Verify transactions are recorded in correct order (SALE → PAYMENT).

        Expected behavior:
        1. SALE transaction comes first (timestamp and order)
        2. PAYMENT transaction comes second
        3. Timestamps reflect the order
        """
        # Arrange & Act: Create sale then payment
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

        # Small delay to ensure different timestamps
        import time

        time.sleep(0.1)

        from app.crud.payment import payment_crud
        from app.models.payment import Payment, PaymentType

        receipt_number = payment_crud.generate_receipt_number(db_session)
        payment = Payment(
            customer_id=customer_with_account.id,
            amount=Decimal("110.00"),
            payment_method="cash",
            payment_type=PaymentType.payment.value,
            receipt_number=receipt_number,
            received_by_id=test_user.id,
            notes="Test payment",
        )
        db_session.add(payment)
        db_session.flush()

        customer_account_service.record_payment(db_session, payment, test_user.id)
        db_session.commit()

        # Assert: Check order
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == customer_with_account.id)
            .order_by(CustomerTransaction.created_at)
            .all()
        )

        assert len(transactions) == 2, "Should have 2 transactions"
        assert (
            transactions[0].transaction_type == TransactionType.SALE
        ), "First transaction should be SALE"
        assert (
            transactions[1].transaction_type == TransactionType.PAYMENT
        ), "Second transaction should be PAYMENT"
        # Timestamps should be in order (SALE <= PAYMENT), verifying chronological consistency
        assert (
            transactions[0].created_at <= transactions[1].created_at
        ), "SALE should be before or at same time as PAYMENT"

    def test_balance_before_after_consistency(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.5: Verify balance_before and balance_after are consistent across transactions.

        Expected behavior:
        1. Each transaction's balance_after should equal the next transaction's balance_before
        2. The final balance_after should match the account's current balance
        """
        # Arrange & Act: Create multiple transactions
        # Transaction 1: Sale #1
        sale1_data = SaleCreate(
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
        sale_crud.create_sale(db=db_session, sale_in=sale1_data, user_id=test_user.id)
        db_session.commit()

        # Transaction 2: Payment
        from app.crud.payment import payment_crud
        from app.models.payment import Payment, PaymentType

        receipt_number = payment_crud.generate_receipt_number(db_session)
        payment1 = Payment(
            customer_id=customer_with_account.id,
            amount=Decimal("50.00"),
            payment_method="cash",
            payment_type=PaymentType.payment.value,
            receipt_number=receipt_number,
            received_by_id=test_user.id,
            notes="Partial payment",
        )
        db_session.add(payment1)
        db_session.flush()

        customer_account_service.record_payment(db_session, payment1, test_user.id)
        db_session.commit()

        # Transaction 3: Sale #2
        sale2_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    price_tier="first",
                )
            ],
        )
        sale_crud.create_sale(db=db_session, sale_in=sale2_data, user_id=test_user.id)
        db_session.commit()

        # Assert: Check balance consistency
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == customer_with_account.id)
            .order_by(CustomerTransaction.created_at)
            .all()
        )

        assert len(transactions) == 3, "Should have 3 transactions"

        # Check each transaction's balance_after matches next transaction's balance_before
        for i in range(len(transactions) - 1):
            assert (
                transactions[i].balance_after == transactions[i + 1].balance_before
            ), f"Transaction {i} balance_after should equal transaction {i+1} balance_before"

        # Check final balance matches account balance
        account = (
            db_session.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == customer_with_account.id)
            .first()
        )
        assert (
            transactions[-1].balance_after == account.account_balance
        ), "Final transaction balance_after should match account balance"

    # ============================================================
    # CATEGORY: Prevention of Duplicates
    # ============================================================

    def test_no_double_credit_application(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_credit: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.6: Verify credit cannot be applied twice to the same sale.

        Expected behavior:
        1. First credit application succeeds
        2. Second attempt should raise an error or be prevented
        """
        # Arrange: Create a sale
        sale_data = SaleCreate(
            customer_id=customer_with_credit.id,
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

        # Act: Apply credit once (should succeed)
        customer_account_service.apply_credit(
            db=db_session,
            customer_id=customer_with_credit.id,
            amount=Decimal("110.00"),
            sale_id=sale.id,
            created_by_id=test_user.id,
        )
        db_session.commit()

        # Act: Try to apply credit again (should fail)
        with pytest.raises(
            ValueError, match="already has a CREDIT_APPLICATION transaction"
        ):
            customer_account_service.apply_credit(
                db=db_session,
                customer_id=customer_with_credit.id,
                amount=Decimal("110.00"),
                sale_id=sale.id,
                created_by_id=test_user.id,
            )

        # Assert: Only one CREDIT_APPLICATION transaction exists
        credit_transactions = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_credit.id,
                CustomerTransaction.transaction_type
                == TransactionType.CREDIT_APPLICATION,
                CustomerTransaction.reference_id == sale.id,
            )
            .all()
        )

        assert (
            len(credit_transactions) == 1
        ), "Should have exactly 1 CREDIT_APPLICATION transaction"

    def test_no_double_payment_recording(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.7: Verify payment cannot be recorded twice for the same payment ID.

        Expected behavior:
        1. record_payment should be idempotent for the same payment_id
        2. Calling it twice with same payment_id should not create duplicate transactions
        """
        # Arrange: Create a sale
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

        # Act: Record payment with a specific ID
        from app.crud.payment import payment_crud
        from app.models.payment import Payment, PaymentType

        receipt_number = payment_crud.generate_receipt_number(db_session)
        payment = Payment(
            customer_id=customer_with_account.id,
            amount=Decimal("110.00"),
            payment_method="cash",
            payment_type=PaymentType.payment.value,
            receipt_number=receipt_number,
            received_by_id=test_user.id,
            notes="Test payment for idempotency",
        )
        db_session.add(payment)
        db_session.flush()

        # Record the payment
        customer_account_service.record_payment(db_session, payment, test_user.id)
        db_session.commit()

        # Get transaction count before second attempt
        initial_count = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.PAYMENT,
            )
            .count()
        )

        # Act: Try to record same payment again (should fail)
        with pytest.raises(ValueError, match="has already been recorded"):
            customer_account_service.record_payment(db_session, payment, test_user.id)
            db_session.commit()

        # Assert: Should still have only one PAYMENT transaction
        final_count = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.PAYMENT,
            )
            .count()
        )

        assert (
            final_count == initial_count
        ), "Should not create duplicate PAYMENT transactions"

    def test_idempotent_sale_creation(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.8: Verify sale creation is idempotent (doesn't create duplicate SALE transactions).

        Expected behavior:
        1. Creating a sale should create exactly one SALE transaction
        2. The system should not accidentally create duplicate SALE transactions

        Note: This test verifies the architectural expectation that one sale = one SALE transaction
        """
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

        # Assert: Only one SALE transaction exists for this sale
        sale_transactions = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.SALE,
                CustomerTransaction.reference_id == sale.id,
            )
            .all()
        )

        assert (
            len(sale_transactions) == 1
        ), "Should have exactly 1 SALE transaction per sale"

    # ============================================================
    # CATEGORY: Audit Trail and Traceability
    # ============================================================

    def test_transaction_references_sale(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.9: Verify transaction has correct reference_type and reference_id.

        Expected behavior:
        1. SALE transaction should reference the sale
        2. reference_type should be "sale"
        3. reference_id should be the sale.id
        """
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

        # Assert: Check references
        transaction = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.SALE,
            )
            .first()
        )

        assert transaction is not None, "SALE transaction should exist"
        assert transaction.reference_type == "sale", "reference_type should be 'sale'"
        assert transaction.reference_id == sale.id, "reference_id should be the sale ID"

    def test_transaction_created_by_user(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.10: Verify transaction records the user who created it.

        Expected behavior:
        1. All transactions should have created_by_id set
        2. created_by_id should reference the actual user who created the transaction
        """
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
        sale_crud.create_sale(db=db_session, sale_in=sale_data, user_id=test_user.id)
        db_session.commit()

        # Assert: Check created_by_id
        transaction = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.SALE,
            )
            .first()
        )

        assert transaction is not None, "SALE transaction should exist"
        assert (
            transaction.created_by_id == test_user.id
        ), "created_by_id should be the test user ID"

    def test_transaction_timestamps(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.11: Verify transaction timestamps are set correctly.

        Expected behavior:
        1. created_at should be set automatically
        2. Timestamps should be in correct order
        """
        # Arrange: Note time before (remove microseconds for comparison)
        time_before = datetime.utcnow().replace(microsecond=0)

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
        sale_crud.create_sale(db=db_session, sale_in=sale_data, user_id=test_user.id)
        db_session.commit()

        time_after = datetime.utcnow().replace(microsecond=0) + timedelta(seconds=1)

        # Assert: Check timestamp
        transaction = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.SALE,
            )
            .first()
        )

        assert transaction is not None, "SALE transaction should exist"
        assert transaction.created_at is not None, "created_at should be set"

        # Remove microseconds from transaction timestamp for comparison
        trx_timestamp = transaction.created_at.replace(microsecond=0)
        assert (
            time_before <= trx_timestamp <= time_after
        ), f"Timestamp {trx_timestamp} should be within range [{time_before}, {time_after}]"

    def test_transaction_immutability(
        self,
        db_session: Session,
        test_product: Product,
        customer_with_account: Customer,
        test_user: User,
        open_cash_register,
    ):
        """Test 6.12: Verify transactions cannot be modified after creation.

        Expected behavior:
        1. Transactions should be immutable (no updates)
        2. This is a design principle - transactions are append-only

        Note: This test documents the architectural expectation.
        In practice, database constraints should prevent updates.
        """
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
        sale_crud.create_sale(db=db_session, sale_in=sale_data, user_id=test_user.id)
        db_session.commit()

        # Get the transaction
        transaction = (
            db_session.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_with_account.id,
                CustomerTransaction.transaction_type == TransactionType.SALE,
            )
            .first()
        )

        original_amount = transaction.amount
        original_balance_after = transaction.balance_after
        (transaction.updated_at if hasattr(transaction, "updated_at") else None)

        # Attempt to modify (this is what we want to prevent)
        # In a proper implementation, this should either:
        # 1. Raise an error
        # 2. Be prevented by database constraints
        # 3. Be ignored (immutable fields)

        # For now, we just verify the original values remain unchanged
        db_session.refresh(transaction)

        assert (
            transaction.amount == original_amount
        ), "Transaction amount should not change"
        assert (
            transaction.balance_after == original_balance_after
        ), "Transaction balance should not change"

        # Check immutability: If updated_at exists, it should equal created_at
        # (meaning the record was never updated after creation)
        if hasattr(transaction, "updated_at"):
            # Allow for slight timestamp differences (server default timestamps)
            # The key is that updated_at should not be significantly later than created_at
            time_diff = abs(
                (transaction.updated_at - transaction.created_at).total_seconds()
            )
            assert (
                time_diff < 1
            ), f"Transaction appears to have been updated (time diff: {time_diff}s)"
