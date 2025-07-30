"""Unit tests for Product models."""

from decimal import Decimal

import pytest
from app.models.product import Category, Product, ProductImage, ProductSupplier
from app.models.supplier import Supplier
from app.models.user import User
from sqlalchemy.exc import IntegrityError


class TestCategoryModel:
    """Test Category model."""

    def test_create_category(self, db_session):
        """Test creating a basic category."""
        category = Category(
            name="Electronics",
            description="Electronic devices and accessories",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()

        assert category.id is not None
        assert category.name == "Electronics"
        assert category.description == "Electronic devices and accessories"
        assert category.is_active is True
        assert category.parent_id is None
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_unique_name(self, db_session):
        """Test that category names must be unique."""
        # Create first category
        category1 = Category(name="Electronics")
        db_session.add(category1)
        db_session.commit()

        # Try to create another with same name
        category2 = Category(name="Electronics")
        db_session.add(category2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_category_hierarchy(self, db_session):
        """Test parent-child category relationships."""
        # Create parent category
        parent = Category(name="Electronics")
        db_session.add(parent)
        db_session.commit()

        # Create child categories
        child1 = Category(name="Smartphones", parent_id=parent.id)
        child2 = Category(name="Laptops", parent_id=parent.id)
        db_session.add_all([child1, child2])
        db_session.commit()

        # Refresh parent to load relationships
        db_session.refresh(parent)

        assert len(parent.children) == 2
        assert child1.parent == parent
        assert child2.parent == parent
        assert child1 in parent.children
        assert child2 in parent.children

    def test_category_repr(self, db_session):
        """Test category string representation."""
        category = Category(name="Test Category")
        assert repr(category) == "<Category Test Category>"


class TestProductModel:
    """Test Product model."""

    def test_create_product(self, db_session, test_user, test_category):
        """Test creating a basic product."""
        product = Product(
            sku="IPHONE-14-PRO",
            name="iPhone 14 Pro",
            description="Latest iPhone model",
            category_id=test_category.id,
            brand="Apple",
            model="A2890",
            barcode="194253024019",
            purchase_price=Decimal("899.99"),
            first_sale_price=Decimal("1199.99"),
            second_sale_price=Decimal("1099.99"),
            third_sale_price=Decimal("999.99"),
            tax_rate=Decimal("16.00"),
            current_stock=10,
            minimum_stock=5,
            maximum_stock=50,
            location="A1-B2",
            is_active=True,
            created_by=test_user.id,
        )
        db_session.add(product)
        db_session.commit()

        assert product.id is not None
        assert product.sku == "IPHONE-14-PRO"
        assert product.name == "iPhone 14 Pro"
        assert product.purchase_price == Decimal("899.99")
        assert product.first_sale_price == Decimal("1199.99")
        assert product.tax_rate == Decimal("16.00")
        assert product.current_stock == 10
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_product_unique_sku(self, db_session, test_user, test_category):
        """Test that product SKUs must be unique."""
        # Create first product
        product1 = Product(
            sku="TEST-SKU",
            name="Product 1",
            category_id=test_category.id,
            purchase_price=Decimal("10.00"),
            first_sale_price=Decimal("15.00"),
            second_sale_price=Decimal("14.00"),
            third_sale_price=Decimal("13.00"),
            created_by=test_user.id,
        )
        db_session.add(product1)
        db_session.commit()

        # Try to create another with same SKU
        product2 = Product(
            sku="TEST-SKU",
            name="Product 2",
            category_id=test_category.id,
            purchase_price=Decimal("20.00"),
            first_sale_price=Decimal("25.00"),
            second_sale_price=Decimal("24.00"),
            third_sale_price=Decimal("23.00"),
            created_by=test_user.id,
        )
        db_session.add(product2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_product_relationships(self, db_session, test_user, test_category):
        """Test product relationships."""
        product = Product(
            sku="TEST-PRODUCT",
            name="Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("10.00"),
            first_sale_price=Decimal("15.00"),
            second_sale_price=Decimal("14.00"),
            third_sale_price=Decimal("13.00"),
            created_by=test_user.id,
        )
        db_session.add(product)
        db_session.commit()

        # Refresh to load relationships
        db_session.refresh(product)

        assert product.category == test_category
        assert product.creator == test_user
        assert product in test_category.products
        assert product in test_user.created_products

    def test_product_repr(self, db_session, test_user, test_category):
        """Test product string representation."""
        product = Product(
            sku="TEST-SKU",
            name="Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("10.00"),
            first_sale_price=Decimal("15.00"),
            second_sale_price=Decimal("14.00"),
            third_sale_price=Decimal("13.00"),
            created_by=test_user.id,
        )
        assert repr(product) == "<Product TEST-SKU: Test Product>"

    def test_product_default_values(self, db_session, test_user, test_category):
        """Test product default values."""
        product = Product(
            sku="DEFAULT-TEST",
            name="Default Test Product",
            category_id=test_category.id,
            purchase_price=Decimal("10.00"),
            first_sale_price=Decimal("15.00"),
            second_sale_price=Decimal("14.00"),
            third_sale_price=Decimal("13.00"),
            created_by=test_user.id,
        )
        db_session.add(product)
        db_session.commit()

        assert product.tax_rate == Decimal("16.00")
        assert product.current_stock == 0
        assert product.minimum_stock == 0
        assert product.is_active is True


class TestProductImageModel:
    """Test ProductImage model."""

    def test_create_product_image(self, db_session, test_product):
        """Test creating a product image."""
        image = ProductImage(
            product_id=test_product.id,
            image_url="/static/uploads/products/iphone-14-pro.jpg",
            is_primary=True,
            display_order=0,
        )
        db_session.add(image)
        db_session.commit()

        assert image.id is not None
        assert image.product_id == test_product.id
        assert image.image_url == "/static/uploads/products/iphone-14-pro.jpg"
        assert image.is_primary is True
        assert image.display_order == 0
        assert image.created_at is not None

    def test_product_image_cascade_delete(self, db_session, test_product):
        """Test that images are deleted when product is deleted."""
        # Create images
        image1 = ProductImage(product_id=test_product.id, image_url="image1.jpg")
        image2 = ProductImage(product_id=test_product.id, image_url="image2.jpg")
        db_session.add_all([image1, image2])
        db_session.commit()

        # Delete product
        db_session.delete(test_product)
        db_session.commit()

        # Check images are deleted
        assert (
            db_session.query(ProductImage).filter_by(product_id=test_product.id).count()
            == 0
        )

    def test_product_image_repr(self, db_session, test_product):
        """Test product image string representation."""
        image = ProductImage(product_id=test_product.id, image_url="test.jpg")
        db_session.add(image)
        db_session.commit()

        assert repr(image) == f"<ProductImage {image.id} for Product {test_product.id}>"


class TestProductSupplierModel:
    """Test ProductSupplier model."""

    def test_create_product_supplier(self, db_session, test_product, test_supplier):
        """Test creating a product-supplier relationship."""
        product_supplier = ProductSupplier(
            product_id=test_product.id,
            supplier_id=test_supplier.id,
            supplier_sku="SUPPLIER-SKU-123",
            is_preferred=True,
            last_purchase_price=Decimal("850.00"),
        )
        db_session.add(product_supplier)
        db_session.commit()

        assert product_supplier.id is not None
        assert product_supplier.product_id == test_product.id
        assert product_supplier.supplier_id == test_supplier.id
        assert product_supplier.supplier_sku == "SUPPLIER-SKU-123"
        assert product_supplier.is_preferred is True
        assert product_supplier.last_purchase_price == Decimal("850.00")

    def test_product_supplier_unique_constraint(
        self, db_session, test_product, test_supplier
    ):
        """Test that product-supplier combination must be unique."""
        # Create first relationship
        ps1 = ProductSupplier(product_id=test_product.id, supplier_id=test_supplier.id)
        db_session.add(ps1)
        db_session.commit()

        # Try to create duplicate
        ps2 = ProductSupplier(product_id=test_product.id, supplier_id=test_supplier.id)
        db_session.add(ps2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_product_supplier_cascade_delete(
        self, db_session, test_product, test_supplier
    ):
        """Test that supplier relationships are deleted when product is deleted."""
        # Create relationship
        ps = ProductSupplier(product_id=test_product.id, supplier_id=test_supplier.id)
        db_session.add(ps)
        db_session.commit()

        # Delete product
        db_session.delete(test_product)
        db_session.commit()

        # Check relationship is deleted
        assert (
            db_session.query(ProductSupplier)
            .filter_by(product_id=test_product.id)
            .count()
            == 0
        )

    def test_product_supplier_repr(self, db_session, test_product, test_supplier):
        """Test product supplier string representation."""
        ps = ProductSupplier(product_id=test_product.id, supplier_id=test_supplier.id)
        assert (
            repr(ps)
            == f"<ProductSupplier Product:{test_product.id} Supplier:{test_supplier.id}>"
        )


# Fixtures for tests
@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_category(db_session):
    """Create a test category."""
    category = Category(name="Test Category", is_active=True)
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def test_product(db_session, test_user, test_category):
    """Create a test product."""
    product = Product(
        sku="TEST-PRODUCT-001",
        name="Test Product",
        category_id=test_category.id,
        purchase_price=Decimal("100.00"),
        first_sale_price=Decimal("150.00"),
        second_sale_price=Decimal("140.00"),
        third_sale_price=Decimal("130.00"),
        created_by=test_user.id,
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture
def test_supplier(db_session):
    """Create a test supplier."""
    supplier = Supplier(
        name="Test Supplier",
        email="supplier@example.com",
        phone="123-456-7890",
        is_active=True,
    )
    db_session.add(supplier)
    db_session.commit()
    return supplier
