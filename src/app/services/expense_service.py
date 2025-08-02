"""Service layer for expense management."""

import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.expense import expense
from app.crud.expense_category import expense_category
from app.models.expense import Expense, ExpenseCategory
from app.models.user import User
from app.schemas.expense import (
    ExpenseCategoryCreate,
    ExpenseCategoryList,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdate,
    ExpenseCreate,
    ExpenseFilter,
    ExpenseResponse,
    ExpenseSummary,
    ExpenseUpdate,
)

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service for managing expenses and expense categories."""

    def create_default_categories(self, db: Session) -> list[ExpenseCategory]:
        """Initialize default categories if they don't exist."""
        default_categories = [
            {"name": "General", "description": "General expenses"},
            {"name": "Suppliers", "description": "Payments to suppliers"},
            {"name": "Utilities", "description": "Electricity, water, internet, etc."},
            {"name": "Salaries", "description": "Employee salaries and benefits"},
            {
                "name": "Maintenance",
                "description": "Equipment and facility maintenance",
            },
            {"name": "Marketing", "description": "Advertising and marketing expenses"},
        ]

        created_categories = []
        for category_data in default_categories:
            existing = expense_category.get_by_name(db, name=category_data["name"])
            if not existing:
                try:
                    category_in = ExpenseCategoryCreate(**category_data)
                    created = expense_category.create(db, obj_in=category_in)
                    created_categories.append(created)
                    logger.info(f"Created default category: {category_data['name']}")
                except Exception as e:
                    logger.error(
                        f"Error creating category {category_data['name']}: {e}"
                    )

        return created_categories

    def manage_category(
        self,
        db: Session,
        *,
        category_id: Optional[int] = None,
        category_create: Optional[ExpenseCategoryCreate] = None,
        category_update: Optional[ExpenseCategoryUpdate] = None,
    ) -> ExpenseCategory:
        """Business logic for category operations."""
        if category_create:
            # Create new category
            logger.info(f"Creating new expense category: {category_create.name}")
            return expense_category.create_category(db, obj_in=category_create)

        elif category_update and category_id:
            # Update existing category
            category = expense_category.get(db, id=category_id)
            if not category:
                raise ValueError(f"Category with id {category_id} not found")

            logger.info(f"Updating expense category {category_id}")
            return expense_category.update_category(
                db, db_obj=category, obj_in=category_update
            )

        else:
            raise ValueError("Invalid operation: provide either create or update data")

    def validate_category_deletion(
        self, db: Session, *, category_id: int
    ) -> tuple[bool, str]:
        """Check if category can be deleted."""
        category = expense_category.get(db, id=category_id)
        if not category:
            return False, "Category not found"

        # Check if category has expenses
        has_expenses = expense_category.check_category_has_expenses(
            db, category_id=category_id
        )

        if has_expenses:
            return False, "Category has associated expenses and cannot be deleted"

        return True, "Category can be deleted"

    def get_categories_for_dropdown(self, db: Session) -> list[ExpenseCategoryList]:
        """Return active categories for dropdown selection."""
        categories = expense_category.get_active_categories(db)
        return [ExpenseCategoryList(id=cat.id, name=cat.name) for cat in categories]

    def get_all_categories(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ExpenseCategoryResponse]:
        """Get all categories with full details."""
        categories = expense_category.get_all_categories(db, skip=skip, limit=limit)
        return [ExpenseCategoryResponse.model_validate(cat) for cat in categories]

    def deactivate_category(self, db: Session, *, category_id: int) -> ExpenseCategory:
        """Deactivate a category (soft delete)."""
        logger.info(f"Deactivating expense category {category_id}")
        return expense_category.deactivate_category(db, category_id=category_id)

    # Expense methods
    def register_expense(
        self,
        db: Session,
        *,
        expense_in: ExpenseCreate,
        current_user: User,
    ) -> Expense:
        """Create new expense with validation."""
        # Validate category exists and is active
        category = expense_category.get(db, id=expense_in.category_id)
        if not category:
            raise ValueError("Invalid category")
        if not category.is_active:
            raise ValueError("Category is not active")

        # Validate expense date
        self.validate_expense_date(expense_in.expense_date)

        # Create expense
        logger.info(
            f"Creating expense: {expense_in.amount} in category {category.name} "
            f"by user {current_user.email}"
        )

        return expense.create_expense(db, obj_in=expense_in, created_by=current_user.id)

    def update_expense(
        self,
        db: Session,
        *,
        expense_id: int,
        expense_in: ExpenseUpdate,
        current_user: User,
    ) -> Expense:
        """Update expense with same-day validation."""
        # Get expense
        db_expense = expense.get(db, id=expense_id)
        if not db_expense:
            raise ValueError("Expense not found")

        # Check edit permissions
        if not expense.check_expense_editable(db_expense, current_user.id):
            raise ValueError(
                "Expense can only be edited on the same day by the creator"
            )

        logger.info(f"Updating expense {expense_id} by user {current_user.email}")

        return expense.update_expense(
            db,
            db_obj=db_expense,
            obj_in=expense_in,
            current_user_id=current_user.id,
        )

    def get_expense_summary(self, db: Session, *, target_date: date) -> ExpenseSummary:
        """Get expense summary for daily closing."""
        return expense.get_expense_summary(db, target_date=target_date)

    def validate_expense_date(self, expense_date: date) -> None:
        """Ensure expense date is not in the future."""
        if expense_date > date.today():
            raise ValueError("Expense date cannot be in the future")

    def handle_receipt_upload(
        self,
        db: Session,
        *,
        expense_id: int,
        file_path: str,
        current_user: User,
    ) -> Expense:
        """Update expense with receipt file path."""
        db_expense = expense.get(db, id=expense_id)
        if not db_expense:
            raise ValueError("Expense not found")

        # Check if user can edit
        if db_expense.created_by != current_user.id:
            raise ValueError("You can only upload receipts for your own expenses")

        # Update file path
        db_expense.receipt_file_path = file_path
        db.commit()
        db.refresh(db_expense)

        logger.info(f"Receipt uploaded for expense {expense_id}")
        return db_expense

    def get_expenses_with_filters(
        self,
        db: Session,
        *,
        filters: ExpenseFilter,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExpenseResponse]:
        """Get expenses with filters and convert to response schema."""
        expenses = expense.get_expenses_with_filters(
            db, filters=filters, skip=skip, limit=limit
        )

        # Get users for all expenses in a single query
        user_ids = [exp.created_by for exp in expenses]
        from app.models.user import User

        users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
        user_map = {user.id: user for user in users}

        return [
            ExpenseResponse(
                **exp.__dict__,
                category_name=exp.category.name,
                created_by_name=user_map[exp.created_by].full_name
                if exp.created_by in user_map
                else "Unknown",
            )
            for exp in expenses
        ]

    def get_daily_expenses(self, db: Session, *, target_date: date) -> list[Expense]:
        """Get all expenses for a specific date."""
        return expense.get_daily_expenses(db, target_date=target_date)


# Create singleton instance
expense_service = ExpenseService()
