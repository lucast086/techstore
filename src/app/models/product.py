"""Product and Category models for inventory management."""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DECIMAL,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class Category(BaseModel):
    """Product category model with hierarchical support.

    Attributes:
        name: Category name (unique).
        description: Optional category description.
        parent_id: ID of parent category for hierarchy.
        is_active: Whether category is active for use.
        parent: Parent category relationship.
        children: Child categories relationship.
        products: Products in this category.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side="Category.id", backref="children"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category"
    )

    def __repr__(self) -> str:
        """String representation of Category."""
        return f"<Category {self.name}>"


class Product(BaseModel):
    """Product model for inventory management.

    Attributes:
        sku: Unique product SKU (stock keeping unit).
        name: Product name.
        description: Optional product description.
        category_id: ID of product category.
        brand: Optional brand name.
        model: Optional model name.
        barcode: Optional barcode.
        purchase_price: Cost price of product.
        first_sale_price: Primary selling price.
        second_sale_price: Secondary selling price.
        third_sale_price: Tertiary selling price.
        tax_rate: Tax rate percentage (default 16%).
        current_stock: Current stock quantity.
        minimum_stock: Minimum stock level for alerts.
        maximum_stock: Maximum stock level.
        location: Storage location in warehouse.
        is_active: Whether product is active for sale.
        created_by: ID of user who created the product.
        category: Product category relationship.
        creator: User who created the product.
        images: Product images relationship.
        suppliers: Product suppliers relationship.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True
    )
    purchase_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    first_sale_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    second_sale_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    third_sale_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(
        DECIMAL(5, 2), nullable=False, default=Decimal("16.00")
    )
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    minimum_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    maximum_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    creator: Mapped["User"] = relationship("User", backref="created_products")
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage", back_populates="product", cascade="all, delete-orphan"
    )
    suppliers: Mapped[list["ProductSupplier"]] = relationship(
        "ProductSupplier", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Product."""
        return f"<Product {self.sku}: {self.name}>"


class ProductImage(BaseModel):
    """Product image model for storing product photos.

    Attributes:
        product_id: ID of related product.
        image_url: URL or path to image file.
        is_primary: Whether this is the primary image.
        display_order: Order for displaying images.
        product: Related product relationship.
    """

    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="images")

    def __repr__(self) -> str:
        """String representation of ProductImage."""
        return f"<ProductImage {self.id} for Product {self.product_id}>"


class ProductSupplier(BaseModel):
    """Product supplier relationship model.

    Attributes:
        product_id: ID of product.
        supplier_id: ID of supplier.
        supplier_sku: Supplier's SKU for this product.
        is_preferred: Whether this is the preferred supplier.
        last_purchase_price: Last price paid to this supplier.
        product: Related product relationship.
    """

    __tablename__ = "product_suppliers"
    __table_args__ = (
        UniqueConstraint("product_id", "supplier_id", name="uq_product_supplier"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False
    )
    supplier_sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_purchase_price: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), nullable=True
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="suppliers")

    def __repr__(self) -> str:
        """String representation of ProductSupplier."""
        return (
            f"<ProductSupplier Product:{self.product_id} Supplier:{self.supplier_id}>"
        )
