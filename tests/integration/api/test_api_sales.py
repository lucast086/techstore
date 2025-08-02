"""Tests for sales API endpoints."""

from decimal import Decimal

import pytest
from app.models.customer import Customer
from app.models.product import Category, Product
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """Get authentication headers."""
    # Create test user first
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "admin",
        },
    )

    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123",
        },
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_products(db_session: Session) -> list[Product]:
    """Create test products."""
    # Create category
    category = Category(
        name="Test Category",
        description="Test category description",
    )
    db_session.add(category)
    db_session.commit()

    # Create products
    products = []
    for i in range(2):
        product = Product(
            sku=f"TEST{i:03d}",
            name=f"Test Product {i+1}",
            category_id=category.id,
            purchase_price=Decimal("50.00"),
            first_sale_price=Decimal("100.00"),
            second_sale_price=Decimal("95.00"),
            third_sale_price=Decimal("90.00"),
            current_stock=10,
            minimum_stock=2,
            created_by=1,  # Assuming user ID 1
        )
        db_session.add(product)
        products.append(product)

    db_session.commit()
    return products


@pytest.fixture
def test_customer(db_session: Session) -> Customer:
    """Create test customer."""
    customer = Customer(
        name="Test Customer",
        phone="1234567890",
        email="customer@test.com",
        created_by_id=1,
    )
    db_session.add(customer)
    db_session.commit()
    return customer


class TestSalesAPI:
    """Test sales API endpoints."""

    def test_create_sale(
        self,
        client: TestClient,
        auth_headers: dict,
        test_products: list[Product],
    ):
        """Test creating a sale via API."""
        sale_data = {
            "payment_method": "cash",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 2,
                    "unit_price": 100.00,
                },
                {
                    "product_id": test_products[1].id,
                    "quantity": 1,
                    "unit_price": 100.00,
                },
            ],
        }

        response = client.post(
            "/api/v1/sales/",
            json=sale_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["invoice_number"].startswith("INV-")
        assert len(data["data"]["items"]) == 2
        assert data["data"]["payment_status"] == "paid"
        assert data["data"]["payment_method"] == "cash"

    def test_create_credit_sale(
        self,
        client: TestClient,
        auth_headers: dict,
        test_products: list[Product],
        test_customer: Customer,
    ):
        """Test creating a credit sale."""
        sale_data = {
            "customer_id": test_customer.id,
            "payment_method": "credit",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 1,
                    "unit_price": 100.00,
                },
            ],
        }

        response = client.post(
            "/api/v1/sales/",
            json=sale_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["payment_status"] == "pending"
        assert data["data"]["customer_name"] == test_customer.name

    def test_list_sales(
        self,
        client: TestClient,
        auth_headers: dict,
        test_products: list[Product],
    ):
        """Test listing sales."""
        # Create a sale first
        sale_data = {
            "payment_method": "cash",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 1,
                    "unit_price": 100.00,
                },
            ],
        }

        client.post("/api/v1/sales/", json=sale_data, headers=auth_headers)

        # List sales
        response = client.get("/api/v1/sales/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) >= 1
        assert data["data"]["total"] >= 1

    def test_get_sale_detail(
        self,
        client: TestClient,
        auth_headers: dict,
        test_products: list[Product],
    ):
        """Test getting sale details."""
        # Create a sale
        sale_data = {
            "payment_method": "cash",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 1,
                    "unit_price": 100.00,
                },
            ],
        }

        create_response = client.post(
            "/api/v1/sales/", json=sale_data, headers=auth_headers
        )
        sale_id = create_response.json()["data"]["id"]

        # Get sale details
        response = client.get(f"/api/v1/sales/{sale_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == sale_id
        assert len(data["data"]["items"]) == 1

    def test_search_products(
        self,
        client: TestClient,
        auth_headers: dict,
        test_products: list[Product],
    ):
        """Test product search for POS."""
        response = client.get(
            "/api/v1/sales/products/search?q=Test",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 1
        assert all("Test" in product["name"] for product in data["data"])

    def test_void_sale(
        self,
        client: TestClient,
        auth_headers: dict,
        test_products: list[Product],
    ):
        """Test voiding a sale."""
        # Create a sale
        sale_data = {
            "payment_method": "cash",
            "items": [
                {
                    "product_id": test_products[0].id,
                    "quantity": 1,
                    "unit_price": 100.00,
                },
            ],
        }

        create_response = client.post(
            "/api/v1/sales/", json=sale_data, headers=auth_headers
        )
        sale_id = create_response.json()["data"]["id"]

        # Void the sale
        void_data = {"reason": "Test void reason for testing"}
        response = client.post(
            f"/api/v1/sales/{sale_id}/void",
            json=void_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Sale voided successfully"

    def test_get_sales_summary(
        self,
        client: TestClient,
        auth_headers: dict,
        test_products: list[Product],
    ):
        """Test getting sales summary."""
        # Create multiple sales
        for i in range(2):
            sale_data = {
                "payment_method": "cash" if i == 0 else "credit",
                "items": [
                    {
                        "product_id": test_products[0].id,
                        "quantity": 1,
                        "unit_price": 100.00,
                    },
                ],
            }
            client.post("/api/v1/sales/", json=sale_data, headers=auth_headers)

        # Get summary
        response = client.get("/api/v1/sales/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_count"] >= 2
        assert float(data["data"]["cash_sales"]) > 0
        assert float(data["data"]["credit_sales"]) > 0
