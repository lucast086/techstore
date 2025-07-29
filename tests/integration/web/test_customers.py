"""Integration tests for Customer web routes."""

from app.models.customer import Customer
from fastapi import status


class TestCustomerWeb:
    """Test Customer web interface routes."""

    def test_customer_list_page(self, client, test_user):
        """Test customer list page loads."""
        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        client.post("/login", data=login_data)

        response = client.get("/customers")
        assert response.status_code == status.HTTP_200_OK
        assert b"Customers" in response.content
        assert b"Register New Customer" in response.content

    def test_customer_list_with_search(self, client, test_user, db_session):
        """Test customer list with search query."""
        # Create customers
        customers = [
            Customer(name="John Doe", phone="1111111111"),
            Customer(name="Jane Smith", phone="2222222222"),
        ]
        db_session.add_all(customers)
        db_session.commit()

        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        client.post("/login", data=login_data)

        # Search
        response = client.get("/customers?search=John")
        assert response.status_code == status.HTTP_200_OK
        assert b"John Doe" in response.content
        assert b"Jane Smith" not in response.content

    def test_new_customer_form(self, client, test_user):
        """Test new customer form page."""
        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        client.post("/login", data=login_data)

        response = client.get("/customers/new")
        assert response.status_code == status.HTTP_200_OK
        assert b"Register New Customer" in response.content
        assert b'name="name"' in response.content
        assert b'name="phone"' in response.content
        assert b"required" in response.content

    def test_create_customer_success(self, client, test_user, db_session):
        """Test successful customer creation via web form."""
        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        client.post("/login", data=login_data)

        # Submit form
        form_data = {
            "name": "John Doe",
            "phone": "1234567890",
            "email": "john@example.com",
            "address": "123 Main St",
            "notes": "VIP customer",
        }

        response = client.post("/customers/new", data=form_data, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Check customer was created
        customer = db_session.query(Customer).filter_by(phone="1234567890").first()
        assert customer is not None
        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"
        assert customer.created_by_id == test_user.id

        # Check redirect
        assert response.headers["location"] == f"/customers/{customer.id}"

    def test_create_customer_duplicate_phone_error(self, client, test_user, db_session):
        """Test creating customer with duplicate phone shows error."""
        # Create existing customer
        existing = Customer(name="Existing", phone="1234567890")
        db_session.add(existing)
        db_session.commit()

        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        client.post("/login", data=login_data)

        # Try to create duplicate
        form_data = {"name": "New Customer", "phone": "1234567890"}

        response = client.post("/customers/new", data=form_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b"already exists" in response.content
        assert b'value="New Customer"' in response.content  # Form retains data

    def test_create_customer_minimal_fields(self, client, test_user, db_session):
        """Test creating customer with only required fields."""
        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        client.post("/login", data=login_data)

        # Submit only required fields
        form_data = {"name": "Minimal Customer", "phone": "9876543210"}

        response = client.post("/customers/new", data=form_data, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Check customer was created
        customer = db_session.query(Customer).filter_by(phone="9876543210").first()
        assert customer is not None
        assert customer.name == "Minimal Customer"
        assert customer.email is None
        assert customer.address is None
        assert customer.notes is None

    def test_customer_form_requires_auth(self, client):
        """Test that customer forms require authentication."""
        # Try to access form without login
        response = client.get("/customers/new")
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/login?next=%2Fcustomers%2Fnew"

        # Try to submit form without login
        response = client.post("/customers/new", data={"name": "Test", "phone": "123"})
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_customer_list_pagination(self, client, test_user, db_session):
        """Test customer list pagination."""
        # Create many customers
        for i in range(25):
            customer = Customer(name=f"Customer {i}", phone=f"100000000{i:02d}")
            db_session.add(customer)
        db_session.commit()

        # Login
        login_data = {"email": test_user.email, "password": "test_password"}
        client.post("/login", data=login_data)

        # First page
        response = client.get("/customers")
        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode()
        assert "Customer 0" in content
        assert "Customer 19" in content
        assert "Customer 20" not in content

        # Second page
        response = client.get("/customers?page=2")
        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode()
        assert "Customer 20" in content
        assert "Customer 24" in content
