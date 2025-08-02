"""Unit tests for expense models."""

from datetime import date, datetime
from decimal import Decimal

import pytest
from app.models.expense import Expense, ExpenseCategory
from sqlalchemy.exc import IntegrityError


class TestExpenseCategoryModel:
    """Test cases for ExpenseCategory model."""

    def test_create_expense_category(self, db_session):
        """Test creating a new expense category."""
        category = ExpenseCategory(
            name="Office Supplies",
            description="Office and stationery supplies",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()

        assert category.id is not None
        assert category.name == "Office Supplies"
        assert category.description == "Office and stationery supplies"
        assert category.is_active is True
        assert isinstance(category.created_at, datetime)
        assert isinstance(category.updated_at, datetime)

    def test_unique_category_name(self, db_session):
        """Test that category names must be unique."""
        # Create first category
        category1 = ExpenseCategory(name="Utilities")
        db_session.add(category1)
        db_session.commit()

        # Try to create duplicate
        category2 = ExpenseCategory(name="Utilities")
        db_session.add(category2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_category_soft_delete(self, db_session):
        """Test soft delete functionality."""
        category = ExpenseCategory(
            name="Test Category",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()

        # Soft delete
        category.is_active = False
        db_session.commit()

        # Verify it's marked as inactive
        assert category.is_active is False

        # Verify it still exists in database
        found = db_session.query(ExpenseCategory).filter_by(id=category.id).first()
        assert found is not None
        assert found.is_active is False

    def test_category_relationships(self, db_session):
        """Test relationship with expenses."""
        category = ExpenseCategory(name="Travel")
        db_session.add(category)
        db_session.commit()

        # Category should have empty expenses list initially
        assert category.expenses == []

    def test_category_defaults(self, db_session):
        """Test default values for category."""
        category = ExpenseCategory(name="Test")
        db_session.add(category)
        db_session.commit()

        assert category.is_active is True
        assert category.description is None


class TestExpenseModel:
    """Test cases for Expense model."""

    def test_create_expense(self, db_session, test_user):
        """Test creating a new expense."""
        # Create category first
        category = ExpenseCategory(name="Office Supplies")
        db_session.add(category)
        db_session.commit()

        expense = Expense(
            category_id=category.id,
            amount=Decimal("99.50"),
            description="Printer paper and ink",
            expense_date=date.today(),
            payment_method="cash",
            receipt_number="REC-001",
            supplier_name="Office Depot",
            created_by=test_user.id,
            is_editable=True,
        )
        db_session.add(expense)
        db_session.commit()

        assert expense.id is not None
        assert expense.amount == Decimal("99.50")
        assert expense.description == "Printer paper and ink"
        assert expense.payment_method == "cash"
        assert expense.created_by == test_user.id

    def test_expense_category_relationship(self, db_session, test_user):
        """Test expense-category relationship."""
        category = ExpenseCategory(name="Utilities")
        db_session.add(category)
        db_session.commit()

        expense = Expense(
            category_id=category.id,
            amount=Decimal("150.00"),
            description="Internet bill",
            expense_date=date.today(),
            payment_method="transfer",
            created_by=test_user.id,
        )
        db_session.add(expense)
        db_session.commit()

        # Test relationship
        assert expense.category == category
        assert expense in category.expenses

    def test_expense_required_fields(self, db_session, test_user):
        """Test that required fields are enforced."""
        category = ExpenseCategory(name="Test")
        db_session.add(category)
        db_session.commit()

        # Missing amount
        expense = Expense(
            category_id=category.id,
            description="Test expense",
            expense_date=date.today(),
            payment_method="cash",
            created_by=test_user.id,
        )
        db_session.add(expense)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_expense_payment_methods(self, db_session, test_user):
        """Test different payment methods."""
        category = ExpenseCategory(name="Test")
        db_session.add(category)
        db_session.commit()

        payment_methods = ["cash", "transfer", "card"]

        for method in payment_methods:
            expense = Expense(
                category_id=category.id,
                amount=Decimal("50.00"),
                description=f"Test {method}",
                expense_date=date.today(),
                payment_method=method,
                created_by=test_user.id,
            )
            db_session.add(expense)

        db_session.commit()

        # Verify all were created
        expenses = db_session.query(Expense).filter_by(category_id=category.id).all()
        assert len(expenses) == 3
        assert {e.payment_method for e in expenses} == set(payment_methods)

    def test_expense_optional_fields(self, db_session, test_user):
        """Test optional fields can be null."""
        category = ExpenseCategory(name="Test")
        db_session.add(category)
        db_session.commit()

        expense = Expense(
            category_id=category.id,
            amount=Decimal("25.00"),
            description="Minimal expense",
            expense_date=date.today(),
            payment_method="cash",
            created_by=test_user.id,
        )
        db_session.add(expense)
        db_session.commit()

        assert expense.receipt_number is None
        assert expense.supplier_name is None
        assert expense.receipt_file_path is None

    def test_expense_indexes(self, db_session):
        """Test that indexes are created correctly."""
        # This test verifies that the indexes exist in the database
        from sqlalchemy import inspect

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes("expenses")

        index_names = [idx["name"] for idx in indexes]
        assert "ix_expenses_expense_date" in index_names
        assert "ix_expenses_category_id" in index_names
