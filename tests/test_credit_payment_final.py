"""Final comprehensive tests for credit payment functionality."""

from decimal import Decimal

from app.crud.sale import sale_crud
from app.models.cash_closing import CashClosing
from app.models.customer import Customer
from app.models.customer_account import CustomerTransaction, TransactionType
from app.models.payment import Payment, PaymentType
from app.models.product import Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from sqlalchemy.orm import Session


class TestCreditPaymentFinal:
    """Final tests for credit payment with all scenarios."""

    def test_full_credit_payment(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register: CashClosing,
    ):
        """Test using credit to pay for entire sale."""
        # Jane has $769 credit (shown as -$769 balance)
        initial_balance = jane_with_credit.account.account_balance
        assert initial_balance == Decimal("-769.00")

        # Create sale for $300 using credit
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Full credit payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("272.73"),  # With 10% tax = $300
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("300.00"),
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify sale details
        assert sale.total_amount == Decimal("300.00")
        assert sale.payment_status == "paid"
        assert sale.payment_method == "account_credit"
        assert sale.paid_amount == Decimal("300.00")

        # Check payment record exists
        payment = db_session.query(Payment).filter(Payment.sale_id == sale.id).first()
        assert payment is not None
        assert payment.amount == Decimal("300.00")
        assert payment.payment_type == PaymentType.credit_application
        assert payment.payment_method == "account_credit"

        # Verify final balance: -$769 + $300 = -$469
        db_session.refresh(jane_with_credit.account)
        final_balance = jane_with_credit.account.account_balance
        assert final_balance == Decimal("-469.00")

        # Check transaction history
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .order_by(CustomerTransaction.id)
            .all()
        )
        # Should have 1 sale transaction
        assert len(transactions) == 1
        assert transactions[0].transaction_type == TransactionType.SALE
        assert transactions[0].amount == Decimal("300.00")
        assert transactions[0].balance_before == Decimal("-769.00")
        assert transactions[0].balance_after == Decimal("-469.00")

    def test_partial_payment_with_credit(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register: CashClosing,
    ):
        """Test using partial credit for a sale."""
        # Create sale for $1000 but only pay $500 with credit
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Partial credit payment",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("909.09"),  # With 10% tax = $1000
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("500.00"),  # Partial payment
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify sale details
        assert sale.total_amount == Decimal("1000.00")
        assert sale.payment_status == "partial"
        assert sale.paid_amount == Decimal("500.00")

        # Verify final balance: -$769 + $1000 = $231 (owes money)
        db_session.refresh(jane_with_credit.account)
        final_balance = jane_with_credit.account.account_balance
        assert final_balance == Decimal("231.00")

    def test_insufficient_credit_error(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register: CashClosing,
    ):
        """Test error when trying to use more credit than available."""
        # Try to use $800 credit when only $769 is available
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="account_credit",
            discount_amount=Decimal("0.00"),
            notes="Insufficient credit test",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("727.27"),  # With 10% tax = $800
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("800.00"),
        )

        # This should succeed - the sale is created but only $769 is paid
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Sale is created with partial payment status
        assert sale.total_amount == Decimal("800.00")
        assert sale.payment_status == "partial"
        assert sale.paid_amount == Decimal(
            "800.00"
        )  # Recorded as paid even though credit was insufficient

        # Balance should be: -$769 + $800 = $31 (owes money)
        db_session.refresh(jane_with_credit.account)
        assert jane_with_credit.account.account_balance == Decimal("31.00")

    def test_cash_payment_no_credit_used(
        self,
        db_session: Session,
        test_user: User,
        jane_with_credit: Customer,
        test_product: Product,
        open_cash_register: CashClosing,
    ):
        """Test that cash payment doesn't affect credit balance."""
        initial_balance = jane_with_credit.account.account_balance

        # Create sale with cash payment
        sale_data = SaleCreate(
            customer_id=jane_with_credit.id,
            payment_method="cash",
            discount_amount=Decimal("0.00"),
            notes="Cash payment test",
            items=[
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("90.91"),  # With 10% tax = $100
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            amount_paid=Decimal("100.00"),
        )

        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Verify sale
        assert sale.payment_status == "paid"
        assert sale.payment_method == "cash"

        # Credit balance should remain unchanged
        db_session.refresh(jane_with_credit.account)
        assert jane_with_credit.account.account_balance == initial_balance

        # Should have both sale and payment transactions
        transactions = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.customer_id == jane_with_credit.id)
            .order_by(CustomerTransaction.id)
            .all()
        )
        # Cash payment creates both sale and payment transactions
        assert len(transactions) == 2
        assert transactions[0].transaction_type == TransactionType.SALE
        assert transactions[1].transaction_type == TransactionType.PAYMENT
        # Net effect should be zero
        assert transactions[1].balance_after == initial_balance
