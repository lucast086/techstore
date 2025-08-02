"""CRUD operations for expense categories."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.expense import ExpenseCategory
from app.schemas.expense import ExpenseCategoryCreate, ExpenseCategoryUpdate


class CRUDExpenseCategory(
    CRUDBase[ExpenseCategory, ExpenseCategoryCreate, ExpenseCategoryUpdate]
):
    """CRUD operations for expense categories."""

    def get_all_categories(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ExpenseCategory]:
        """Retrieve all expense categories."""
        stmt = select(self.model).offset(skip).limit(limit).order_by(self.model.name)
        return db.execute(stmt).scalars().all()

    def get_active_categories(self, db: Session) -> list[ExpenseCategory]:
        """Retrieve only active expense categories for dropdowns."""
        stmt = (
            select(self.model)
            .where(self.model.is_active.is_(True))
            .order_by(self.model.name)
        )
        return db.execute(stmt).scalars().all()

    def get_by_name(self, db: Session, *, name: str) -> Optional[ExpenseCategory]:
        """Get expense category by name."""
        stmt = select(self.model).where(self.model.name == name)
        return db.execute(stmt).scalar_one_or_none()

    def create_category(
        self, db: Session, *, obj_in: ExpenseCategoryCreate
    ) -> ExpenseCategory:
        """Create new expense category."""
        # Check if category with same name exists
        existing = self.get_by_name(db, name=obj_in.name)
        if existing:
            raise ValueError(f"Category with name '{obj_in.name}' already exists")

        return self.create(db, obj_in=obj_in)

    def update_category(
        self, db: Session, *, db_obj: ExpenseCategory, obj_in: ExpenseCategoryUpdate
    ) -> ExpenseCategory:
        """Update expense category."""
        # If updating name, check for duplicates
        if obj_in.name and obj_in.name != db_obj.name:
            existing = self.get_by_name(db, name=obj_in.name)
            if existing:
                raise ValueError(f"Category with name '{obj_in.name}' already exists")

        return self.update(db, db_obj=db_obj, obj_in=obj_in)

    def deactivate_category(self, db: Session, *, category_id: int) -> ExpenseCategory:
        """Soft delete by setting is_active=False."""
        category = self.get(db, id=category_id)
        if not category:
            raise ValueError(f"Category with id {category_id} not found")

        # Check if category has expenses before deactivating
        if self.check_category_has_expenses(db, category_id=category_id):
            # For now, we'll allow deactivation even with expenses
            # In the future, we might want to prevent this
            pass

        category.is_active = False
        db.commit()
        db.refresh(category)
        return category

    def check_category_has_expenses(self, db: Session, *, category_id: int) -> bool:
        """Verify if category has any associated expenses."""
        from app.models.expense import Expense

        stmt = select(Expense).where(Expense.category_id == category_id).limit(1)
        result = db.execute(stmt).first()
        return result is not None


# Create instance to use throughout the application
expense_category = CRUDExpenseCategory(ExpenseCategory)
