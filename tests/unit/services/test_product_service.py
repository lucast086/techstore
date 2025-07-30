"""Unit tests for Product Service."""

from decimal import Decimal

import pytest
from app.models.product import Category
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.product import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
)
from app.services.product_service import CategoryService, ProductService


@pytest.mark.asyncio
class TestCategoryService:
    """Test CategoryService."""

    @pytest.fixture
    def category_service(self, db_session):
        """Create a CategoryService instance."""
        return CategoryService(db_session)

    async def test_create_category(self, category_service, db_session):
        """Test creating a category."""
        category_data = CategoryCreate(
            name="Electronics", description="Electronic devices", is_active=True
        )

        category = await category_service.create_category(category_data)

        assert category.id is not None
        assert category.name == "Electronics"
        assert category.description == "Electronic devices"
        assert category.is_active is True

    async def test_create_category_duplicate_name(self, category_service, db_session):
        """Test creating a category with duplicate name raises error."""
        # Create first category
        category_data = CategoryCreate(name="Electronics")
        await category_service.create_category(category_data)

        # Try to create another with same name
        with pytest.raises(ValueError, match="already exists"):
            await category_service.create_category(category_data)

    async def test_create_category_with_parent(self, category_service, db_session):
        """Test creating a category with parent."""
        # Create parent category
        parent_data = CategoryCreate(name="Electronics")
        parent = await category_service.create_category(parent_data)

        # Create child category
        child_data = CategoryCreate(name="Smartphones", parent_id=parent.id)
        child = await category_service.create_category(child_data)

        assert child.parent_id == parent.id

    async def test_create_category_invalid_parent(self, category_service, db_session):
        """Test creating a category with invalid parent raises error."""
        category_data = CategoryCreate(name="Test", parent_id=9999)

        with pytest.raises(ValueError, match="Parent category"):
            await category_service.create_category(category_data)

    async def test_get_categories(self, category_service, db_session):
        """Test getting all categories."""
        # Create test categories
        await category_service.create_category(CategoryCreate(name="Category1"))
        await category_service.create_category(
            CategoryCreate(name="Category2", is_active=False)
        )

        # Get all categories
        all_categories = await category_service.get_categories()
        assert len(all_categories) == 2

        # Get only active categories
        active_categories = await category_service.get_categories(is_active=True)
        assert len(active_categories) == 1
        assert active_categories[0].name == "Category1"

    async def test_get_category(self, category_service, db_session):
        """Test getting a single category."""
        # Create category
        created = await category_service.create_category(CategoryCreate(name="Test"))

        # Get category
        category = await category_service.get_category(created.id)
        assert category is not None
        assert category.id == created.id
        assert category.name == "Test"

        # Get non-existent category
        category = await category_service.get_category(9999)
        assert category is None

    async def test_update_category(self, category_service, db_session):
        """Test updating a category."""
        # Create category
        created = await category_service.create_category(
            CategoryCreate(name="Original")
        )

        # Update category
        update_data = CategoryUpdate(name="Updated", description="New description")
        updated = await category_service.update_category(created.id, update_data)

        assert updated is not None
        assert updated.name == "Updated"
        assert updated.description == "New description"

    async def test_update_category_duplicate_name(self, category_service, db_session):
        """Test updating category to duplicate name raises error."""
        # Create two categories
        await category_service.create_category(CategoryCreate(name="Category1"))
        cat2 = await category_service.create_category(CategoryCreate(name="Category2"))

        # Try to update cat2 to have cat1's name
        update_data = CategoryUpdate(name="Category1")

        with pytest.raises(ValueError, match="already exists"):
            await category_service.update_category(cat2.id, update_data)

    async def test_update_nonexistent_category(self, category_service, db_session):
        """Test updating non-existent category returns None."""
        update_data = CategoryUpdate(name="Test")
        result = await category_service.update_category(9999, update_data)
        assert result is None


