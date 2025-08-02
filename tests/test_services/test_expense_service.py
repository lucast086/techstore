"""Tests for expense service layer."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from app.models.expense import Expense, ExpenseCategory
from app.schemas.expense import (
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCreate,
    ExpenseFilter,
    ExpenseUpdate,
)
from app.services.expense_service import expense_service


class TestExpenseService:
    """Test cases for expense service layer."""

    def test_create_default_categories(self, db_session):
        """Test creating default expense categories."""
        # Clear any existing categories
        db_session.query(ExpenseCategory).delete()
        db_session.commit()

        # Create default categories
        created = expense_service.create_default_categories(db_session)

        # Should create 6 default categories
        assert len(created) == 6

        # Check category names
        category_names = [cat.name for cat in created]
        assert "General" in category_names
        assert "Suppliers" in category_names
        assert "Utilities" in category_names
        assert "Salaries" in category_names
        assert "Maintenance" in category_names
        assert "Marketing" in category_names

    def test_create_default_categories_idempotent(self, db_session):
        """Test that creating default categories is idempotent."""
        # First run
        expense_service.create_default_categories(db_session)

        # Count categories
        first_count = db_session.query(ExpenseCategory).count()

        # Second run should not create duplicates
        expense_service.create_default_categories(db_session)

        # Count should be the same
        second_count = db_session.query(ExpenseCategory).count()
        assert first_count == second_count

    def test_manage_category_create(self, db_session):
        """Test category creation through service."""
        category_create = ExpenseCategoryCreate(
            name="New Category", description="Test description"
        )

        category = expense_service.manage_category(
            db_session, category_create=category_create
        )

        assert category.name == "New Category"
        assert category.description == "Test description"
        assert category.is_active is True

    def test_manage_category_update(self, db_session, test_expense_category):
        """Test category update through service."""
        category_update = ExpenseCategoryUpdate(name="Updated Name", is_active=False)

        updated = expense_service.manage_category(
            db_session,
            category_id=test_expense_category.id,
            category_update=category_update,
        )

        assert updated.id == test_expense_category.id
        assert updated.name == "Updated Name"
        assert updated.is_active is False

    def test_manage_category_invalid_operation(self, db_session):
        """Test that invalid operations raise ValueError."""
        with pytest.raises(ValueError, match="Invalid operation"):
            expense_service.manage_category(db_session)

    def test_validate_category_deletion(
        self, db_session, test_expense_category, test_expense
    ):
        """Test category deletion validation."""
        # Category with expenses should not be deletable
        can_delete, message = expense_service.validate_category_deletion(
            db_session, category_id=test_expense_category.id
        )
        assert can_delete is False
        assert "has associated expenses" in message

        # Create empty category
        empty_category = ExpenseCategory(name="Empty Category")
        db_session.add(empty_category)
        db_session.commit()

        # Empty category should be deletable
        can_delete, message = expense_service.validate_category_deletion(
            db_session, category_id=empty_category.id
        )
        assert can_delete is True
        assert "can be deleted" in message

    def test_validate_category_deletion_not_found(self, db_session):
        """Test deletion validation for non-existent category."""
        can_delete, message = expense_service.validate_category_deletion(
            db_session, category_id=99999
        )
        assert can_delete is False
        assert "not found" in message

    def test_get_categories_for_dropdown(self, db_session):
        """Test getting active categories for dropdown."""
        # Create active and inactive categories
        active1 = ExpenseCategory(name="Active 1", is_active=True)
        active2 = ExpenseCategory(name="Active 2", is_active=True)
        inactive = ExpenseCategory(name="Inactive", is_active=False)

        db_session.add_all([active1, active2, inactive])
        db_session.commit()

        # Get dropdown categories
        dropdown_categories = expense_service.get_categories_for_dropdown(db_session)

        # Should only include active categories
        names = [cat.name for cat in dropdown_categories]
        assert "Active 1" in names
        assert "Active 2" in names
        assert "Inactive" not in names

    def test_register_expense(self, db_session, test_user, test_expense_category):
        """Test expense registration through service."""
        expense_create = ExpenseCreate(
            category_id=test_expense_category.id,
            amount=Decimal("250.00"),
            description="Service test expense",
            expense_date=date.today(),
            payment_method="card",
            supplier_name="Test Supplier",
        )

        expense = expense_service.register_expense(
            db_session, expense_in=expense_create, current_user=test_user
        )

        assert expense.amount == Decimal("250.00")
        assert expense.created_by == test_user.id
        assert expense.category_id == test_expense_category.id

    def test_register_expense_invalid_category(self, db_session, test_user):
        """Test expense registration with invalid category."""
        expense_create = ExpenseCreate(
            category_id=99999,
            amount=Decimal("100.00"),
            description="Test",
            expense_date=date.today(),
            payment_method="cash",
        )

        with pytest.raises(ValueError, match="Invalid category"):
            expense_service.register_expense(
                db_session, expense_in=expense_create, current_user=test_user
            )

    def test_register_expense_inactive_category(self, db_session, test_user):
        """Test expense registration with inactive category."""
        # Create inactive category
        inactive_category = ExpenseCategory(name="Inactive Category", is_active=False)
        db_session.add(inactive_category)
        db_session.commit()

        expense_create = ExpenseCreate(
            category_id=inactive_category.id,
            amount=Decimal("100.00"),
            description="Test",
            expense_date=date.today(),
            payment_method="cash",
        )

        with pytest.raises(ValueError, match="Category is not active"):
            expense_service.register_expense(
                db_session, expense_in=expense_create, current_user=test_user
            )

    def test_validate_expense_date(self):
        """Test expense date validation."""
        # Today's date should be valid
        expense_service.validate_expense_date(date.today())

        # Yesterday should be valid
        expense_service.validate_expense_date(date.today() - timedelta(days=1))

        # Future date should raise error
        future_date = date.today() + timedelta(days=1)
        with pytest.raises(ValueError, match="cannot be in the future"):
            expense_service.validate_expense_date(future_date)

    def test_update_expense(self, db_session, test_expense, test_user):
        """Test expense update through service."""
        expense_update = ExpenseUpdate(
            amount=Decimal("300.00"), description="Updated through service"
        )

        updated = expense_service.update_expense(
            db_session,
            expense_id=test_expense.id,
            expense_in=expense_update,
            current_user=test_user,
        )

        assert updated.amount == Decimal("300.00")
        assert updated.description == "Updated through service"

    def test_update_expense_not_found(self, db_session, test_user):
        """Test updating non-existent expense."""
        expense_update = ExpenseUpdate(amount=Decimal("100.00"))

        with pytest.raises(ValueError, match="Expense not found"):
            expense_service.update_expense(
                db_session,
                expense_id=99999,
                expense_in=expense_update,
                current_user=test_user,
            )

    def test_update_expense_different_user(self, db_session, test_expense):
        """Test that users can't update other users' expenses."""
        from app.models.user import User

        # Create different user
        other_user = User(
            email="other@example.com",
            password_hash="hash",
            full_name="Other User",
            role="technician",
        )
        db_session.add(other_user)
        db_session.commit()

        expense_update = ExpenseUpdate(amount=Decimal("100.00"))

        with pytest.raises(ValueError, match="can only be edited"):
            expense_service.update_expense(
                db_session,
                expense_id=test_expense.id,
                expense_in=expense_update,
                current_user=other_user,
            )

    def test_get_expense_summary(self, db_session, test_user):
        """Test getting expense summary for a date."""
        # Create categories
        cat1 = ExpenseCategory(name="Food")
        cat2 = ExpenseCategory(name="Transport")
        db_session.add_all([cat1, cat2])
        db_session.commit()

        # Create expenses for today
        today = date.today()
        expenses_data = [
            {
                "category_id": cat1.id,
                "amount": Decimal("50.00"),
                "payment_method": "cash",
                "description": "Lunch",
            },
            {
                "category_id": cat1.id,
                "amount": Decimal("30.00"),
                "payment_method": "card",
                "description": "Dinner",
            },
            {
                "category_id": cat2.id,
                "amount": Decimal("20.00"),
                "payment_method": "cash",
                "description": "Taxi",
            },
        ]

        for data in expenses_data:
            expense = Expense(expense_date=today, created_by=test_user.id, **data)
            db_session.add(expense)
        db_session.commit()

        # Get summary
        summary = expense_service.get_expense_summary(db_session, target_date=today)

        assert summary.total_amount == Decimal("100.00")
        assert summary.expense_count == 3
        assert summary.by_category["Food"] == Decimal("80.00")
        assert summary.by_category["Transport"] == Decimal("20.00")
        assert summary.by_payment_method["cash"] == Decimal("70.00")
        assert summary.by_payment_method["card"] == Decimal("30.00")

    def test_handle_receipt_upload(self, db_session, test_expense, test_user):
        """Test handling receipt file upload."""
        file_path = "/uploads/receipts/test-receipt.pdf"

        updated = expense_service.handle_receipt_upload(
            db_session,
            expense_id=test_expense.id,
            file_path=file_path,
            current_user=test_user,
        )

        assert updated.receipt_file_path == file_path

    def test_handle_receipt_upload_different_user(self, db_session, test_expense):
        """Test that users can only upload receipts for their own expenses."""
        from app.models.user import User

        # Create different user
        other_user = User(
            email="other@example.com",
            password_hash="hash",
            full_name="Other User",
            role="technician",
        )
        db_session.add(other_user)
        db_session.commit()

        with pytest.raises(
            ValueError, match="only upload receipts for your own expenses"
        ):
            expense_service.handle_receipt_upload(
                db_session,
                expense_id=test_expense.id,
                file_path="/test.pdf",
                current_user=other_user,
            )

    def test_get_expenses_with_filters(
        self, db_session, test_user, test_expense_category
    ):
        """Test getting expenses with filters."""
        # Create test expenses
        today = date.today()
        yesterday = today - timedelta(days=1)

        expense1 = Expense(
            category_id=test_expense_category.id,
            amount=Decimal("100.00"),
            description="Today cash",
            expense_date=today,
            payment_method="cash",
            created_by=test_user.id,
        )
        expense2 = Expense(
            category_id=test_expense_category.id,
            amount=Decimal("200.00"),
            description="Yesterday card",
            expense_date=yesterday,
            payment_method="card",
            created_by=test_user.id,
        )
        db_session.add_all([expense1, expense2])
        db_session.commit()

        # Test date filter
        filters = ExpenseFilter(date_from=today, date_to=today)
        expenses = expense_service.get_expenses_with_filters(
            db_session, filters=filters
        )

        # Should only have today's expense
        assert len(expenses) >= 1
        for exp in expenses:
            assert exp.expense_date == today
            assert exp.created_by_name == test_user.full_name

    def test_get_daily_expenses(self, db_session, test_user, test_expense_category):
        """Test getting expenses for a specific date."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Create expenses for different dates
        today_expense = Expense(
            category_id=test_expense_category.id,
            amount=Decimal("100.00"),
            description="Today's expense",
            expense_date=today,
            payment_method="cash",
            created_by=test_user.id,
        )
        yesterday_expense = Expense(
            category_id=test_expense_category.id,
            amount=Decimal("200.00"),
            description="Yesterday's expense",
            expense_date=yesterday,
            payment_method="card",
            created_by=test_user.id,
        )
        db_session.add_all([today_expense, yesterday_expense])
        db_session.commit()

        # Get only today's expenses
        daily_expenses = expense_service.get_daily_expenses(
            db_session, target_date=today
        )

        # Should only have today's expense
        assert len(daily_expenses) >= 1
        for exp in daily_expenses:
            assert exp.expense_date == today
