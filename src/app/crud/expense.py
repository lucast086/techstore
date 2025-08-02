"""CRUD operations for expenses."""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.expense import Expense
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseFilter,
    ExpenseSummary,
    ExpenseUpdate,
)


class CRUDExpense(CRUDBase[Expense, ExpenseCreate, ExpenseUpdate]):
    """CRUD operations for expenses."""

    def create_expense(
        self, db: Session, *, obj_in: ExpenseCreate, created_by: int
    ) -> Expense:
        """Create new expense."""
        db_obj = Expense(
            **obj_in.model_dump(),
            created_by=created_by,
            is_editable=True,  # New expenses are always editable on creation day
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_expense(
        self,
        db: Session,
        *,
        db_obj: Expense,
        obj_in: ExpenseUpdate,
        current_user_id: int,
    ) -> Expense:
        """Update expense if same day and created by user."""
        # Check if expense is editable
        if not self.check_expense_editable(db_obj, current_user_id):
            raise ValueError(
                "Expense can only be edited on the same day by the creator"
            )

        # Update expense
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_expenses_by_date_range(
        self,
        db: Session,
        *,
        date_from: date,
        date_to: date,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Expense]:
        """Get expenses within date range."""
        stmt = (
            select(Expense)
            .options(joinedload(Expense.category), joinedload(Expense.user))
            .where(
                and_(Expense.expense_date >= date_from, Expense.expense_date <= date_to)
            )
            .order_by(Expense.expense_date.desc(), Expense.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return db.execute(stmt).scalars().all()

    def get_expenses_by_category(
        self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> list[Expense]:
        """Get expenses by category."""
        stmt = (
            select(Expense)
            .options(joinedload(Expense.category), joinedload(Expense.user))
            .where(Expense.category_id == category_id)
            .order_by(Expense.expense_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return db.execute(stmt).scalars().all()

    def get_daily_expenses(self, db: Session, *, target_date: date) -> list[Expense]:
        """Get all expenses for a specific date (for cash closing)."""
        stmt = (
            select(Expense)
            .options(joinedload(Expense.category))
            .where(Expense.expense_date == target_date)
            .order_by(Expense.created_at)
        )
        return db.execute(stmt).scalars().all()

    def get_expense_summary(self, db: Session, *, target_date: date) -> ExpenseSummary:
        """Get expense summary for a specific date."""
        expenses = self.get_daily_expenses(db, target_date=target_date)

        if not expenses:
            return ExpenseSummary(
                total_amount=Decimal("0.00"),
                expense_count=0,
                by_category={},
                by_payment_method={},
            )

        # Calculate summaries
        total_amount = sum(exp.amount for exp in expenses)
        by_category = {}
        by_payment_method = {}

        for expense in expenses:
            # By category
            cat_name = expense.category.name
            by_category[cat_name] = (
                by_category.get(cat_name, Decimal("0.00")) + expense.amount
            )

            # By payment method
            by_payment_method[expense.payment_method] = (
                by_payment_method.get(expense.payment_method, Decimal("0.00"))
                + expense.amount
            )

        return ExpenseSummary(
            total_amount=total_amount,
            expense_count=len(expenses),
            by_category=by_category,
            by_payment_method=by_payment_method,
        )

    def get_expenses_with_filters(
        self, db: Session, *, filters: ExpenseFilter, skip: int = 0, limit: int = 100
    ) -> list[Expense]:
        """Get expenses with multiple filters."""
        stmt = select(Expense).options(
            joinedload(Expense.category), joinedload(Expense.user)
        )

        # Apply filters
        conditions = []

        if filters.date_from:
            conditions.append(Expense.expense_date >= filters.date_from)
        if filters.date_to:
            conditions.append(Expense.expense_date <= filters.date_to)
        if filters.category_id:
            conditions.append(Expense.category_id == filters.category_id)
        if filters.min_amount:
            conditions.append(Expense.amount >= filters.min_amount)
        if filters.max_amount:
            conditions.append(Expense.amount <= filters.max_amount)
        if filters.payment_method:
            conditions.append(Expense.payment_method == filters.payment_method)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(Expense.expense_date.desc(), Expense.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        return db.execute(stmt).scalars().all()

    def check_expense_editable(self, expense: Expense, current_user_id: int) -> bool:
        """Verify if expense can be edited (same day rule)."""
        # Must be created by the current user
        if expense.created_by != current_user_id:
            return False

        # Must be same day as creation
        if expense.created_at.date() != date.today():
            return False

        return True

    def update_editability_status(self, db: Session) -> int:
        """Update is_editable flag for expenses older than today."""
        # This could be run as a daily job
        yesterday = date.today() - timedelta(days=1)

        stmt = select(Expense).where(
            and_(Expense.is_editable.is_(True), Expense.created_at < yesterday)
        )

        expenses_to_update = db.execute(stmt).scalars().all()
        count = 0

        for expense in expenses_to_update:
            expense.is_editable = False
            count += 1

        if count > 0:
            db.commit()

        return count


# Create instance to use throughout the application
expense = CRUDExpense(Expense)
