"""Integration tests for product web routes."""

from decimal import Decimal

import pytest
from app.models.product import Category, Product
from app.models.supplier import Supplier
from app.models.user import User
from fastapi.testclient import TestClient


class TestProductWebRoutes:
    """Test product web routes."""

    @pytest.fixture
    def authenticated_client(self, client: TestClient, test_user: User):
        """Create an authenticated test client."""
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
    def test_supplier(self, db_session):
        """Create a test supplier."""
        supplier = Supplier(name="Test Supplier", is_active=True)
        db_session.add(supplier)
        db_session.commit()
        return supplier

    @pytest.fixture
    def test_products(self, db_session, test_user, test_category):
        """Create test products."""
        products = []
        for i in range(5):
            product = Product(
                sku=f"PROD-{i:03d}",
                name=f"Test Product {i}",
                category_id=test_category.id,
                purchase_price=Decimal("100.00"),
                first_sale_price=Decimal("150.00"),
                second_sale_price=Decimal("140.00"),
                third_sale_price=Decimal("130.00"),
                current_stock=10 + i,
                created_by=test_user.id,
                is_active=(i % 2 == 0),
            )
            db_session.add(product)
            products.append(product)
        db_session.commit()
        return products

    def test_products_list_page(self, authenticated_client, test_products):
        """Test accessing products list page."""
        response = authenticated_client.get("/products/")

        assert response.status_code == 200
        assert "Products" in response.text
        assert "Add Product" in response.text

        # Check that products are displayed
        for product in test_products:
            if product.is_active:
                assert product.name in response.text
                assert product.sku in response.text

    def test_products_list_pagination(
        self, authenticated_client, db_session, test_user, test_category
    ):
        """Test products list pagination."""
        # Create 25 products
        for i in range(25):
            product = Product(
                sku=f"PAGE-{i:03d}",
                name=f"Product {i}",
                category_id=test_category.id,
                purchase_price=Decimal("100.00"),
                first_sale_price=Decimal("150.00"),
                second_sale_price=Decimal("140.00"),
                third_sale_price=Decimal("130.00"),
                created_by=test_user.id,
            )
            db_session.add(product)
        db_session.commit()

        # Test first page
        response = authenticated_client.get("/products/")
        assert response.status_code == 200
        assert "PAGE-000" in response.text
        assert "PAGE-024" not in response.text  # Should be on page 2

        # Test second page
        response = authenticated_client.get("/products/?page=2")
        assert response.status_code == 200
        assert "PAGE-024" in response.text
        assert "PAGE-000" not in response.text  # Should be on page 1

    def test_products_list_search(self, authenticated_client, test_products):
        """Test products list search functionality."""
        # Search by name
        response = authenticated_client.get("/products/?search=Product%202")
        assert response.status_code == 200
        assert "Test Product 2" in response.text
        assert "Test Product 1" not in response.text

        # Search by SKU
        response = authenticated_client.get("/products/?search=PROD-001")
        assert response.status_code == 200
        assert "PROD-001" in response.text
        assert "PROD-002" not in response.text

    def test_products_list_category_filter(
        self, authenticated_client, db_session, test_user, test_category
    ):
        """Test products list category filtering."""
        # Create another category
        category2 = Category(name="Accessories", is_active=True)
        db_session.add(category2)
        db_session.commit()

        # Create products in different categories
        prod1 = Product(
            sku="CAT-TEST-1",
            name="Electronics Product",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
            created_by=test_user.id,
        )
        prod2 = Product(
            sku="CAT-TEST-2",
            name="Accessories Product",
            category_id=category2.id,
            purchase_price=Decimal("50.00"),
            first_sale_price=Decimal("75.00"),
            second_sale_price=Decimal("70.00"),
            third_sale_price=Decimal("65.00"),
            created_by=test_user.id,
        )
        db_session.add_all([prod1, prod2])
        db_session.commit()

        # Filter by category
        response = authenticated_client.get(
            f"/products/?category_id={test_category.id}"
        )
        assert response.status_code == 200
        assert "Electronics Product" in response.text
        assert "Accessories Product" not in response.text

    def test_create_product_form(self, authenticated_client, test_category):
        """Test accessing create product form."""
        response = authenticated_client.get("/products/create")

        assert response.status_code == 200
        assert "Create New Product" in response.text
        assert "<form" in response.text
        assert 'name="sku"' in response.text
        assert 'name="name"' in response.text
        assert test_category.name in response.text

    def test_create_product_success(self, authenticated_client, test_category):
        """Test successfully creating a product."""
        form_data = {
            "sku": "NEW-PRODUCT-001",
            "name": "New Test Product",
            "description": "This is a test product",
            "category_id": str(test_category.id),
            "brand": "Test Brand",
            "model": "Model X",
            "barcode": "1234567890123",
            "purchase_price": "99.99",
            "first_sale_price": "149.99",
            "second_sale_price": "139.99",
            "third_sale_price": "129.99",
            "tax_rate": "16.00",
            "current_stock": "10",
            "minimum_stock": "5",
            "maximum_stock": "50",
            "location": "A1-B2",
            "is_active": "true",
        }

        response = authenticated_client.post(
            "/products/create", data=form_data, follow_redirects=False
        )

        assert response.status_code == 201
        assert "Producto creado exitosamente" in response.text
        assert "NEW-PRODUCT-001" in response.text

        # Check HX-Redirect header
        assert "HX-Redirect" in response.headers

        # Verify product was created in database
        from app.database import SessionLocal

        db = SessionLocal()
        product = db.query(Product).filter_by(sku="NEW-PRODUCT-001").first()
        assert product is not None
        assert product.name == "New Test Product"
        assert product.purchase_price == Decimal("99.99")
        db.close()

    def test_create_product_duplicate_sku(
        self, authenticated_client, test_category, test_products
    ):
        """Test creating a product with duplicate SKU."""
        form_data = {
            "sku": test_products[0].sku,  # Use existing SKU
            "name": "Duplicate SKU Product",
            "category_id": str(test_category.id),
            "purchase_price": "100.00",
            "first_sale_price": "150.00",
            "second_sale_price": "140.00",
            "third_sale_price": "130.00",
            "current_stock": "0",
            "minimum_stock": "0",
        }

        response = authenticated_client.post("/products/create", data=form_data)

        assert response.status_code == 400
        assert "already exists" in response.text

    def test_create_product_validation_error(self, authenticated_client, test_category):
        """Test creating a product with validation errors."""
        form_data = {
            "sku": "INVALID SKU!",  # Invalid characters
            "name": "",  # Empty name
            "category_id": str(test_category.id),
            "purchase_price": "-10.00",  # Negative price
            "first_sale_price": "150.00",
            "second_sale_price": "140.00",
            "third_sale_price": "130.00",
        }

        response = authenticated_client.post("/products/create", data=form_data)

        assert response.status_code == 400
        # Should show form with errors
        assert "<form" in response.text

    def test_product_detail_page(self, authenticated_client, test_products):
        """Test accessing product detail page."""
        product = test_products[0]
        response = authenticated_client.get(f"/products/{product.id}")

        assert response.status_code == 200
        assert product.name in response.text
        assert product.sku in response.text
        assert f"${product.first_sale_price}" in response.text
        assert "Edit Product" in response.text
        assert "Print Label" in response.text

    def test_product_detail_not_found(self, authenticated_client):
        """Test accessing non-existent product detail page."""
        response = authenticated_client.get("/products/9999")

        assert response.status_code == 404
        assert "Producto no encontrado" in response.text

    def test_product_search_endpoint(self, authenticated_client, test_products):
        """Test product search endpoint."""
        # Search for existing product
        response = authenticated_client.get("/products/search?q=Product%201")

        assert response.status_code == 200
        assert "Test Product 1" in response.text
        assert "PROD-001" in response.text

        # Search with no results
        response = authenticated_client.get("/products/search?q=NonExistent")

        assert response.status_code == 200
        assert "No products found" in response.text

    def test_unauthenticated_access(self, client):
        """Test that unauthenticated users cannot access product pages."""
        # Try to access products list
        response = client.get("/products/", follow_redirects=False)
        assert response.status_code == 401  # Unauthorized

        # Try to access create form
        response = client.get("/products/create", follow_redirects=False)
        assert response.status_code == 401

        # Try to create product
        response = client.post("/products/create", data={}, follow_redirects=False)
        assert response.status_code == 401
