"""Tests for expense category API endpoints."""

from fastapi import status
from fastapi.testclient import TestClient


class TestExpenseCategoryAPI:
    """Test cases for expense category API endpoints."""

    def test_get_categories_unauthenticated(self, client: TestClient):
        """Test that unauthenticated requests are rejected."""
        response = client.get("/api/v1/categories")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_categories_empty(self, client: TestClient, test_user):
        """Test getting categories when none exist."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]

        # Get categories
        response = client.get(
            "/api/v1/categories", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []

    def test_create_category(self, client, test_user):
        """Test creating a new expense category."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Create category
        category_data = {
            "name": "Office Supplies",
            "description": "Office and stationery supplies",
        }
        response = client.post(
            "/api/v1/categories",
            json=category_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["success"] is True
        data = result["data"]
        assert data["name"] == "Office Supplies"
        assert data["description"] == "Office and stationery supplies"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_category_duplicate_name(
        self, client, test_user, test_expense_category
    ):
        """Test that duplicate category names are rejected."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to create duplicate
        category_data = {
            "name": test_expense_category.name,
            "description": "Duplicate category",
        }
        response = client.post(
            "/api/v1/categories",
            json=category_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_get_all_categories(self, client, test_user, db_session):
        """Test getting all expense categories."""
        from app.models.expense import ExpenseCategory

        # Create test categories
        categories = [
            ExpenseCategory(name="Category 1", description="First"),
            ExpenseCategory(name="Category 2", description="Second"),
            ExpenseCategory(name="Category 3", description="Third", is_active=False),
        ]
        db_session.add_all(categories)
        db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Get all categories
        response = client.get(
            "/api/v1/categories", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        result = data["data"]
        assert len(result) == 3
        assert all("name" in cat for cat in result)
        assert all("is_active" in cat for cat in result)

    def test_get_active_categories(self, client, test_user, db_session):
        """Test getting only active categories."""
        from app.models.expense import ExpenseCategory

        # Create test categories
        active1 = ExpenseCategory(name="Active 1", is_active=True)
        active2 = ExpenseCategory(name="Active 2", is_active=True)
        inactive = ExpenseCategory(name="Inactive", is_active=False)
        db_session.add_all([active1, active2, inactive])
        db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Get active categories only
        response = client.get(
            "/api/v1/categories/active", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        result = data["data"]
        assert len(result) == 2
        assert all(cat["is_active"] for cat in result)
        names = [cat["name"] for cat in result]
        assert "Active 1" in names
        assert "Active 2" in names
        assert "Inactive" not in names

    def test_get_category_by_id(self, client, test_user, test_expense_category):
        """Test getting a specific category by ID."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Get category
        response = client.get(
            f"/api/v1/categories/{test_expense_category.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["success"] is True
        data = result["data"]
        assert data["id"] == test_expense_category.id
        assert data["name"] == test_expense_category.name

    def test_get_category_not_found(self, client, test_user):
        """Test getting non-existent category."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Get non-existent category
        response = client.get(
            "/api/v1/categories/99999", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category(self, client, test_user, test_expense_category):
        """Test updating an expense category."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Update category
        update_data = {
            "name": "Updated Category Name",
            "description": "Updated description",
            "is_active": False,
        }
        response = client.put(
            f"/api/v1/categories/{test_expense_category.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["success"] is True
        data = result["data"]
        assert data["name"] == "Updated Category Name"
        assert data["description"] == "Updated description"
        assert data["is_active"] is False

    def test_partial_update_category(self, client, test_user, test_expense_category):
        """Test partial update of category."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        original_name = test_expense_category.name

        # Update only description
        update_data = {"description": "Only update description"}
        response = client.patch(
            f"/api/v1/categories/{test_expense_category.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["success"] is True
        data = result["data"]
        assert data["name"] == original_name  # Name unchanged
        assert data["description"] == "Only update description"

    def test_delete_category_with_expenses(
        self, client, test_user, test_expense_category, test_expense
    ):
        """Test that categories with expenses cannot be deleted."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to delete category with expenses
        response = client.delete(
            f"/api/v1/categories/{test_expense_category.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "has associated expenses" in response.json()["detail"]

    def test_delete_empty_category(self, client, test_user, db_session):
        """Test deleting an empty category."""
        from app.models.expense import ExpenseCategory

        # Create empty category
        empty_category = ExpenseCategory(name="Empty Category")
        db_session.add(empty_category)
        db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Delete category
        response = client.delete(
            f"/api/v1/categories/{empty_category.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        check_response = client.get(
            f"/api/v1/categories/{empty_category.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert check_response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_default_categories(self, client, test_user):
        """Test creating default expense categories."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Create defaults
        response = client.post(
            "/api/v1/categories/create-defaults",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "created" in data
        assert data["created"] == 6  # Should create 6 default categories

        # Verify categories were created
        get_response = client.get(
            "/api/v1/categories", headers={"Authorization": f"Bearer {token}"}
        )
        categories = get_response.json()
        category_names = [cat["name"] for cat in categories]

        # Check default categories exist
        expected_defaults = [
            "General",
            "Suppliers",
            "Utilities",
            "Salaries",
            "Maintenance",
            "Marketing",
        ]
        for default in expected_defaults:
            assert default in category_names

    def test_create_defaults_idempotent(self, client, test_user):
        """Test that creating defaults is idempotent."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Create defaults first time
        response1 = client.post(
            "/api/v1/categories/create-defaults",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response1.status_code == status.HTTP_201_CREATED
        assert response1.json()["created"] == 6

        # Create defaults second time
        response2 = client.post(
            "/api/v1/categories/create-defaults",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.json()["created"] == 0  # No new categories created

    def test_role_based_access(self, client, db_session):
        """Test that only admin and manager roles can manage categories."""
        from app.core.security import get_password_hash
        from app.models.user import User

        # Create technician user
        technician = User(
            email="technician@example.com",
            password_hash=get_password_hash("test_password"),
            full_name="Test Technician",
            role="technician",
            is_active=True,
        )
        db_session.add(technician)
        db_session.commit()

        # Login as technician
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": technician.email, "password": "test_password"},
        )
        token = login_response.json()["access_token"]

        # Try to create category
        category_data = {"name": "Test Category", "description": "Test"}
        response = client.post(
            "/api/v1/categories",
            json=category_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should be forbidden for technician role
        assert response.status_code == status.HTTP_403_FORBIDDEN
