"""Service layer for customer account management."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_account import (
    CustomerAccount,
    CustomerTransaction,
    TransactionType,
)
from app.models.payment import Payment
from app.models.sale import Sale
from app.schemas.customer_account import (
    AccountsReceivableAging,
    AccountStatement,
    CustomerAccountCreate,
    CustomerAccountResponse,
    CustomerTransactionResponse,
)
from app.utils.timezone import get_utc_now

logger = logging.getLogger(__name__)


class CustomerAccountService:
    """Service for managing customer accounts and transactions."""

    def create_account(
        self, db: Session, account_data: CustomerAccountCreate, created_by_id: int
    ) -> CustomerAccountResponse:
        """Create a new customer account.

        Args:
            db: Database session
            account_data: Account creation data
            created_by_id: ID of user creating the account

        Returns:
            Created account details

        Raises:
            ValueError: If account already exists for customer
        """
        # Check if account already exists
        existing = (
            db.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == account_data.customer_id)
            .first()
        )

        if existing:
            raise ValueError(
                f"Account already exists for customer {account_data.customer_id}"
            )

        # Create account
        account = CustomerAccount(
            customer_id=account_data.customer_id,
            credit_limit=account_data.credit_limit,
            account_balance=account_data.initial_balance or Decimal("0.00"),
            is_active=account_data.is_active,
            notes=account_data.notes,
            created_by_id=created_by_id,
        )

        db.add(account)
        db.flush()

        # Create initial balance transaction if needed
        if account_data.initial_balance and account_data.initial_balance != 0:
            transaction = CustomerTransaction(
                customer_id=account_data.customer_id,
                account_id=account.id,
                transaction_type=TransactionType.OPENING_BALANCE,
                amount=abs(account_data.initial_balance),
                balance_before=Decimal("0.00"),
                balance_after=account_data.initial_balance,
                description="Opening balance",
                transaction_date=get_utc_now(),
                created_by_id=created_by_id,
            )
            db.add(transaction)

            account.last_transaction_date = transaction.transaction_date
            account.transaction_count = 1

        db.commit()
        db.refresh(account)

        logger.info(f"Created account for customer {account.customer_id}")
        return self._format_account_response(db, account)

    def get_account(
        self, db: Session, customer_id: int
    ) -> Optional[CustomerAccountResponse]:
        """Get customer account details.

        Args:
            db: Database session
            customer_id: Customer ID

        Returns:
            Account details if found
        """
        account = (
            db.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == customer_id)
            .first()
        )

        if not account:
            return None

        return self._format_account_response(db, account)

    def get_or_create_account(
        self, db: Session, customer_id: int, created_by_id: int
    ) -> CustomerAccount:
        """Get existing account or create new one.

        Args:
            db: Database session
            customer_id: Customer ID
            created_by_id: User ID for creation

        Returns:
            Customer account instance
        """
        account = (
            db.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == customer_id)
            .first()
        )

        if not account:
            logger.info(f"Creating new account for customer {customer_id}")
            account = CustomerAccount(
                customer_id=customer_id,
                created_by_id=created_by_id,
            )
            db.add(account)
            db.flush()

        return account

    def get_balance_summary(self, db: Session, customer_id: int) -> dict:
        """Get balance summary from CustomerAccount.

        This is the SINGLE SOURCE OF TRUTH for customer balance.
        All UI components should use this method instead of calculating
        balance from Sales - Payments.

        Args:
            db: Database session
            customer_id: Customer ID

        Returns:
            Dict with balance info:
            - current_balance: Decimal (positive=debt, negative=credit)
            - has_debt: bool
            - has_credit: bool
            - status: str ('debt', 'credit', 'clear')
            - formatted: str
        """
        account = (
            db.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == customer_id)
            .first()
        )

        if not account:
            # No account yet - balance is zero
            return {
                "current_balance": Decimal("0.00"),
                "has_debt": False,
                "has_credit": False,
                "status": "clear",
                "formatted": "$0.00",
            }

        balance = account.account_balance

        if balance > 0:
            status = "debt"
            formatted = f"Debe ${balance:,.2f}"
        elif balance < 0:
            status = "credit"
            formatted = f"Crédito ${abs(balance):,.2f}"
        else:
            status = "clear"
            formatted = "$0.00"

        return {
            "current_balance": balance,
            "has_debt": balance > 0,
            "has_credit": balance < 0,
            "status": status,
            "formatted": formatted,
        }

    def get_payment_transaction_balances(
        self, db: Session, payment_id: int
    ) -> tuple[Decimal, Decimal]:
        """Get balance_before and balance_after from the payment transaction.

        Args:
            db: Database session
            payment_id: Payment ID

        Returns:
            Tuple of (balance_before, balance_after)
        """
        transaction = (
            db.query(CustomerTransaction)
            .filter(
                CustomerTransaction.reference_type == "payment",
                CustomerTransaction.reference_id == payment_id,
            )
            .first()
        )

        if transaction:
            return transaction.balance_before, transaction.balance_after

        # Fallback: return current balance for both if transaction not found
        logger.warning(f"No transaction found for payment {payment_id}")
        return Decimal("0.00"), Decimal("0.00")

    def record_sale(
        self, db: Session, sale: Sale, created_by_id: int
    ) -> CustomerTransactionResponse:
        """Record a sale transaction.

        Args:
            db: Database session
            sale: Sale instance
            created_by_id: User creating the transaction

        Returns:
            Created transaction
        """
        if not sale.customer_id:
            raise ValueError("Cannot record sale transaction for walk-in customer")

        # Get or create account
        account = self.get_or_create_account(db, sale.customer_id, created_by_id)

        # Record the FULL sale amount as a debit to customer account
        # Payment will be recorded separately as a credit
        sale_amount = sale.total_amount

        # Create transaction
        balance_before = account.account_balance
        balance_after = balance_before + sale_amount

        transaction = CustomerTransaction(
            customer_id=sale.customer_id,
            account_id=account.id,
            transaction_type=TransactionType.SALE,
            amount=sale_amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="sale",
            reference_id=sale.id,
            description=f"Sale {sale.invoice_number}",
            transaction_date=sale.sale_date,
            created_by_id=created_by_id,
        )

        db.add(transaction)

        # Update account
        account.account_balance = balance_after
        account.total_sales += sale.total_amount
        account.last_transaction_date = transaction.transaction_date
        account.transaction_count += 1
        account.updated_by_id = created_by_id
        account.updated_at = func.now()

        # Update available credit (negative balance = credit available)
        account.available_credit = (
            abs(balance_after) if balance_after < 0 else Decimal("0.00")
        )

        db.flush()

        logger.info(
            f"Recorded sale transaction for customer {sale.customer_id}: "
            f"${sale_amount} sale recorded, new balance: ${balance_after}"
        )

        return self._format_transaction_response(db, transaction)

    def record_payment(
        self,
        db: Session,
        payment: Payment,
        created_by_id: int,
        apply_to_oldest: bool = True,
    ) -> CustomerTransactionResponse:
        """Record a payment transaction.

        Args:
            db: Database session
            payment: Payment instance
            created_by_id: User creating the transaction
            apply_to_oldest: Whether to apply to oldest debt first

        Returns:
            Created transaction

        Raises:
            ValueError: If payment has already been recorded
        """
        # Check if this payment has already been recorded
        from app.models.customer_account import CustomerTransaction, TransactionType

        existing_payment_transaction = (
            db.query(CustomerTransaction)
            .filter(
                CustomerTransaction.reference_type == "payment",
                CustomerTransaction.reference_id == payment.id,
            )
            .first()
        )

        if existing_payment_transaction:
            raise ValueError(
                f"Payment {payment.id} (receipt {payment.receipt_number}) has already been recorded. "
                "Cannot record the same payment twice."
            )

        # Get or create account
        account = self.get_or_create_account(db, payment.customer_id, created_by_id)

        # Determine transaction type
        if payment.payment_type == "credit_application":
            transaction_type = TransactionType.CREDIT_APPLICATION
            description = f"Credit applied - {payment.receipt_number}"
        else:
            transaction_type = TransactionType.PAYMENT
            description = f"Payment received - {payment.receipt_number}"

        # Create transaction
        balance_before = account.account_balance

        # For credit applications, we're using existing credit (making balance less negative/more positive)
        # For regular payments, we're reducing debt (making balance more negative/less positive)
        if payment.payment_type == "credit_application":
            balance_after = (
                balance_before + payment.amount
            )  # Using credit increases balance
        else:
            balance_after = balance_before - payment.amount  # Payments reduce debt

        transaction = CustomerTransaction(
            customer_id=payment.customer_id,
            account_id=account.id,
            transaction_type=transaction_type,
            amount=payment.amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="payment",
            reference_id=payment.id,
            description=description,
            notes=payment.notes,
            transaction_date=payment.created_at,
            created_by_id=created_by_id,
        )

        db.add(transaction)

        # Update account
        account.account_balance = balance_after
        account.total_payments += payment.amount
        account.last_transaction_date = transaction.transaction_date
        account.last_payment_date = transaction.transaction_date
        account.transaction_count += 1
        account.updated_by_id = created_by_id
        account.updated_at = func.now()

        # Update available credit if payment creates credit balance
        if balance_after < 0:
            account.available_credit = abs(balance_after)
        else:
            account.available_credit = Decimal("0.00")

        db.flush()

        logger.info(
            f"Recorded payment transaction for customer {payment.customer_id}: "
            f"${payment.amount} paid, new balance: ${balance_after}"
        )

        return self._format_transaction_response(db, transaction)

    def record_void_sale(
        self, db: Session, sale, voided_by_id: int
    ) -> CustomerTransactionResponse:
        """Record a VOID_SALE transaction to reverse customer account balance.

        Args:
            db: Database session
            sale: The sale being voided
            voided_by_id: ID of user voiding the sale

        Returns:
            Transaction response

        Raises:
            ValueError: If void has already been recorded
        """
        # Check if this sale has already been voided
        existing_void = (
            db.query(CustomerTransaction)
            .filter(
                CustomerTransaction.reference_type == "sale",
                CustomerTransaction.reference_id == sale.id,
                CustomerTransaction.transaction_type == TransactionType.VOID_SALE,
            )
            .first()
        )

        if existing_void:
            raise ValueError(
                f"Sale {sale.invoice_number} void has already been recorded. "
                "Cannot void the same sale twice."
            )

        # Get account (SQLAlchemy model, not response)
        account = (
            db.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == sale.customer_id)
            .first()
        )

        if not account:
            raise ValueError(
                f"Customer account not found for customer_id {sale.customer_id}"
            )

        # Create VOID_SALE transaction to reverse the debt
        balance_before = account.account_balance
        balance_after = balance_before - sale.total_amount  # Void reduces debt

        transaction = CustomerTransaction(
            customer_id=sale.customer_id,
            account_id=account.id,
            transaction_type=TransactionType.VOID_SALE,
            amount=sale.total_amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="sale",
            reference_id=sale.id,
            description=f"Sale {sale.invoice_number} voided",
            notes=sale.void_reason,
            created_by_id=voided_by_id,
        )

        db.add(transaction)

        # Update account
        account.account_balance = balance_after
        account.transaction_count += 1
        account.updated_at = func.now()

        # Update available credit if void creates credit balance
        if balance_after < 0:
            account.available_credit = abs(balance_after)
        else:
            account.available_credit = Decimal("0.00")

        db.flush()

        logger.info(
            f"Recorded void sale transaction for customer {sale.customer_id}: "
            f"Sale {sale.invoice_number} voided, ${sale.total_amount} reversed, "
            f"new balance: ${balance_after}"
        )

        return self._format_transaction_response(db, transaction)

    def apply_credit(
        self,
        db: Session,
        customer_id: int,
        amount: Decimal,
        sale_id: int,
        created_by_id: int,
        notes: Optional[str] = None,
    ) -> tuple[CustomerTransactionResponse, Decimal]:
        """Record credit usage for a sale (informational transaction).

        This function records that customer credit was used to pay for a sale.
        It does NOT modify the account balance because the credit is automatically
        consumed when the SALE transaction is recorded (balance goes up by sale amount,
        consuming any negative balance/credit the customer had).

        This transaction is for TRACEABILITY only - to show in the customer's
        transaction history that their credit was used for this specific sale.

        Args:
            db: Database session
            customer_id: Customer ID
            amount: Amount of credit used
            sale_id: Sale where credit was applied
            created_by_id: User recording the credit usage
            notes: Optional notes

        Returns:
            Tuple of (transaction, actual_amount_applied)

        Raises:
            ValueError: If credit was already recorded for this sale
        """
        account = self.get_or_create_account(db, customer_id, created_by_id)

        # Check if account is blocked
        if account.is_blocked:
            raise ValueError(f"Account is blocked: {account.block_reason}")

        # Get the sale
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            raise ValueError(f"Sale {sale_id} not found")

        from app.models.customer_account import CustomerTransaction, TransactionType

        # Check if credit was already applied to this sale
        credit_application_exists = (
            db.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_id,
                CustomerTransaction.reference_type == "sale",
                CustomerTransaction.reference_id == sale_id,
                CustomerTransaction.transaction_type
                == TransactionType.CREDIT_APPLICATION,
            )
            .first()
        )

        if credit_application_exists:
            raise ValueError(
                f"Sale {sale_id} already has a CREDIT_APPLICATION transaction. "
                "Cannot record credit usage twice for the same sale."
            )

        # Create INFORMATIONAL transaction (balance does NOT change)
        # The credit was already consumed when the SALE was recorded
        balance_before = account.account_balance
        balance_after = balance_before  # NO CHANGE - this is informational only

        transaction = CustomerTransaction(
            customer_id=customer_id,
            account_id=account.id,
            transaction_type=TransactionType.CREDIT_APPLICATION,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,  # Same as before - no balance change
            reference_type="sale",
            reference_id=sale_id,
            description=f"Credit used for sale {sale.invoice_number}",
            notes=notes,
            transaction_date=get_utc_now(),
            created_by_id=created_by_id,
        )

        db.add(transaction)

        # Update account metadata (but NOT the balance)
        account.last_transaction_date = transaction.transaction_date
        account.transaction_count += 1
        account.updated_by_id = created_by_id
        account.updated_at = func.now()

        db.flush()

        logger.info(
            f"Recorded credit usage: ${amount} for sale {sale_id}, "
            f"customer {customer_id} (informational - balance unchanged)"
        )

        return self._format_transaction_response(db, transaction), amount

    def record_transaction(
        self,
        db: Session,
        customer_id: int,
        transaction_type: TransactionType,
        amount: Decimal,
        reference_id: Optional[int],
        description: str,
        created_by_id: int,
        notes: Optional[str] = None,
    ) -> CustomerTransactionResponse:
        """Record a generic transaction.

        Args:
            db: Database session
            customer_id: Customer ID
            transaction_type: Type of transaction
            amount: Transaction amount (positive for debit, negative for credit)
            reference_id: Optional reference ID
            description: Transaction description
            created_by_id: User creating transaction
            notes: Optional notes

        Returns:
            Created transaction
        """
        # Get or create account
        account = self.get_or_create_account(db, customer_id, created_by_id)

        # Create transaction
        balance_before = account.account_balance
        balance_after = balance_before + amount

        transaction = CustomerTransaction(
            customer_id=customer_id,
            account_id=account.id,
            transaction_type=transaction_type,
            amount=abs(amount),  # Store absolute value
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type="deposit",
            reference_id=reference_id,
            description=description,
            notes=notes,
            transaction_date=get_utc_now(),
            created_by_id=created_by_id,
        )

        db.add(transaction)

        # Update account
        account.account_balance = balance_after
        account.last_transaction_date = transaction.transaction_date
        account.transaction_count += 1
        account.updated_by_id = created_by_id
        account.updated_at = func.now()

        # Update available credit if balance is negative
        if balance_after < 0:
            account.available_credit = abs(balance_after)
        else:
            account.available_credit = Decimal("0.00")

        db.flush()

        logger.info(
            f"Recorded {transaction_type} transaction for customer {customer_id}: "
            f"${amount}, new balance: ${balance_after}"
        )

        return self._format_transaction_response(db, transaction)

    def check_credit_availability(
        self, db: Session, customer_id: int
    ) -> tuple[bool, Decimal, str]:
        """Check if customer has credit available.

        Args:
            db: Database session
            customer_id: Customer ID

        Returns:
            Tuple of (has_credit, amount_available, message)
        """
        account = (
            db.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == customer_id)
            .first()
        )

        if not account:
            return False, Decimal("0.00"), "No account found"

        if not account.is_active:
            return False, Decimal("0.00"), "Account is inactive"

        if account.is_blocked:
            return False, Decimal("0.00"), f"Account blocked: {account.block_reason}"

        if account.account_balance >= 0:
            return False, Decimal("0.00"), "No credit balance available"

        available = abs(account.account_balance)
        return True, available, f"${available} credit available"

    def get_statement(
        self,
        db: Session,
        customer_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AccountStatement:
        """Generate account statement for customer.

        Args:
            db: Database session
            customer_id: Customer ID
            start_date: Period start (default: 30 days ago)
            end_date: Period end (default: today)

        Returns:
            Account statement
        """
        # Default date range
        if not end_date:
            end_date = get_utc_now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get customer and account
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        account = self.get_or_create_account(db, customer_id, 1)  # System user

        # Get opening balance
        opening_balance_query = (
            db.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_id,
                CustomerTransaction.transaction_date < start_date,
            )
            .order_by(CustomerTransaction.transaction_date.desc())
            .first()
        )

        opening_balance = (
            opening_balance_query.balance_after
            if opening_balance_query
            else Decimal("0.00")
        )

        # Get transactions in period
        transactions = (
            db.query(CustomerTransaction)
            .filter(
                CustomerTransaction.customer_id == customer_id,
                CustomerTransaction.transaction_date >= start_date,
                CustomerTransaction.transaction_date <= end_date,
            )
            .order_by(CustomerTransaction.transaction_date)
            .all()
        )

        # Calculate totals
        total_debits = sum(t.amount for t in transactions if t.is_debit)
        total_credits = sum(t.amount for t in transactions if t.is_credit)

        # Format transactions
        transaction_list = [
            self._format_transaction_response(db, t) for t in transactions
        ]

        return AccountStatement(
            customer_id=customer_id,
            customer_name=customer.name,
            statement_date=get_utc_now(),
            period_start=start_date,
            period_end=end_date,
            opening_balance=opening_balance,
            closing_balance=account.account_balance,
            total_debits=total_debits,
            total_credits=total_credits,
            transaction_count=len(transactions),
            transactions=transaction_list,
            current_balance=account.account_balance,
            credit_limit=account.credit_limit,
            available_credit=account.total_available_credit,
        )

    def get_aging_report(
        self, db: Session, customer_id: Optional[int] = None
    ) -> list[AccountsReceivableAging]:
        """Generate accounts receivable aging report.

        Args:
            db: Database session
            customer_id: Optional specific customer

        Returns:
            List of aging entries
        """
        # This would need to be implemented based on unpaid sales
        # For now, returning empty list
        return []

    def _format_account_response(
        self, db: Session, account: CustomerAccount
    ) -> CustomerAccountResponse:
        """Format account response with computed fields."""
        customer = account.customer

        return CustomerAccountResponse(
            id=account.id,
            customer_id=account.customer_id,
            customer_name=customer.name,
            credit_limit=account.credit_limit,
            is_active=account.is_active,
            notes=account.notes,
            account_balance=account.account_balance,
            available_credit=account.available_credit,
            total_sales=account.total_sales,
            total_payments=account.total_payments,
            last_transaction_date=account.last_transaction_date,
            last_payment_date=account.last_payment_date,
            transaction_count=account.transaction_count,
            is_blocked=account.is_blocked,
            blocked_until=account.blocked_until,
            block_reason=account.block_reason,
            created_at=account.created_at,
            updated_at=account.updated_at,
            has_debt=account.has_debt,
            has_credit=account.has_credit,
            is_settled=account.is_settled,
            total_available_credit=account.total_available_credit,
            remaining_credit_limit=account.remaining_credit_limit,
        )

    def _format_transaction_response(
        self, db: Session, transaction: CustomerTransaction
    ) -> CustomerTransactionResponse:
        """Format transaction response."""
        created_by = transaction.created_by

        return CustomerTransactionResponse(
            id=transaction.id,
            customer_id=transaction.customer_id,
            account_id=transaction.account_id,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            balance_before=transaction.balance_before,
            balance_after=transaction.balance_after,
            reference_type=transaction.reference_type,
            reference_id=transaction.reference_id,
            description=transaction.description,
            notes=transaction.notes,
            transaction_date=transaction.transaction_date,
            created_at=transaction.created_at,
            created_by_id=transaction.created_by_id,
            created_by_name=created_by.full_name,
            is_debit=transaction.is_debit,
            is_credit=transaction.is_credit,
            impact_amount=transaction.impact_amount,
        )


# Create singleton instance
customer_account_service = CustomerAccountService()
