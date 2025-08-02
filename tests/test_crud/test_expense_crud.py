"""Tests for expense CRUD operations."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from app.crud.expense import expense
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseFilter, ExpenseUpdate


class TestExpenseCRUD:
    """Test cases for expense CRUD operations."""

    def test_create_expense(self, db_session, test_user, test_expense_category):
        """Test creating a new expense."""
        expense_in = ExpenseCreate(
            category_id=test_expense_category.id,
            amount=Decimal("150.00"),
            description="Office supplies purchase",
            expense_date=date.today(),
            payment_method="card",
            receipt_number="REC-2024-001",
            supplier_name="Office Max",
        )

        new_expense = expense.create_expense(
            db_session, obj_in=expense_in, created_by=test_user.id
        )

        assert new_expense.id is not None
        assert new_expense.amount == Decimal("150.00")
        assert new_expense.description == "Office supplies purchase"
        assert new_expense.created_by == test_user.id
        assert new_expense.is_editable is True

    def test_get_expense(self, db_session, test_expense):
        """Test retrieving an expense by ID."""
        found = expense.get(db_session, id=test_expense.id)

        assert found is not None
        assert found.id == test_expense.id
        assert found.amount == test_expense.amount

    def test_update_expense_same_day(self, db_session, test_expense, test_user):
        """Test updating an expense on the same day."""
        update_data = ExpenseUpdate(
            amount=Decimal("200.00"),
            description="Updated description",
            payment_method="transfer",
        )

        updated = expense.update_expense(
            db_session,
            db_obj=test_expense,
            obj_in=update_data,
            current_user_id=test_user.id,
        )

        assert updated.amount == Decimal("200.00")
        assert updated.description == "Updated description"
        assert updated.payment_method == "transfer"

    def test_update_expense_different_user(self, db_session, test_expense):
        """Test that users can't edit other users' expenses."""
        different_user_id = test_expense.created_by + 1
        update_data = ExpenseUpdate(amount=Decimal("200.00"))

        with pytest.raises(
            ValueError, match="can only be edited on the same day by the creator"
        ):
            expense.update_expense(
                db_session,
                db_obj=test_expense,
                obj_in=update_data,
                current_user_id=different_user_id,
            )

    def test_check_expense_editable(self, db_session, test_expense, test_user):
        """Test expense editability check."""
        # Same day, same user - should be editable
        is_editable = expense.check_expense_editable(test_expense, test_user.id)
        assert is_editable is True

        # Different user - should not be editable
        is_editable = expense.check_expense_editable(test_expense, test_user.id + 1)
        assert is_editable is False

    def test_get_expenses_by_date_range(
        self, db_session, test_user, test_expense_category
    ):
        """Test retrieving expenses within a date range."""
        # Create expenses for different dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        expenses_data = [
            {"expense_date": today, "amount": Decimal("100.00")},
            {"expense_date": yesterday, "amount": Decimal("200.00")},
            {"expense_date": week_ago, "amount": Decimal("300.00")},
        ]

        for data in expenses_data:
            exp = Expense(
                category_id=test_expense_category.id,
                description="Test expense",
                payment_method="cash",
                created_by=test_user.id,
                **data,
            )
            db_session.add(exp)
        db_session.commit()

        # Get expenses from yesterday to today
        expenses = expense.get_expenses_by_date_range(
            db_session, date_from=yesterday, date_to=today
        )

        # Should have 2 expenses (today and yesterday)
        assert len(expenses) >= 2
        amounts = [exp.amount for exp in expenses]
        assert Decimal("100.00") in amounts
        assert Decimal("200.00") in amounts

    def test_get_expenses_by_category(
        self, db_session, test_user, test_expense_category
    ):
        """Test retrieving expenses by category."""
        # Create another category
        from app.models.expense import ExpenseCategory

        other_category = ExpenseCategory(name="Other Category")
        db_session.add(other_category)
        db_session.commit()

        # Create expenses in different categories
        expense1 = Expense(
            category_id=test_expense_category.id,
            amount=Decimal("50.00"),
            description="Category 1 expense",
            expense_date=date.today(),
            payment_method="cash",
            created_by=test_user.id,
        )
        expense2 = Expense(
            category_id=other_category.id,
            amount=Decimal("75.00"),
            description="Category 2 expense",
            expense_date=date.today(),
            payment_method="card",
            created_by=test_user.id,
        )
        db_session.add_all([expense1, expense2])
        db_session.commit()

        # Get expenses for test category only
        expenses = expense.get_expenses_by_category(
            db_session, category_id=test_expense_category.id
        )

        # Should only have expenses from test category
        category_ids = {exp.category_id for exp in expenses}
        assert test_expense_category.id in category_ids
        assert other_category.id not in category_ids

    def test_get_daily_expenses(self, db_session, test_user, test_expense_category):
        """Test retrieving expenses for a specific date."""
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
        daily_expenses = expense.get_daily_expenses(db_session, target_date=today)

        # Should only have today's expense
        dates = {exp.expense_date for exp in daily_expenses}
        assert today in dates
        assert yesterday not in dates

    def test_get_expense_summary(self, db_session, test_user):
        """Test expense summary generation."""
        from app.models.expense import ExpenseCategory

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
            },
            {
                "category_id": cat1.id,
                "amount": Decimal("30.00"),
                "payment_method": "card",
            },
            {
                "category_id": cat2.id,
                "amount": Decimal("20.00"),
                "payment_method": "cash",
            },
        ]

        for data in expenses_data:
            exp = Expense(
                description="Test expense",
                expense_date=today,
                created_by=test_user.id,
                **data,
            )
            db_session.add(exp)
        db_session.commit()

        # Get summary
        summary = expense.get_expense_summary(db_session, target_date=today)

        assert summary.total_amount == Decimal("100.00")
        assert summary.expense_count == 3
        assert summary.by_category["Food"] == Decimal("80.00")
        assert summary.by_category["Transport"] == Decimal("20.00")
        assert summary.by_payment_method["cash"] == Decimal("70.00")
        assert summary.by_payment_method["card"] == Decimal("30.00")

    def test_get_expenses_with_filters(
        self, db_session, test_user, test_expense_category
    ):
        """Test retrieving expenses with multiple filters."""
        # Create test data
        today = date.today()
        expenses_data = [
            {
                "amount": Decimal("100.00"),
                "payment_method": "cash",
                "expense_date": today,
            },
            {
                "amount": Decimal("200.00"),
                "payment_method": "card",
                "expense_date": today - timedelta(days=1),
            },
            {
                "amount": Decimal("50.00"),
                "payment_method": "transfer",
                "expense_date": today,
            },
        ]

        for data in expenses_data:
            exp = Expense(
                category_id=test_expense_category.id,
                description="Test expense",
                created_by=test_user.id,
                **data,
            )
            db_session.add(exp)
        db_session.commit()

        # Test various filters
        filters = ExpenseFilter(date_from=today, date_to=today, payment_method="cash")

        filtered = expense.get_expenses_with_filters(db_session, filters=filters)

        # Should only have today's cash expense
        assert len(filtered) >= 1
        for exp in filtered:
            assert exp.expense_date == today
            assert exp.payment_method == "cash"

    def test_update_editability_status(
        self, db_session, test_user, test_expense_category
    ):
        """Test updating editability status for old expenses."""
        from datetime import datetime

        # Create an expense with created_at in the past
        yesterday = date.today() - timedelta(days=1)
        old_expense = Expense(
            category_id=test_expense_category.id,
            amount=Decimal("100.00"),
            description="Old expense",
            expense_date=yesterday,
            payment_method="cash",
            created_by=test_user.id,
            is_editable=True,
        )
        db_session.add(old_expense)
        db_session.commit()

        # Manually set created_at to 2 days ago (before yesterday)
        two_days_ago = datetime.now() - timedelta(days=2)
        old_expense.created_at = two_days_ago
        db_session.commit()

        # Run update
        count = expense.update_editability_status(db_session)

        # Check that the expense is no longer editable
        db_session.refresh(old_expense)
        assert old_expense.is_editable is False
        assert count >= 1
