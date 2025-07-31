"""Simple integration tests for product web routes without complex SQL."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from app.models.product import Category
from app.models.user import User
from app.schemas.filters import ProductListItem, StockStatus
from app.services.product_service import ProductService
from fastapi.testclient import TestClient


class TestProductWebRoutesSimple:
    """Test product web routes with mocked service."""

    @pytest.fixture
    def authenticated_client(self, client: TestClient, test_user: User, db_session):
        """Create an authenticated test client."""
        # Ensure test_user is in the session
        db_session.add(test_user)
        db_session.commit()

        # Login to get session
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "test_password"},
        )
        assert response.status_code == 200

        # Get the session cookie
        cookies = response.cookies
        client.cookies = cookies
        return client

    @pytest.fixture
    def test_category(self, db_session):
        """Create a test category."""
        category = Category(name="Electronics", is_active=True)
        db_session.add(category)
        db_session.commit()
        return category

    @pytest.fixture
    def mock_products(self, test_category):
        """Create mock product list items."""
        products = []
        for i in range(3):
            product = ProductListItem(
                id=i + 1,
                sku=f"PROD-{i:03d}",
                name=f"Test Product {i}",
                barcode=None,
                brand="Test Brand",
                model=f"Model {i}",
                category_id=test_category.id,
                category_name=test_category.name,
                purchase_price=Decimal("100.00"),
                first_sale_price=Decimal("150.00"),
                second_sale_price=Decimal("140.00"),
                third_sale_price=Decimal("130.00"),
                current_stock=10 + i,
                minimum_stock=5,
                stock_status=StockStatus.IN_STOCK,
                profit_margin=Decimal("50.00"),
                margin_percentage=50.0,
                primary_image=None,
                is_active=True,
                updated_at=datetime.utcnow(),
            )
            products.append(product)
        return products

    def test_products_list_page_with_mock(
        self, authenticated_client, mock_products, test_category, monkeypatch
    ):
        """Test accessing products list page with mocked service."""
        # Mock the ProductService methods
        mock_get_product_list = AsyncMock(
            return_value=(mock_products, len(mock_products))
        )
        mock_get_filter_options = AsyncMock(
            return_value={
                "categories": [test_category],
                "brands": ["Test Brand"],
                "stock_statuses": ["in_stock", "low_stock", "out_of_stock"],
            }
        )

        # Patch the service methods
        monkeypatch.setattr(ProductService, "get_product_list", mock_get_product_list)
        monkeypatch.setattr(
            ProductService, "get_filter_options", mock_get_filter_options
        )

        # Make the request
        response = authenticated_client.get("/products/")

        # Verify response
        assert response.status_code == 200
        assert "Products" in response.text
        assert "Add Product" in response.text

        # Check that products are displayed
        for product in mock_products:
            assert product.name in response.text
            assert product.sku in response.text

        # Verify the service was called
        mock_get_product_list.assert_called_once()

    def test_products_search_with_mock(
        self, authenticated_client, mock_products, test_category, monkeypatch
    ):
        """Test product search functionality with mocked service."""
        # Filter to just one product
        filtered_products = [p for p in mock_products if "1" in p.name]

        # Mock the service methods
        mock_get_product_list = AsyncMock(
            return_value=(filtered_products, len(filtered_products))
        )
        mock_get_filter_options = AsyncMock(
            return_value={
                "categories": [test_category],
                "brands": ["Test Brand"],
                "stock_statuses": ["in_stock", "low_stock", "out_of_stock"],
            }
        )

        # Patch the service methods
        monkeypatch.setattr(ProductService, "get_product_list", mock_get_product_list)
        monkeypatch.setattr(
            ProductService, "get_filter_options", mock_get_filter_options
        )

        # Make the request with search
        response = authenticated_client.get("/products/?search=Product%201")

        # Verify response
        assert response.status_code == 200
        assert "Test Product 1" in response.text
        assert "Test Product 0" not in response.text
        assert "Test Product 2" not in response.text

    def test_products_category_filter_with_mock(
        self, authenticated_client, mock_products, test_category, monkeypatch
    ):
        """Test product category filtering with mocked service."""
        # Mock the service methods
        mock_get_product_list = AsyncMock(
            return_value=(mock_products, len(mock_products))
        )
        mock_get_filter_options = AsyncMock(
            return_value={
                "categories": [test_category],
                "brands": ["Test Brand"],
                "stock_statuses": ["in_stock", "low_stock", "out_of_stock"],
            }
        )

        # Patch the service methods
        monkeypatch.setattr(ProductService, "get_product_list", mock_get_product_list)
        monkeypatch.setattr(
            ProductService, "get_filter_options", mock_get_filter_options
        )

        # Make the request with category filter
        response = authenticated_client.get(
            f"/products/?category_id={test_category.id}"
        )

        # Verify response
        assert response.status_code == 200
        # All mock products should be shown as they're all in the same category
        for product in mock_products:
            assert product.name in response.text

    def test_create_product_form_access(self, authenticated_client, test_category):
        """Test accessing create product form."""
        response = authenticated_client.get("/products/create")

        assert response.status_code == 200
        assert "Create New Product" in response.text
        assert "<form" in response.text
        assert 'name="sku"' in response.text
        assert 'name="name"' in response.text
        assert test_category.name in response.text

    def test_unauthenticated_access(self, client):
        """Test that unauthenticated users cannot access product pages."""
        # Try to access products list
        response = client.get("/products/", follow_redirects=False)
        assert response.status_code == 401  # Unauthorized

        # Try to access create form
        response = client.get("/products/create", follow_redirects=False)
        assert response.status_code == 401
