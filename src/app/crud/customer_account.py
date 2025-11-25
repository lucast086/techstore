"""CRUD operations for customer accounts."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload

from app.models.customer_account import (
    CustomerAccount,
    CustomerTransaction,
    TransactionType,
)
from app.schemas.customer_account import CustomerAccountCreate

logger = logging.getLogger(__name__)


class CustomerAccountCRUD:
    """CRUD operations for customer accounts."""

    def get(self, db: Session, id: int) -> Optional[CustomerAccount]:
        """Get customer account by ID."""
        return (
            db.query(CustomerAccount)
            .options(joinedload(CustomerAccount.customer))
            .filter(CustomerAccount.id == id)
            .first()
        )

    def get_by_customer_id(
        self, db: Session, customer_id: int
    ) -> Optional[CustomerAccount]:
        """Get customer account by customer ID."""
        return (
            db.query(CustomerAccount)
            .options(joinedload(CustomerAccount.customer))
            .filter(CustomerAccount.customer_id == customer_id)
            .first()
        )

    def get_or_create(
        self, db: Session, customer_id: int, created_by_id: int
    ) -> CustomerAccount:
        """Get existing account or create new one."""
        account = self.get_by_customer_id(db, customer_id)

        if not account:
            logger.info(f"Creating new account for customer {customer_id}")
            account = CustomerAccount(
                customer_id=customer_id,
                credit_limit=Decimal("0.00"),
                account_balance=Decimal("0.00"),
                created_by_id=created_by_id,
            )
            db.add(account)
            db.flush()

        return account

    def create(
        self, db: Session, *, obj_in: CustomerAccountCreate, created_by_id: int
    ) -> CustomerAccount:
        """Create new customer account."""
        # Check if account already exists
        existing = self.get_by_customer_id(db, obj_in.customer_id)
        if existing:
            raise ValueError(
                f"Account already exists for customer {obj_in.customer_id}"
            )

        account = CustomerAccount(
            customer_id=obj_in.customer_id,
            credit_limit=obj_in.credit_limit,
            account_balance=obj_in.initial_balance or Decimal("0.00"),
            is_active=obj_in.is_active,
            notes=obj_in.notes,
            created_by_id=created_by_id,
        )

        db.add(account)
        db.flush()

        # Create initial balance transaction if needed
        if obj_in.initial_balance and obj_in.initial_balance != 0:
            transaction = CustomerTransaction(
                customer_id=obj_in.customer_id,
                account_id=account.id,
                transaction_type=TransactionType.OPENING_BALANCE,
                amount=abs(obj_in.initial_balance),
                balance_before=Decimal("0.00"),
                balance_after=obj_in.initial_balance,
                description="Opening balance",
                transaction_date=datetime.utcnow(),
                created_by_id=created_by_id,
            )
            db.add(transaction)

            account.last_transaction_date = transaction.transaction_date
            account.transaction_count = 1

        db.commit()
        db.refresh(account)

        return account

    def update_credit_limit(
        self,
        db: Session,
        *,
        account_id: int,
        credit_limit: Decimal,
        updated_by_id: int,
    ) -> CustomerAccount:
        """Update account credit limit."""
        account = self.get(db, account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        account.credit_limit = credit_limit
        account.updated_by_id = updated_by_id
        account.updated_at = func.now()

        db.add(account)
        db.commit()
        db.refresh(account)

        return account

    def block_account(
        self,
        db: Session,
        *,
        account_id: int,
        blocked_until: datetime,
        block_reason: str,
        updated_by_id: int,
    ) -> CustomerAccount:
        """Block account temporarily."""
        account = self.get(db, account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        account.blocked_until = blocked_until
        account.block_reason = block_reason
        account.updated_by_id = updated_by_id
        account.updated_at = func.now()

        db.add(account)
        db.commit()
        db.refresh(account)

        logger.info(f"Blocked account {account_id} until {blocked_until}")

        return account

    def unblock_account(
        self, db: Session, *, account_id: int, updated_by_id: int
    ) -> CustomerAccount:
        """Unblock account."""
        account = self.get(db, account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        account.blocked_until = None
        account.block_reason = None
        account.updated_by_id = updated_by_id
        account.updated_at = func.now()

        db.add(account)
        db.commit()
        db.refresh(account)

        logger.info(f"Unblocked account {account_id}")

        return account

    def get_transactions(
        self,
        db: Session,
        *,
        customer_id: int,
        skip: int = 0,
        limit: int = 100,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[CustomerTransaction], int]:
        """Get customer transactions with filters."""
        query = (
            db.query(CustomerTransaction)
            .options(joinedload(CustomerTransaction.created_by))
            .filter(CustomerTransaction.customer_id == customer_id)
        )

        # Apply filters
        if transaction_type:
            query = query.filter(
                CustomerTransaction.transaction_type == transaction_type
            )
        if start_date:
            query = query.filter(CustomerTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(CustomerTransaction.transaction_date <= end_date)

        # Get total count
        total = query.count()

        # Get paginated results
        transactions = (
            query.order_by(desc(CustomerTransaction.transaction_date))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return transactions, total

    def get_transaction(
        self, db: Session, transaction_id: int
    ) -> Optional[CustomerTransaction]:
        """Get single transaction by ID."""
        return (
            db.query(CustomerTransaction)
            .options(
                joinedload(CustomerTransaction.customer),
                joinedload(CustomerTransaction.created_by),
            )
            .filter(CustomerTransaction.id == transaction_id)
            .first()
        )

    def get_accounts_with_debt(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        min_balance: Optional[Decimal] = None,
    ) -> tuple[list[CustomerAccount], int]:
        """Get accounts with outstanding debt."""
        query = (
            db.query(CustomerAccount)
            .options(joinedload(CustomerAccount.customer))
            .filter(
                and_(
                    CustomerAccount.account_balance > 0,
                    CustomerAccount.is_active.is_(True),
                )
            )
        )

        if min_balance:
            query = query.filter(CustomerAccount.account_balance >= min_balance)

        # Get total count
        total = query.count()

        # Get paginated results
        accounts = (
            query.order_by(desc(CustomerAccount.account_balance))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return accounts, total

    def get_accounts_with_credit(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CustomerAccount], int]:
        """Get accounts with credit balance."""
        query = (
            db.query(CustomerAccount)
            .options(joinedload(CustomerAccount.customer))
            .filter(
                and_(
                    CustomerAccount.account_balance < 0,
                    CustomerAccount.is_active.is_(True),
                )
            )
        )

        # Get total count
        total = query.count()

        # Get paginated results
        accounts = (
            query.order_by(CustomerAccount.account_balance)  # Most negative first
            .offset(skip)
            .limit(limit)
            .all()
        )

        return accounts, total

    def get_statement_transactions(
        self,
        db: Session,
        *,
        customer_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CustomerTransaction]:
        """Get transactions for statement period."""
        return (
            db.query(CustomerTransaction)
            .options(joinedload(CustomerTransaction.created_by))
            .filter(
                and_(
                    CustomerTransaction.customer_id == customer_id,
                    CustomerTransaction.transaction_date >= start_date,
                    CustomerTransaction.transaction_date <= end_date,
                )
            )
            .order_by(CustomerTransaction.transaction_date)
            .all()
        )

    def get_opening_balance(
        self, db: Session, *, customer_id: int, before_date: datetime
    ) -> Decimal:
        """Get account balance before a specific date."""
        # Get the last transaction before the date
        last_transaction = (
            db.query(CustomerTransaction)
            .filter(
                and_(
                    CustomerTransaction.customer_id == customer_id,
                    CustomerTransaction.transaction_date < before_date,
                )
            )
            .order_by(desc(CustomerTransaction.transaction_date))
            .first()
        )

        if last_transaction:
            return last_transaction.balance_after

        return Decimal("0.00")

    def get_account_summary(self, db: Session) -> dict:
        """Get overall accounts summary."""
        result = (
            db.query(
                func.count(CustomerAccount.id).label("total_accounts"),
                func.sum(
                    func.case([(CustomerAccount.account_balance > 0, 1)], else_=0)
                ).label("accounts_with_debt"),
                func.sum(
                    func.case([(CustomerAccount.account_balance < 0, 1)], else_=0)
                ).label("accounts_with_credit"),
                func.sum(
                    func.case(
                        [
                            (
                                CustomerAccount.account_balance > 0,
                                CustomerAccount.account_balance,
                            )
                        ],
                        else_=0,
                    )
                ).label("total_debt"),
                func.sum(
                    func.case(
                        [
                            (
                                CustomerAccount.account_balance < 0,
                                func.abs(CustomerAccount.account_balance),
                            )
                        ],
                        else_=0,
                    )
                ).label("total_credit"),
            )
            .filter(CustomerAccount.is_active.is_(True))
            .first()
        )

        return {
            "total_accounts": result.total_accounts or 0,
            "accounts_with_debt": result.accounts_with_debt or 0,
            "accounts_with_credit": result.accounts_with_credit or 0,
            "total_debt": result.total_debt or Decimal("0.00"),
            "total_credit": result.total_credit or Decimal("0.00"),
            "net_receivable": (result.total_debt or Decimal("0.00"))
            - (result.total_credit or Decimal("0.00")),
        }


# Create singleton instance
customer_account_crud = CustomerAccountCRUD()
