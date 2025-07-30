"""Product service for business logic and data operations."""

import logging
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.product import Category, Product, ProductImage, ProductSupplier
from app.models.supplier import Supplier
from app.schemas.product import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
)

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for managing product categories."""

    def __init__(self, db: Session):
        """Initialize category service.

        Args:
            db: Database session.
        """
        self.db = db

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category.

        Args:
            category_data: Category creation data.

        Returns:
            Created category.

        Raises:
            ValueError: If category name already exists.
        """
        logger.info(f"Creating category: {category_data.name}")

        # Check if category name already exists
        existing = (
            self.db.query(Category).filter(Category.name == category_data.name).first()
        )
        if existing:
            logger.error(f"Category with name '{category_data.name}' already exists")
            raise ValueError(
                f"Category with name '{category_data.name}' already exists"
            )

        # Validate parent category if provided
        if category_data.parent_id:
            parent = (
                self.db.query(Category)
                .filter(Category.id == category_data.parent_id)
                .first()
            )
            if not parent:
                raise ValueError(
                    f"Parent category with ID {category_data.parent_id} not found"
                )

        # Create category
        category = Category(**category_data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        logger.info(f"Successfully created category: {category.id}")
        return category

    async def get_categories(
        self, is_active: Optional[bool] = None, parent_id: Optional[int] = None
    ) -> list[Category]:
        """Get all categories with optional filters.

        Args:
            is_active: Filter by active status.
            parent_id: Filter by parent category.

        Returns:
            List of categories.
        """
        query = self.db.query(Category)

        if is_active is not None:
            query = query.filter(Category.is_active == is_active)

        if parent_id is not None:
            query = query.filter(Category.parent_id == parent_id)

        return query.order_by(Category.name).all()

    async def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID.

        Args:
            category_id: Category ID.

        Returns:
            Category if found, None otherwise.
        """
        return self.db.query(Category).filter(Category.id == category_id).first()

    async def update_category(
        self, category_id: int, category_data: CategoryUpdate
    ) -> Optional[Category]:
        """Update a category.

        Args:
            category_id: Category ID to update.
            category_data: Update data.

        Returns:
            Updated category if found, None otherwise.

        Raises:
            ValueError: If new name already exists.
        """
        category = await self.get_category(category_id)
        if not category:
            return None

        # Check if new name already exists (if name is being changed)
        if category_data.name and category_data.name != category.name:
            existing = (
                self.db.query(Category)
                .filter(Category.name == category_data.name, Category.id != category_id)
                .first()
            )
            if existing:
                raise ValueError(
                    f"Category with name '{category_data.name}' already exists"
                )

        # Update fields
        for field, value in category_data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)

        self.db.commit()
        self.db.refresh(category)
        return category


class ProductService:
    """Service for managing products."""

    def __init__(self, db: Session):
        """Initialize product service.

        Args:
            db: Database session.
        """
        self.db = db
        self.category_service = CategoryService(db)

    async def create_product(
        self, product_data: ProductCreate, user_id: int
    ) -> Product:
        """Create a new product with images and supplier links.

        Args:
            product_data: Product creation data.
            user_id: ID of user creating the product.

        Returns:
            Created product.

        Raises:
            ValueError: If SKU already exists or category not found.
        """
        logger.info(f"Creating product with SKU: {product_data.sku}")

        # Check if SKU already exists
        existing = (
            self.db.query(Product).filter(Product.sku == product_data.sku).first()
        )
        if existing:
            logger.error(f"Product with SKU {product_data.sku} already exists")
            raise ValueError(f"Product with SKU {product_data.sku} already exists")

        # Validate category
        category = await self.category_service.get_category(product_data.category_id)
        if not category or not category.is_active:
            raise ValueError(
                f"Invalid or inactive category ID: {product_data.category_id}"
            )

        # Validate suppliers if provided
        if product_data.supplier_ids:
            supplier_count = (
                self.db.query(func.count(Supplier.id))
                .filter(
                    Supplier.id.in_(product_data.supplier_ids),
                    Supplier.is_active.is_(True),
                )
                .scalar()
            )
            if supplier_count != len(product_data.supplier_ids):
                raise ValueError("One or more supplier IDs are invalid or inactive")

        try:
            # Create product
            product_dict = product_data.model_dump(exclude={"supplier_ids", "images"})
            product = Product(**product_dict, created_by=user_id)
            self.db.add(product)
            self.db.flush()  # Get product ID without committing

            # Add images
            for idx, image_url in enumerate(product_data.images or []):
                image = ProductImage(
                    product_id=product.id,
                    image_url=image_url,
                    is_primary=(idx == 0),
                    display_order=idx,
                )
                self.db.add(image)

            # Link suppliers
            for supplier_id in product_data.supplier_ids or []:
                product_supplier = ProductSupplier(
                    product_id=product.id,
                    supplier_id=supplier_id,
                    is_preferred=(len(product_data.supplier_ids) == 1),
                )
                self.db.add(product_supplier)

            self.db.commit()
            self.db.refresh(product)

            # Load relationships
            product = (
                self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.images),
                    joinedload(Product.suppliers),
                )
                .filter(Product.id == product.id)
                .first()
            )

            logger.info(f"Successfully created product: {product.id}")
            return product

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database error creating product: {str(e)}")
            raise ValueError("Database constraint violation") from e

    async def get_products(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> list[Product]:
        """Get products with optional filters.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            is_active: Filter by active status.
            category_id: Filter by category.
            search: Search in name, SKU, or barcode.

        Returns:
            List of products.
        """
        query = self.db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.images),
            joinedload(Product.suppliers),
        )

        if is_active is not None:
            query = query.filter(Product.is_active == is_active)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
                Product.barcode.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.offset(skip).limit(limit).all()

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID.

        Args:
            product_id: Product ID.

        Returns:
            Product if found, None otherwise.
        """
        return (
            self.db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.images),
                joinedload(Product.suppliers),
            )
            .filter(Product.id == product_id)
            .first()
        )

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by SKU.

        Args:
            sku: Product SKU.

        Returns:
            Product if found, None otherwise.
        """
        return (
            self.db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.images),
                joinedload(Product.suppliers),
            )
            .filter(Product.sku == sku)
            .first()
        )

    async def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[Product]:
        """Update a product.

        Args:
            product_id: Product ID to update.
            product_data: Update data.

        Returns:
            Updated product if found, None otherwise.

        Raises:
            ValueError: If new SKU already exists.
        """
        product = await self.get_product(product_id)
        if not product:
            return None

        # Check if new SKU already exists (if SKU is being changed)
        if product_data.sku and product_data.sku != product.sku:
            existing = (
                self.db.query(Product)
                .filter(Product.sku == product_data.sku, Product.id != product_id)
                .first()
            )
            if existing:
                raise ValueError(
                    f"Product with SKU '{product_data.sku}' already exists"
                )

        # Validate category if being changed
        if product_data.category_id:
            category = await self.category_service.get_category(
                product_data.category_id
            )
            if not category or not category.is_active:
                raise ValueError(
                    f"Invalid or inactive category ID: {product_data.category_id}"
                )

        # Update fields
        for field, value in product_data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)
        return product

    async def update_stock(
        self, product_id: int, quantity: int, is_absolute: bool = False
    ) -> Optional[Product]:
        """Update product stock.

        Args:
            product_id: Product ID.
            quantity: Stock quantity (absolute or relative).
            is_absolute: If True, set stock to quantity. If False, add quantity to current stock.

        Returns:
            Updated product if found, None otherwise.

        Raises:
            ValueError: If resulting stock would be negative.
        """
        product = await self.get_product(product_id)
        if not product:
            return None

        if is_absolute:
            if quantity < 0:
                raise ValueError("Stock quantity cannot be negative")
            product.current_stock = quantity
        else:
            new_stock = product.current_stock + quantity
            if new_stock < 0:
                raise ValueError(
                    f"Insufficient stock. Current: {product.current_stock}, Requested: {quantity}"
                )
            product.current_stock = new_stock

        self.db.commit()
        self.db.refresh(product)

        logger.info(f"Updated stock for product {product_id}: {product.current_stock}")
        return product

    async def count_products(
        self,
        is_active: Optional[bool] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count products with optional filters.

        Args:
            is_active: Filter by active status.
            category_id: Filter by category.
            search: Search in name, SKU, or barcode.

        Returns:
            Total count of products matching filters.
        """
        query = self.db.query(func.count(Product.id))

        if is_active is not None:
            query = query.filter(Product.is_active == is_active)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
                Product.barcode.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.scalar() or 0
