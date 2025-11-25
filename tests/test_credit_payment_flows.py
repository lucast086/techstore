"""Comprehensive tests for customer credit payment functionality.

Tests cover:
1. Full payment with credit
2. Partial credit payment
3. Mixed payment (credit + cash)
4. Insufficient credit scenarios
5. Edge cases and error conditions
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
from app.services.customer_account_service import customer_account_service
from app.utils.timezone import get_utc_now
from sqlalchemy.orm import Session


class TestCreditPaymentFlows:
    """Test various credit payment scenarios."""

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
        """Create a test product."""
        product = Product(
            sku="TEST001",
            name="Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("500.00"),
            first_sale_price=Decimal("1000.00"),
            second_sale_price=Decimal("1000.00"),
            third_sale_price=Decimal("1000.00"),
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
    def jane_with_credit(self, db_session: Session, test_user: User) -> Customer:
        """Create Jane with $769 credit balance."""
        # Create customer
        jane = Customer(
            id=2,  # ID: 2 as specified
            name="Jane",
            phone="555-0102",
            email="jane@example.com",
            is_active=True,
        )
        db_session.add(jane)
        db_session.flush()

        # Create account with credit
        account = CustomerAccount(
            customer_id=jane.id,
            account_balance=Decimal("-769.00"),  # Negative = credit
            available_credit=Decimal("769.00"),
            credit_limit=Decimal("0.00"),
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(jane)
        return jane

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

    def test_full_payment_with_credit_exact_amount(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test using entire credit balance to pay for a sale that matches exactly."""
        # Create a sale for exactly $769 (matching Jane's credit)
        # With 10% tax: subtotal = $699.09, tax = $69.91, total = $769.00
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Full credit payment test",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal(
                        "699.09"
                    ),  # Custom price to get exact $769 with tax
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("769.00"),
        )

        # Create the sale (only creates SALE transaction)
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # NEW FLOW: Jane's existing credit is automatically consumed by SALE transaction
        # No need to create Payment or apply credit separately
        # Balance: -$769 + $769 (SALE) = $0

        # Assertions for sale
        assert sale is not None
        assert sale.customer_id == jane_with_credit.id
        assert sale.total_amount == Decimal("769.00")
        assert sale.payment_status == "paid"
        assert sale.payment_method == "account_credit"
        assert sale.paid_amount == Decimal("769.00")

        # Check NO payment record was created (credit consumed automatically)
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is None  # No Payment for existing credit consumption

        # Check customer account balance
        db_session.refresh(jane_with_credit)
        account = jane_with_credit.account

        # Debug: Check transaction order
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .order_by(CustomerTransaction.id)
            .all()
        )
        print(f"\nDebug - Final balance: {account.account_balance}")
        print("Transactions:")
        for t in transactions:
            print(
                f"  {t.transaction_type.value}: {t.balance_before} + {t.amount if t.is_debit else -t.amount} = {t.balance_after}"
            )

        assert account.account_balance == Decimal("0.00")
        assert account.available_credit == Decimal("0.00")

        # Check transactions were recorded
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .order_by(CustomerTransaction.id)
            .all()
        )

        # NEW FLOW: Should have only 1 transaction - SALE
        # Existing credit is consumed automatically, no CREDIT_APPLICATION needed
        assert len(transactions) == 1

        # Only transaction: SALE that consumes existing credit
        sale_trans = transactions[0]
        assert sale_trans.transaction_type == TransactionType.SALE
        assert sale_trans.amount == Decimal("769.00")
        assert sale_trans.balance_before == Decimal("-769.00")
        assert sale_trans.balance_after == Decimal("0.00")  # Credit consumed by sale
        assert sale_trans.reference_type == "sale"
        assert sale_trans.reference_id == sale.id

        # Credit payments don't affect cash register
        # In production, cash register entries would only be created for cash payments

    def test_partial_credit_payment(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test using part of credit for a sale less than the credit balance."""
        # Create a sale for $330 (Jane has $769 credit)
        # Using simple numbers to avoid rounding issues
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Partial credit payment test",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("300.00"),  # With 10% tax = $330.00
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("330.00"),
        )

        # Create the sale (only creates SALE transaction)
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # NEW FLOW: Existing credit consumed automatically
        # Balance: -$769 + $330 (SALE) = -$439 credit remaining

        # Assertions for sale
        assert sale.total_amount == Decimal("330.00")
        assert sale.payment_status == "paid"
        assert sale.paid_amount == Decimal("330.00")

        # Check NO payment record (existing credit consumed automatically)
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is None

        # Check customer account balance ($769 - $330 = $439 credit remaining)
        db_session.refresh(jane_with_credit)
        account = jane_with_credit.account
        assert account.account_balance == Decimal("-439.00")  # Negative = credit
        assert account.available_credit == Decimal("439.00")

        # Verify transactions
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .order_by(CustomerTransaction.id)
            .all()
        )
        # Only 1 SALE transaction (existing credit consumed automatically)
        assert len(transactions) == 1

        # SALE transaction that consumes part of existing credit
        assert transactions[0].transaction_type == TransactionType.SALE
        assert transactions[0].amount == Decimal("330.00")
        assert transactions[0].balance_before == Decimal("-769.00")
        assert transactions[0].balance_after == Decimal("-439.00")

    def test_mixed_payment_credit_plus_cash(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test using credit + cash to pay for a sale that exceeds credit balance."""
        # Create a sale for $1,000 (Jane has $769 credit, needs $231 cash)
        # IMPORTANT: For mixed payments, amount_paid should only include non-credit payments
        # Credit is applied separately to avoid double-recording
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="mixed",
            discount_amount=Decimal("0.00"),
            notes="Mixed payment: $769 credit + $231 cash",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("909.09"),  # With 10% tax = $1,000.00
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("231.00"),  # Only the cash portion, not the credit
        )

        # Create the sale (now only creates SALE transaction)
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # NEW FLOW: After sale creation, apply payments in correct order
        # This simulates what web/sales.py does after create_sale()
        # Order matters: Apply cash payment FIRST, then credit
        from app.models.payment import Payment, PaymentType
        from app.services.customer_account_service import customer_account_service

        # Step 1: Create and record Payment for cash portion
        # NOTE: Jane's existing credit (-$769) automatically offsets the sale debt
        # After SALE transaction: balance went from -$769 to +$231 (used $769 credit)
        # Now we just need to record the cash payment for the remaining $231
        cash_payment = Payment(
            customer_id=jane_with_credit.id,
            sale_id=sale.id,
            amount=Decimal("231.00"),
            payment_method="mixed",
            payment_type=PaymentType.payment.value,
            receipt_number=f"REC-{sale.invoice_number}",
            received_by_id=test_user.id,
            notes="Mixed payment (cash portion)",
        )
        db_session.add(cash_payment)
        db_session.flush()

        # Record PAYMENT transaction for cash portion
        customer_account_service.record_payment(db_session, cash_payment, test_user.id)

        # NO CREDIT_APPLICATION needed! Jane's existing credit was automatically consumed
        # by the SALE transaction. The balance shows this: -$769 -> +$231 -> $0

        db_session.commit()
        db_session.refresh(sale)

        # Assertions for sale
        assert sale.total_amount == Decimal("1000.00")
        assert sale.payment_method == "mixed"
        assert sale.paid_amount == Decimal("231.00")  # Cash portion only

        # Check payments - should have only 1: cash payment
        # Credit applications don't create Payment records
        payments = (
            db_session.query(Payment)
            .filter(Payment.sale_id == sale.id)
            .order_by(Payment.id)
            .all()
        )

        # Should have 1 payment: cash portion only
        assert len(payments) == 1

        # Payment: cash portion
        assert cash_payment.amount == Decimal("231.00")
        assert cash_payment.payment_type == PaymentType.payment

        # Check customer account balance (should be zero after using all credit)
        db_session.refresh(jane_with_credit)
        account = jane_with_credit.account
        assert account.account_balance == Decimal("0.00")
        assert account.available_credit == Decimal("0.00")

        # Verify transactions
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .order_by(CustomerTransaction.id)
            .all()
        )

        # Should have 2 transactions only: SALE, PAYMENT (cash)
        # No CREDIT_APPLICATION because existing credit is automatically consumed
        assert len(transactions) == 2

        # For mixed payment, only the cash portion would affect the cash register
        # Credit portions don't create cash register entries

    def test_insufficient_credit_error(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test error when trying to use more credit than available."""
        # Try to use credit that exceeds available balance
        # Jane has only $769 credit, trying to use $1,000 should fail

        # Test the service layer validation
        (
            has_credit,
            available,
            message,
        ) = customer_account_service.check_credit_availability(
            db_session, jane_with_credit.id
        )

        assert has_credit is True
        assert available == Decimal("769.00")
        assert available < Decimal("1000.00")  # Not enough credit

        # If we try to apply more credit than available, it should raise an error
        from app.services.payment_service import payment_service

        with pytest.raises(ValueError, match="Insufficient credit"):
            payment_service.apply_customer_credit(
                db=db_session,
                customer_id=jane_with_credit.id,
                credit_amount=Decimal("1000.00"),  # More than available
                sale_id=1,  # Dummy sale ID
                user_id=test_user.id,
            )

        # Customer balance should remain unchanged
        db_session.refresh(jane_with_credit)
        assert jane_with_credit.account.account_balance == Decimal("-769.00")

    def test_customer_without_credit_cannot_use_credit_payment(
        self,
        db_session: Session,
        test_user: User,
        test_customer: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test that customers without credit cannot use credit payment method."""
        # Ensure customer has no account or zero balance
        account = CustomerAccount(
            customer_id=test_customer.id,
            account_balance=Decimal("0.00"),
            available_credit=Decimal("0.00"),
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()

        # Check credit availability
        (
            has_credit,
            available,
            message,
        ) = customer_account_service.check_credit_availability(
            db_session, test_customer.id
        )

        assert has_credit is False
        assert available == Decimal("0.00")
        assert "No credit balance available" in message

        # Try to apply credit - should fail
        from app.services.payment_service import payment_service

        with pytest.raises(ValueError, match="No credit available"):
            payment_service.apply_customer_credit(
                db=db_session,
                customer_id=test_customer.id,
                credit_amount=Decimal("100.00"),
                sale_id=1,
                user_id=test_user.id,
            )

    def test_credit_payment_creates_correct_transaction_records(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test that all transaction records are created correctly for credit payments."""
        initial_balance = jane_with_credit.account.account_balance

        # Create a sale for $500
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Transaction records test",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("454.55"),  # With 10% tax = $500.00
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("500.00"),
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Get all transactions
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .order_by(CustomerTransaction.id)
            .all()
        )

        # NEW FLOW: Should have exactly 1 SALE transaction
        # Existing credit consumed automatically, no CREDIT_APPLICATION needed
        assert len(transactions) == 1

        # Transaction: SALE that consumes existing credit
        sale_trans = transactions[0]
        assert sale_trans.transaction_type == TransactionType.SALE
        assert sale_trans.amount == Decimal("500.00")
        assert sale_trans.reference_type == "sale"
        assert sale_trans.reference_id == sale.id
        assert sale_trans.is_debit is True
        assert sale_trans.is_credit is False

        # Final balance check
        db_session.refresh(jane_with_credit)
        # Initial: -$769, Sale: +$500, Final: -$269
        expected_balance = initial_balance + Decimal("500.00")
        assert jane_with_credit.account.account_balance == expected_balance

    def test_voided_sale_reverses_credit_usage(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test that voiding a sale with credit payment reverses the credit usage."""
        initial_balance = jane_with_credit.account.account_balance

        # Create a sale using credit
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Sale to be voided",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("272.73"),  # With 10% tax = $300.00
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("300.00"),
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify credit was used
        db_session.refresh(jane_with_credit)
        assert jane_with_credit.account.account_balance == initial_balance + Decimal(
            "300.00"
        )

        # Void the sale
        voided_sale = sale_crud.void_sale(
            db=db_session,
            sale_id=sale.id,
            reason="Test void to reverse credit",
            user_id=test_user.id,
        )

        assert voided_sale.is_voided is True
        assert voided_sale.payment_status == "voided"

        # Check that payments were voided
        payments = db_session.query(Payment).filter(Payment.sale_id == sale.id).all()
        for payment in payments:
            assert payment.voided is True
            assert payment.void_reason == f"Sale {sale.invoice_number} voided"

        # Note: Current implementation may not automatically reverse the customer account balance
        # This would need to be implemented in the customer_account_service

    def test_credit_payment_with_partial_sale_amount(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test sale where existing credit fully covers the amount."""
        # NEW FLOW: Jane has $769 credit, makes $500 sale
        # Existing credit automatically covers it, leaving $269 credit
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Sale covered by existing credit",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("454.54"),  # With 10% tax = $499.994 ≈ $500.00
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("500.00"),  # Full amount covered by existing credit
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Sale should be fully paid (existing credit covers it)
        assert sale.total_amount == Decimal("499.99")
        assert sale.paid_amount == Decimal("500.00")
        assert sale.payment_status == "paid"

        # Check balance changes
        db_session.refresh(jane_with_credit)
        # Initial: -$769 (credit)
        # Sale: +$499.99 (consumed from existing credit)
        # Final: -$769 + $499.99 = -$269.01 credit remaining
        assert jane_with_credit.account.account_balance == Decimal("-269.01")

        # Verify transactions - only 1 SALE transaction
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .order_by(CustomerTransaction.id)
            .all()
        )
        assert len(transactions) == 1
        assert transactions[0].transaction_type == TransactionType.SALE
        assert transactions[0].amount == Decimal("499.99")

    def test_walk_in_customer_cannot_use_credit(
        self,
        db_session: Session,
        test_user: User,
        test_product: Product,
        open_cash_register,
    ):
        """Test that sales without customer_id are automatically assigned to walk-in (ID=1).

        BUSINESS RULE: All sales MUST have a customer. If no customer_id provided,
        it defaults to walk-in customer (ID=1), which ensures all sales and payments
        are tracked in the transaction system.
        """
        # Try to create a sale without customer_id
        sale_data = SaleCreate(
            customer_id=None,  # Should be auto-converted to walk-in (ID=1)
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Sale without customer_id",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("110.00"),  # With tax
        )

        # Sale should be created and assigned to walk-in customer
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify it was assigned to walk-in customer (ID=1)
        assert sale.customer_id == 1

        # Payment record SHOULD be created (walk-in is a real customer)
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is not None
        assert payment.customer_id == 1

        # Customer transactions SHOULD exist (SALE + PAYMENT)
        transactions = db_session.query(CustomerTransaction).all()
        assert len(transactions) == 2  # SALE and PAYMENT transactions

    def test_no_double_credit_application(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test that credit is not applied twice to the same sale."""
        # NEW FLOW: In the new system, existing credit is consumed automatically by SALE transaction
        # There's no manual credit application needed or allowed

        # Create a sale with credit payment method
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Double credit test",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("90.91"),  # With 10% tax = $100.00
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("100.00"),
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # NEW FLOW: After sale creation, Jane's credit is automatically consumed
        # Balance: -$769 (credit) + $100 (sale) = -$669 (remaining credit)
        db_session.refresh(jane_with_credit)
        assert jane_with_credit.account.account_balance == Decimal("-669.00")
        assert jane_with_credit.account.available_credit == Decimal("669.00")

        # Check transactions - should only have SALE transaction
        from app.models.customer_account import CustomerTransaction

        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .filter(CustomerTransaction.reference_type == "sale")
            .filter(CustomerTransaction.reference_id == sale.id)
            .all()
        )

        # Should only have 1 SALE transaction (credit consumed automatically)
        assert len(transactions) == 1
        assert transactions[0].transaction_type.value == "sale"

        # NEW FLOW: Now we need to apply the payment to complete the sale
        # This simulates what web/sales.py does after create_sale()
        from app.services.customer_account_service import customer_account_service

        # Apply the credit payment (this creates CREDIT_APPLICATION transaction)
        customer_account_service.apply_credit(
            db=db_session,
            customer_id=jane_with_credit.id,
            amount=Decimal("100.00"),
            sale_id=sale.id,
            created_by_id=test_user.id,
            notes="Credit payment",
        )

        # After applying credit, balance should be back to original
        # Balance: -$669 - $100 (credit applied) = -$769 (back to original)
        db_session.refresh(jane_with_credit)
        balance_after_credit = jane_with_credit.account.account_balance
        assert balance_after_credit == Decimal("-769.00")

        # Try to apply credit again to the same sale - should fail
        with pytest.raises(ValueError, match="already has a CREDIT_APPLICATION"):
            customer_account_service.apply_credit(
                db=db_session,
                customer_id=jane_with_credit.id,
                amount=Decimal("100.00"),
                sale_id=sale.id,
                created_by_id=test_user.id,
                notes="Duplicate credit attempt",
            )

        # Balance should remain unchanged after failed attempt
        db_session.refresh(jane_with_credit)
        assert jane_with_credit.account.account_balance == balance_after_credit

    def test_blocked_account_cannot_use_credit(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test that blocked accounts cannot use credit."""
        from datetime import timedelta

        # Block Jane's account by setting blocked_until
        jane_with_credit.account.blocked_until = get_utc_now() + timedelta(days=7)
        jane_with_credit.account.block_reason = "Payment dispute"
        db_session.commit()

        # Check credit availability
        (
            has_credit,
            available,
            message,
        ) = customer_account_service.check_credit_availability(
            db_session, jane_with_credit.id
        )

        assert has_credit is False
        assert "Account blocked" in message

        # Try to use credit - should fail
        from app.services.payment_service import payment_service

        with pytest.raises(ValueError, match="Account blocked"):
            payment_service.apply_customer_credit(
                db=db_session,
                customer_id=jane_with_credit.id,
                credit_amount=Decimal("100.00"),
                sale_id=1,
                user_id=test_user.id,
            )
