"""Product service for business logic and data operations."""

import logging
from typing import Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.product import Category, Product, ProductImage, ProductSupplier
from app.models.supplier import Supplier
from app.schemas.filters import (
    ProductFilter,
    ProductListItem,
    ProductListParams,
    SortField,
    SortOrder,
    StockStatus,
)
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

    async def delete_product(self, product_id: int) -> bool:
        """Soft delete a product by setting is_active=False.

        Args:
            product_id: Product ID to delete.

        Returns:
            True if product was deleted, False if not found.
        """
        product = await self.get_product(product_id)
        if not product:
            return False

        product.is_active = False
        self.db.commit()
        return True

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

    async def get_product_list(
        self, params: ProductListParams
    ) -> tuple[list[ProductListItem], int]:
        """Get paginated product list with advanced filters.

        Args:
            params: Product list parameters including filters, sorting, and pagination.

        Returns:
            Tuple of product items and total count.
        """
        logger.info(f"Fetching product list with params: {params}")

        # Start with base query
        # For SQLite compatibility in tests, only use joinedload if not SQLite
        db_url = str(self.db.bind.url) if self.db.bind else str(self.db.get_bind().url)
        logger.info(f"Database URL detected: {db_url}")
        if "sqlite" in db_url:
            logger.info("Using simple query for SQLite")
            query = self.db.query(Product)
        else:
            logger.info("Using joinedload query for PostgreSQL")
            query = self.db.query(Product).options(
                joinedload(Product.category),
                joinedload(Product.images),
            )

        # Apply filters
        query = self._apply_filters(query, params.filters)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        query = self._apply_sorting(query, params.sort_by, params.sort_order)

        # Apply pagination
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

        # Execute query
        products = query.all()

        # Convert to list items
        items = []
        for product in products:
            # Calculate stock status
            stock_status = self._calculate_stock_status(product)

            # Calculate profit margin
            profit_margin = product.first_sale_price - product.purchase_price
            margin_percentage = (
                float(profit_margin / product.purchase_price * 100)
                if product.purchase_price > 0
                else 0.0
            )

            # Get primary image
            primary_image = None
            if hasattr(product, "images"):
                for img in product.images:
                    if img.is_primary:
                        primary_image = img.image_url
                        break

            # For SQLite, manually load category if needed
            category_name = ""
            if hasattr(product, "category") and product.category:
                category_name = product.category.name
            elif product.category_id:
                # Manually fetch category for SQLite
                from app.models.product import Category

                category = (
                    self.db.query(Category)
                    .filter(Category.id == product.category_id)
                    .first()
                )
                category_name = category.name if category else ""

            item = ProductListItem(
                id=product.id,
                sku=product.sku,
                name=product.name,
                barcode=product.barcode,
                brand=product.brand,
                model=product.model,
                category_id=product.category_id,
                category_name=category_name,
                purchase_price=product.purchase_price,
                first_sale_price=product.first_sale_price,
                second_sale_price=product.second_sale_price,
                third_sale_price=product.third_sale_price,
                current_stock=product.current_stock,
                minimum_stock=product.minimum_stock,
                stock_status=stock_status,
                profit_margin=profit_margin,
                margin_percentage=margin_percentage,
                primary_image=primary_image,
                is_active=product.is_active,
                updated_at=product.updated_at,
            )
            items.append(item)

        logger.info(f"Found {total} products, returning page {params.page}")
        return items, total

    def _apply_filters(self, query, filters: ProductFilter):
        """Apply filters to product query.

        Args:
            query: SQLAlchemy query object.
            filters: Product filter parameters.

        Returns:
            Filtered query.
        """
        # Text search
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.barcode.ilike(search_term),
                    Product.brand.ilike(search_term),
                    Product.model.ilike(search_term),
                )
            )

        # Category filter
        if filters.category_ids:
            query = query.filter(Product.category_id.in_(filters.category_ids))

        # Price range
        if filters.price_min is not None:
            query = query.filter(Product.first_sale_price >= filters.price_min)
        if filters.price_max is not None:
            query = query.filter(Product.first_sale_price <= filters.price_max)

        # Stock status
        if filters.stock_status != StockStatus.ALL:
            if filters.stock_status == StockStatus.OUT_OF_STOCK:
                query = query.filter(Product.current_stock == 0)
            elif filters.stock_status == StockStatus.LOW_STOCK:
                query = query.filter(
                    and_(
                        Product.current_stock > 0,
                        Product.current_stock <= Product.minimum_stock,
                    )
                )
            elif filters.stock_status == StockStatus.IN_STOCK:
                query = query.filter(Product.current_stock > Product.minimum_stock)
            elif filters.stock_status == StockStatus.OVERSTOCK:
                query = query.filter(
                    and_(
                        Product.maximum_stock.isnot(None),
                        Product.current_stock >= Product.maximum_stock,
                    )
                )

        # Active status
        if filters.is_active is not None:
            query = query.filter(Product.is_active == filters.is_active)

        # Brand filter
        if filters.brands:
            query = query.filter(Product.brand.in_(filters.brands))

        return query

    def _apply_sorting(self, query, sort_by: SortField, order: SortOrder):
        """Apply sorting to product query.

        Args:
            query: SQLAlchemy query object.
            sort_by: Field to sort by.
            order: Sort order (ASC or DESC).

        Returns:
            Sorted query.
        """
        # Map sort fields to model attributes
        sort_mapping = {
            SortField.NAME: Product.name,
            SortField.SKU: Product.sku,
            SortField.PRICE: Product.first_sale_price,
            SortField.STOCK: Product.current_stock,
            SortField.UPDATED: Product.updated_at,
        }

        # Special handling for category name
        if sort_by == SortField.CATEGORY:
            query = query.join(Category)
            sort_column = Category.name
        else:
            sort_column = sort_mapping.get(sort_by, Product.name)

        if order == SortOrder.DESC:
            return query.order_by(sort_column.desc())
        else:
            return query.order_by(sort_column.asc())

    def _calculate_stock_status(self, product: Product) -> str:
        """Calculate stock status for a product.

        Args:
            product: Product model instance.

        Returns:
            Stock status string.
        """
        if product.current_stock == 0:
            return "out_of_stock"
        elif product.current_stock <= product.minimum_stock:
            return "low_stock"
        elif (
            product.maximum_stock is not None
            and product.current_stock >= product.maximum_stock
        ):
            return "overstock"
        else:
            return "normal"

    async def get_filter_options(self) -> dict:
        """Get available filter options.

        Returns:
            Dictionary with available brands and price range.
        """
        # Get unique brands
        brands = (
            self.db.query(Product.brand)
            .filter(Product.brand.isnot(None))
            .distinct()
            .all()
        )

        # Get price range
        price_stats = self.db.query(
            func.min(Product.first_sale_price).label("min_price"),
            func.max(Product.first_sale_price).label("max_price"),
        ).first()

        return {
            "brands": [b[0] for b in brands if b[0]],
            "price_range": {
                "min": float(price_stats.min_price or 0),
                "max": float(price_stats.max_price or 0),
            },
        }
