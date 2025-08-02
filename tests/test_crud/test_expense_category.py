"""Tests for expense category CRUD operations."""

import pytest
from app.crud.expense_category import expense_category
from app.models.expense import ExpenseCategory
from app.schemas.expense import ExpenseCategoryCreate, ExpenseCategoryUpdate


class TestExpenseCategoryCRUD:
    """Test cases for expense category CRUD operations."""

    def test_create_category(self, db_session):
        """Test creating a new expense category."""
        category_in = ExpenseCategoryCreate(
            name="Office Supplies", description="Office and stationery supplies"
        )

        category = expense_category.create_category(db_session, obj_in=category_in)

        assert category.id is not None
        assert category.name == "Office Supplies"
        assert category.description == "Office and stationery supplies"
        assert category.is_active is True

    def test_get_category(self, db_session, test_expense_category):
        """Test retrieving a category by ID."""
        category = expense_category.get(db_session, id=test_expense_category.id)

        assert category is not None
        assert category.id == test_expense_category.id
        assert category.name == test_expense_category.name

    def test_get_by_name(self, db_session, test_expense_category):
        """Test retrieving a category by name."""
        category = expense_category.get_by_name(
            db_session, name=test_expense_category.name
        )

        assert category is not None
        assert category.id == test_expense_category.id
        assert category.name == test_expense_category.name

    def test_get_all_categories(self, db_session):
        """Test retrieving all categories."""
        # Create multiple categories
        categories_data = [
            {"name": "Category 1", "description": "First"},
            {"name": "Category 2", "description": "Second"},
            {"name": "Category 3", "description": "Third"},
        ]

        for data in categories_data:
            category = ExpenseCategory(**data)
            db_session.add(category)
        db_session.commit()

        # Get all categories
        all_categories = expense_category.get_all_categories(db_session)

        assert len(all_categories) >= 3
        category_names = [cat.name for cat in all_categories]
        assert "Category 1" in category_names
        assert "Category 2" in category_names
        assert "Category 3" in category_names

    def test_get_active_categories(self, db_session):
        """Test retrieving only active categories."""
        # Create active and inactive categories
        active_cat = ExpenseCategory(name="Active", is_active=True)
        inactive_cat = ExpenseCategory(name="Inactive", is_active=False)

        db_session.add_all([active_cat, inactive_cat])
        db_session.commit()

        # Get only active categories
        active_categories = expense_category.get_active_categories(db_session)

        # Check that inactive category is not included
        category_names = [cat.name for cat in active_categories]
        assert "Active" in category_names
        assert "Inactive" not in category_names

    def test_update_category(self, db_session, test_expense_category):
        """Test updating a category."""
        update_data = ExpenseCategoryUpdate(
            name="Updated Name", description="Updated description", is_active=False
        )

        updated = expense_category.update_category(
            db_session, db_obj=test_expense_category, obj_in=update_data
        )

        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.is_active is False

    def test_partial_update_category(self, db_session, test_expense_category):
        """Test partial update of a category."""
        original_name = test_expense_category.name

        update_data = ExpenseCategoryUpdate(description="Only update description")

        updated = expense_category.update_category(
            db_session, db_obj=test_expense_category, obj_in=update_data
        )

        assert updated.name == original_name  # Name unchanged
        assert updated.description == "Only update description"

    def test_deactivate_category(self, db_session, test_expense_category):
        """Test deactivating a category."""
        assert test_expense_category.is_active is True

        deactivated = expense_category.deactivate_category(
            db_session, category_id=test_expense_category.id
        )

        assert deactivated.is_active is False
        assert deactivated.id == test_expense_category.id

    def test_check_category_has_expenses(
        self, db_session, test_expense_category, test_expense
    ):
        """Test checking if category has associated expenses."""
        # Category with expense should return True
        has_expenses = expense_category.check_category_has_expenses(
            db_session, category_id=test_expense_category.id
        )
        assert has_expenses is True

        # Create empty category
        empty_category = ExpenseCategory(name="Empty Category")
        db_session.add(empty_category)
        db_session.commit()

        # Empty category should return False
        has_expenses = expense_category.check_category_has_expenses(
            db_session, category_id=empty_category.id
        )
        assert has_expenses is False

    def test_create_category_duplicate_name(self, db_session, test_expense_category):
        """Test that duplicate category names are not allowed."""
        duplicate = ExpenseCategoryCreate(name=test_expense_category.name)

        with pytest.raises(ValueError, match="already exists"):
            expense_category.create_category(db_session, obj_in=duplicate)

    def test_pagination(self, db_session):
        """Test pagination of category list."""
        # Create many categories
        for i in range(15):
            category = ExpenseCategory(name=f"Category {i:02d}")
            db_session.add(category)
        db_session.commit()

        # Test pagination
        page1 = expense_category.get_all_categories(db_session, skip=0, limit=5)
        page2 = expense_category.get_all_categories(db_session, skip=5, limit=5)
        page3 = expense_category.get_all_categories(db_session, skip=10, limit=5)

        assert len(page1) == 5
        assert len(page2) == 5
        assert len(page3) >= 5  # May have test categories too

        # Ensure no overlap
        page1_ids = {cat.id for cat in page1}
        page2_ids = {cat.id for cat in page2}
        assert page1_ids.isdisjoint(page2_ids)
