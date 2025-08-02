"""Tests for expense API endpoints."""

from datetime import date, timedelta
from decimal import Decimal

from fastapi import status
from fastapi.testclient import TestClient


class TestExpenseAPI:
    """Test cases for expense API endpoints."""

    def test_register_expense_unauthenticated(self, client: TestClient):
        """Test that unauthenticated requests are rejected."""
        expense_data = {
            "category_id": 1,
            "amount": "100.00",
            "description": "Test expense",
            "expense_date": str(date.today()),
            "payment_method": "cash",
        }
        response = client.post("/api/v1/expenses/", json=expense_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_expense(self, client, test_user, test_expense_category):
        """Test registering a new expense."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Create expense
        expense_data = {
            "category_id": test_expense_category.id,
            "amount": "250.50",
            "description": "Office supplies purchase",
            "expense_date": str(date.today()),
            "payment_method": "card",
            "receipt_number": "REC-2024-001",
            "supplier_name": "Office Max",
        }
        response = client.post(
            "/api/v1/expenses/",
            json=expense_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["amount"] == "250.50"
        assert data["description"] == "Office supplies purchase"
        assert data["created_by"] == test_user.id
        assert data["is_editable"] is True
        assert "id" in data

    def test_register_expense_invalid_category(self, client, test_user):
        """Test registering expense with invalid category."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to create expense with non-existent category
        expense_data = {
            "category_id": 99999,
            "amount": "100.00",
            "description": "Test",
            "expense_date": str(date.today()),
            "payment_method": "cash",
        }
        response = client.post(
            "/api/v1/expenses/",
            json=expense_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid category" in response.json()["detail"]

    def test_register_expense_inactive_category(self, client, test_user, db_session):
        """Test registering expense with inactive category."""
        from app.models.expense import ExpenseCategory

        # Create inactive category
        inactive_category = ExpenseCategory(name="Inactive Category", is_active=False)
        db_session.add(inactive_category)
        db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to create expense with inactive category
        expense_data = {
            "category_id": inactive_category.id,
            "amount": "100.00",
            "description": "Test",
            "expense_date": str(date.today()),
            "payment_method": "cash",
        }
        response = client.post(
            "/api/v1/expenses/",
            json=expense_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category is not active" in response.json()["detail"]

    def test_register_expense_future_date(
        self, client, test_user, test_expense_category
    ):
        """Test that future expense dates are rejected."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to create expense with future date
        future_date = date.today() + timedelta(days=1)
        expense_data = {
            "category_id": test_expense_category.id,
            "amount": "100.00",
            "description": "Future expense",
            "expense_date": str(future_date),
            "payment_method": "cash",
        }
        response = client.post(
            "/api/v1/expenses/",
            json=expense_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot be in the future" in response.json()["detail"]

    def test_get_expenses(self, client, test_user, test_expense):
        """Test getting list of expenses."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Get expenses
        response = client.get(
            "/api/v1/expenses/", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(exp["id"] == test_expense.id for exp in data)

    def test_get_expenses_with_filters(
        self, client, test_user, test_expense_category, db_session
    ):
        """Test getting expenses with various filters."""
        from app.models.expense import Expense

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

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Test date filter
        response = client.get(
            f"/api/v1/expenses/?date_from={today}&date_to={today}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only have today's expenses
        for exp in data:
            assert exp["expense_date"] == str(today)

    def test_get_expense_by_id(self, client, test_user, test_expense):
        """Test getting a specific expense by ID."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Get expense
        response = client.get(
            f"/api/v1/expenses/{test_expense.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_expense.id
        assert data["amount"] == str(test_expense.amount)
        assert data["category"]["id"] == test_expense.category_id

    def test_get_expense_not_found(self, client, test_user):
        """Test getting non-existent expense."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Get non-existent expense
        response = client.get(
            "/api/v1/expenses/99999", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_expense_same_day(self, client, test_user, test_expense):
        """Test updating an expense on the same day."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Update expense
        update_data = {
            "amount": "300.00",
            "description": "Updated description",
            "payment_method": "transfer",
        }
        response = client.put(
            f"/api/v1/expenses/{test_expense.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == "300.00"
        assert data["description"] == "Updated description"
        assert data["payment_method"] == "transfer"

    def test_update_expense_different_user(self, client, test_expense, db_session):
        """Test that users can't update other users' expenses."""
        from app.core.security import get_password_hash
        from app.models.user import User

        # Create different user
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("test_password"),
            full_name="Other User",
            role="admin",
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()

        # Login as other user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": other_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to update expense
        update_data = {"amount": "999.00"}
        response = client.put(
            f"/api/v1/expenses/{test_expense.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "can only be edited" in response.json()["detail"]

    def test_update_expense_old(
        self, client, test_user, test_expense_category, db_session
    ):
        """Test that old expenses cannot be updated."""
        from datetime import datetime

        from app.models.expense import Expense

        # Create an old expense
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

        # Manually set created_at to 2 days ago
        two_days_ago = datetime.now() - timedelta(days=2)
        old_expense.created_at = two_days_ago
        db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to update old expense
        update_data = {"amount": "200.00"}
        response = client.put(
            f"/api/v1/expenses/{old_expense.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_expense(self, client, test_user, test_expense):
        """Test deleting an expense."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Delete expense
        response = client.delete(
            f"/api/v1/expenses/{test_expense.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        check_response = client.get(
            f"/api/v1/expenses/{test_expense.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert check_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_expense_different_user(self, client, test_expense, db_session):
        """Test that users can only delete their own expenses."""
        from app.core.security import get_password_hash
        from app.models.user import User

        # Create different user
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("test_password"),
            full_name="Other User",
            role="admin",
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()

        # Login as other user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": other_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to delete expense
        response = client.delete(
            f"/api/v1/expenses/{test_expense.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_expense_summary(
        self, client, test_user, test_expense_category, db_session
    ):
        """Test getting expense summary for a date."""
        from app.models.expense import Expense, ExpenseCategory

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

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Get summary
        response = client.get(
            f"/api/v1/expenses/summary?target_date={today}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_amount"] == "100.00"
        assert data["expense_count"] == 3
        assert data["by_category"]["Food"] == "80.00"
        assert data["by_category"]["Transport"] == "20.00"
        assert data["by_payment_method"]["cash"] == "70.00"
        assert data["by_payment_method"]["card"] == "30.00"

    def test_upload_receipt(self, client, test_user, test_expense):
        """Test uploading a receipt for an expense."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Upload receipt
        receipt_data = {"file_path": "/uploads/receipts/test-receipt.pdf"}
        response = client.post(
            f"/api/v1/expenses/{test_expense.id}/receipt",
            json=receipt_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["receipt_file_path"] == "/uploads/receipts/test-receipt.pdf"

    def test_upload_receipt_different_user(self, client, test_expense, db_session):
        """Test that users can only upload receipts for their own expenses."""
        from app.core.security import get_password_hash
        from app.models.user import User

        # Create different user
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("test_password"),
            full_name="Other User",
            role="admin",
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()

        # Login as other user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": other_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to upload receipt
        receipt_data = {"file_path": "/uploads/receipts/test.pdf"}
        response = client.post(
            f"/api/v1/expenses/{test_expense.id}/receipt",
            json=receipt_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "only upload receipts for your own expenses" in response.json()["detail"]

    def test_expense_validation(self, client, test_user, test_expense_category):
        """Test various expense validation rules."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Test negative amount
        expense_data = {
            "category_id": test_expense_category.id,
            "amount": "-50.00",
            "description": "Negative amount",
            "expense_date": str(date.today()),
            "payment_method": "cash",
        }
        response = client.post(
            "/api/v1/expenses/",
            json=expense_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test invalid payment method
        expense_data["amount"] = "50.00"
        expense_data["payment_method"] = "invalid_method"
        response = client.post(
            "/api/v1/expenses/",
            json=expense_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
