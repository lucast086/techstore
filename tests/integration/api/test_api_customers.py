"""Integration tests for Customer API endpoints."""

from app.models.customer import Customer
from fastapi import status


class TestCustomerAPI:
    """Test Customer API endpoints."""

    def test_create_customer_success(self, client, test_user, db_session):
        """Test successful customer creation via API."""
        # Login first
        login_data = {"email": test_user.email, "password": "test_password"}
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]

        # Create customer with unique phone
        import time

        unique_phone = f"555{int(time.time() * 1000) % 10000000:07d}"
        customer_data = {
            "name": "John Doe",
            "phone": unique_phone,
            "email": "john@example.com",
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/customers", json=customer_data, headers=headers)
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["name"] == customer_data["name"]
        assert data["phone"] == customer_data["phone"]
        assert data["email"] == customer_data["email"]
        assert data["balance"] == 0.0
        assert data["transaction_count"] == 0
        assert data["created_by_name"] == test_user.full_name

    def test_create_customer_duplicate_phone(self, client, test_user, db_session):
        """Test creating customer with duplicate phone number."""
        # Create first customer
        customer = Customer(name="Existing", phone="1234567890")
        db_session.add(customer)
        db_session.commit()

        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to create duplicate
        customer_data = {"name": "New Customer", "phone": "1234567890"}

        response = client.post("/api/v1/customers", json=customer_data, headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_check_phone_availability(self, client, db_session):
        """Test phone availability check endpoint."""
        # Create existing customer
        customer = Customer(name="Existing", phone="1234567890")
        db_session.add(customer)
        db_session.commit()

        # Check existing phone
        response = client.get("/api/v1/customers/check-phone?phone=1234567890")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["available"] is False
        assert "Existing" in data["message"]
        assert data["customer"]["id"] == customer.id

        # Check available phone
        response = client.get("/api/v1/customers/check-phone?phone=9876543210")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["available"] is True

    def test_check_phone_with_exclusion(self, client, db_session):
        """Test phone check excluding current customer."""
        customer = Customer(name="Test", phone="1234567890")
        db_session.add(customer)
        db_session.commit()

        # Check same phone excluding this customer
        response = client.get(
            f"/api/v1/customers/check-phone?phone=1234567890&exclude_id={customer.id}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["available"] is True

    def test_search_customers(self, client, test_user, db_session):
        """Test customer search endpoint."""
        # Create test customers
        customers = [
            Customer(name="John Doe", phone="1111111111"),
            Customer(name="Jane Smith", phone="2222222222"),
            Customer(name="John Smith", phone="3333333333"),
        ]
        db_session.add_all(customers)
        db_session.commit()

        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Search by name
        response = client.get("/api/v1/customers/search?q=John", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 2
        assert all("John" in r["name"] for r in data["results"])

        # Search by phone
        response = client.get("/api/v1/customers/search?q=2222", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Jane Smith"

    def test_create_customer_requires_auth(self, client):
        """Test that creating customer requires authentication."""
        customer_data = {"name": "Test", "phone": "1234567890"}

        response = client.post("/api/v1/customers", json=customer_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_customer_validation(self, client, test_user, db_session):
        """Test customer creation validation."""
        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Missing required fields
        response = client.post("/api/v1/customers", json={}, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid email
        response = client.post(
            "/api/v1/customers",
            json={"name": "Test", "phone": "1234567890", "email": "invalid-email"},
            headers=headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Phone too short
        response = client.post(
            "/api/v1/customers", json={"name": "Test", "phone": "123"}, headers=headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