@pytest.mark.asyncio
class TestProductService:
    """Test ProductService."""

    @pytest.fixture
    def product_service(self, db_session):
        """Create a ProductService instance."""
        return ProductService(db_session)

    @pytest.fixture
    def test_user(self, db_session):
        """Create a test user."""
        user = User(
            email="test@example.com",
            password_hash="hashed",
            full_name="Test User",
            role="admin",
        )
        db_session.add(user)
        db_session.commit()
        return user

    @pytest.fixture
    def test_category(self, db_session):
        """Create a test category."""
        category = Category(name="Test Category", is_active=True)
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

    async def test_create_product(
        self, product_service, db_session, test_user, test_category
    ):
        """Test creating a product."""
        product_data = ProductCreate(
            sku="TEST-001",
            name="Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
            current_stock=10,
        )

        product = await product_service.create_product(product_data, test_user.id)

        assert product.id is not None
        assert product.sku == "TEST-001"
        assert product.name == "Test Product"
        assert product.category_id == test_category.id
        assert product.created_by == test_user.id
        assert product.current_stock == 10

    async def test_create_product_duplicate_sku(
        self, product_service, db_session, test_user, test_category
    ):
        """Test creating a product with duplicate SKU raises error."""
        product_data = ProductCreate(
            sku="DUP-SKU",
            name="Product 1",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
        )

        # Create first product
        await product_service.create_product(product_data, test_user.id)

        # Try to create another with same SKU
        product_data.name = "Product 2"
        with pytest.raises(ValueError, match="already exists"):
            await product_service.create_product(product_data, test_user.id)

    async def test_create_product_invalid_category(
        self, product_service, db_session, test_user
    ):
        """Test creating a product with invalid category raises error."""
        product_data = ProductCreate(
            sku="TEST-001",
            name="Test Product",
            category_id=9999,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
        )

        with pytest.raises(ValueError, match="Invalid or inactive category"):
            await product_service.create_product(product_data, test_user.id)

    async def test_create_product_with_images(
        self, product_service, db_session, test_user, test_category
    ):
        """Test creating a product with images."""
        product_data = ProductCreate(
            sku="IMG-001",
            name="Product with Images",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
            images=["image1.jpg", "image2.jpg", "image3.jpg"],
        )

        product = await product_service.create_product(product_data, test_user.id)

        assert len(product.images) == 3
        assert product.images[0].image_url == "image1.jpg"
        assert product.images[0].is_primary is True
        assert product.images[1].is_primary is False

    async def test_create_product_with_suppliers(
        self, product_service, db_session, test_user, test_category, test_supplier
    ):
        """Test creating a product with supplier links."""
        product_data = ProductCreate(
            sku="SUP-001",
            name="Product with Suppliers",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
            supplier_ids=[test_supplier.id],
        )

        product = await product_service.create_product(product_data, test_user.id)

        assert len(product.suppliers) == 1
        assert product.suppliers[0].supplier_id == test_supplier.id
        assert product.suppliers[0].is_preferred is True

    async def test_get_products(
        self, product_service, db_session, test_user, test_category
    ):
        """Test getting products with filters."""
        # Create test products
        products_data = [
            ProductCreate(
                sku=f"PROD-{i}",
                name=f"Product {i}",
                category_id=test_category.id,
                purchase_price=Decimal("100.00"),
                first_sale_price=Decimal("150.00"),
                second_sale_price=Decimal("140.00"),
                third_sale_price=Decimal("130.00"),
                is_active=(i % 2 == 0),
            )
            for i in range(5)
        ]

        for data in products_data:
            await product_service.create_product(data, test_user.id)

        # Get all products
        all_products = await product_service.get_products()
        assert len(all_products) == 5

        # Get active products only
        active_products = await product_service.get_products(is_active=True)
        assert len(active_products) == 3  # 0, 2, 4 are active

        # Test pagination
        page1 = await product_service.get_products(skip=0, limit=2)
        assert len(page1) == 2

    async def test_get_products_search(
        self, product_service, db_session, test_user, test_category
    ):
        """Test searching products."""
        # Create test products
        products = [
            ("ABC-123", "Apple iPhone", "194253024019"),
            ("XYZ-789", "Samsung Galaxy", "887276409689"),
            ("DEF-456", "Apple iPad", None),
        ]

        for sku, name, barcode in products:
            data = ProductCreate(
                sku=sku,
                name=name,
                barcode=barcode,
                category_id=test_category.id,
                purchase_price=Decimal("100.00"),
                first_sale_price=Decimal("150.00"),
                second_sale_price=Decimal("140.00"),
                third_sale_price=Decimal("130.00"),
            )
            await product_service.create_product(data, test_user.id)

        # Search by name
        results = await product_service.get_products(search="Apple")
        assert len(results) == 2

        # Search by SKU
        results = await product_service.get_products(search="ABC")
        assert len(results) == 1
        assert results[0].sku == "ABC-123"

        # Search by barcode
        results = await product_service.get_products(search="194253")
        assert len(results) == 1
        assert results[0].name == "Apple iPhone"

    async def test_get_product_by_id(
        self, product_service, db_session, test_user, test_category
    ):
        """Test getting a product by ID."""
        # Create product
        data = ProductCreate(
            sku="GET-001",
            name="Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
        )
        created = await product_service.create_product(data, test_user.id)

        # Get product
        product = await product_service.get_product(created.id)
        assert product is not None
        assert product.id == created.id
        assert product.sku == "GET-001"

        # Get non-existent product
        product = await product_service.get_product(9999)
        assert product is None

    async def test_get_product_by_sku(
        self, product_service, db_session, test_user, test_category
    ):
        """Test getting a product by SKU."""
        # Create product
        data = ProductCreate(
            sku="SKU-SEARCH-001",
            name="Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
        )
        await product_service.create_product(data, test_user.id)

        # Get product by SKU
        product = await product_service.get_product_by_sku("SKU-SEARCH-001")
        assert product is not None
        assert product.sku == "SKU-SEARCH-001"

        # Get non-existent product
        product = await product_service.get_product_by_sku("NONEXISTENT")
        assert product is None

    async def test_update_product(
        self, product_service, db_session, test_user, test_category
    ):
        """Test updating a product."""
        # Create product
        data = ProductCreate(
            sku="UPDATE-001",
            name="Original Name",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
        )
        created = await product_service.create_product(data, test_user.id)

        # Update product
        update_data = ProductUpdate(
            name="Updated Name", purchase_price=Decimal("110.00"), current_stock=20
        )
        updated = await product_service.update_product(created.id, update_data)

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.purchase_price == Decimal("110.00")
        assert updated.current_stock == 20
        assert updated.sku == "UPDATE-001"  # SKU unchanged

    async def test_update_product_duplicate_sku(
        self, product_service, db_session, test_user, test_category
    ):
        """Test updating product to duplicate SKU raises error."""
        # Create two products
        for i in range(2):
            data = ProductCreate(
                sku=f"SKU-{i}",
                name=f"Product {i}",
                category_id=test_category.id,
                purchase_price=Decimal("100.00"),
                first_sale_price=Decimal("150.00"),
                second_sale_price=Decimal("140.00"),
                third_sale_price=Decimal("130.00"),
            )
            if i == 1:
                product2 = await product_service.create_product(data, test_user.id)
            else:
                await product_service.create_product(data, test_user.id)

        # Try to update product2 to have product1's SKU
        update_data = ProductUpdate(sku="SKU-0")

        with pytest.raises(ValueError, match="already exists"):
            await product_service.update_product(product2.id, update_data)

    async def test_update_stock(
        self, product_service, db_session, test_user, test_category
    ):
        """Test updating product stock."""
        # Create product with initial stock
        data = ProductCreate(
            sku="STOCK-001",
            name="Stock Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("100.00"),
            first_sale_price=Decimal("150.00"),
            second_sale_price=Decimal("140.00"),
            third_sale_price=Decimal("130.00"),
            current_stock=10,
        )
        product = await product_service.create_product(data, test_user.id)

        # Add stock (relative)
        updated = await product_service.update_stock(product.id, 5, is_absolute=False)
        assert updated.current_stock == 15

        # Remove stock (relative)
        updated = await product_service.update_stock(product.id, -3, is_absolute=False)
        assert updated.current_stock == 12

        # Set stock (absolute)
        updated = await product_service.update_stock(product.id, 20, is_absolute=True)
        assert updated.current_stock == 20

        # Try to set negative stock (absolute)
        with pytest.raises(ValueError, match="cannot be negative"):
            await product_service.update_stock(product.id, -5, is_absolute=True)

        # Try to remove more stock than available
        with pytest.raises(ValueError, match="Insufficient stock"):
            await product_service.update_stock(product.id, -25, is_absolute=False)

    async def test_count_products(
        self, product_service, db_session, test_user, test_category
    ):
        """Test counting products with filters."""
        # Create another category
        category2 = Category(name="Category 2", is_active=True)
        db_session.add(category2)
        db_session.commit()

        # Create test products
        products_data = [
            ("PROD-1", "Apple iPhone", test_category.id, True),
            ("PROD-2", "Samsung Galaxy", test_category.id, True),
            ("PROD-3", "Apple iPad", test_category.id, False),
            ("PROD-4", "Dell Laptop", category2.id, True),
        ]

        for sku, name, cat_id, is_active in products_data:
            data = ProductCreate(
                sku=sku,
                name=name,
                category_id=cat_id,
                purchase_price=Decimal("100.00"),
                first_sale_price=Decimal("150.00"),
                second_sale_price=Decimal("140.00"),
                third_sale_price=Decimal("130.00"),
                is_active=is_active,
            )
            await product_service.create_product(data, test_user.id)

        # Count all products
        assert await product_service.count_products() == 4

        # Count active products
        assert await product_service.count_products(is_active=True) == 3

        # Count by category
        assert await product_service.count_products(category_id=test_category.id) == 3

        # Count with search
        assert await product_service.count_products(search="Apple") == 2
