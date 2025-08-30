"""Pydantic schemas for product-related data validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryBase(BaseModel):
    """Base schema for category data."""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(
        None, description="Parent category ID for hierarchy"
    )
    is_active: bool = Field(True, description="Whether category is active")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryInDB(CategoryBase):
    """Schema for category data from database."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Category(CategoryInDB):
    """Schema for category API responses."""

    pass


class ProductBase(BaseModel):
    """Base schema for product data."""

    sku: str = Field(
        ...,
        pattern="^[A-Za-z0-9-]+$",
        max_length=50,
        description="Product SKU (alphanumeric and hyphens only)",
    )
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category_id: int = Field(..., description="Product category ID")
    brand: Optional[str] = Field(None, max_length=100, description="Brand name")
    model: Optional[str] = Field(None, max_length=100, description="Model name")
    barcode: Optional[str] = Field(None, max_length=50, description="Product barcode")
    purchase_price: Decimal = Field(
        ..., ge=0, decimal_places=2, description="Purchase price"
    )
    first_sale_price: Decimal = Field(
        ..., ge=0, decimal_places=2, description="Primary selling price"
    )
    second_sale_price: Decimal = Field(
        ..., ge=0, decimal_places=2, description="Secondary selling price"
    )
    third_sale_price: Decimal = Field(
        ..., ge=0, decimal_places=2, description="Tertiary selling price"
    )
    tax_rate: Decimal = Field(
        default=Decimal("16.00"),
        ge=0,
        le=100,
        decimal_places=2,
        description="Tax rate percentage",
    )
    current_stock: int = Field(default=0, ge=0, description="Current stock quantity")
    minimum_stock: int = Field(default=0, ge=0, description="Minimum stock level")
    maximum_stock: Optional[int] = Field(None, ge=0, description="Maximum stock level")
    location: Optional[str] = Field(
        None, max_length=100, description="Storage location"
    )
    is_active: bool = Field(True, description="Whether product is active")

    @field_validator("first_sale_price", "second_sale_price", "third_sale_price")
    @classmethod
    def validate_sale_prices(cls, v: Decimal, info) -> Decimal:
        """Validate that sale prices are not less than purchase price."""
        if "purchase_price" in info.data and v < info.data["purchase_price"]:
            raise ValueError(
                "El precio de venta no puede ser menor que el precio de compra"
            )
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    supplier_ids: Optional[list[int]] = Field(
        default_factory=list, description="List of supplier IDs"
    )
    images: Optional[list[str]] = Field(
        default_factory=list, max_length=5, description="List of image URLs (max 5)"
    )

    @field_validator("images")
    @classmethod
    def validate_images(cls, v: list[str]) -> list[str]:
        """Validate image URLs and count."""
        if len(v) > 5:
            raise ValueError("Máximo 5 imágenes permitidas")
        return v


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    sku: Optional[str] = Field(None, pattern="^[A-Za-z0-9-]+$", max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    purchase_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    first_sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    second_sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    third_sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    current_stock: Optional[int] = Field(None, ge=0)
    minimum_stock: Optional[int] = Field(None, ge=0)
    maximum_stock: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class ProductImageBase(BaseModel):
    """Base schema for product image data."""

    image_url: str = Field(..., max_length=500, description="Image URL or path")
    is_primary: bool = Field(False, description="Whether this is the primary image")
    display_order: int = Field(0, ge=0, description="Display order")


class ProductImageCreate(ProductImageBase):
    """Schema for creating a product image."""

    product_id: int = Field(..., description="Product ID")


class ProductImage(ProductImageBase):
    """Schema for product image API responses."""

    id: int
    product_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductSupplierBase(BaseModel):
    """Base schema for product supplier data."""

    supplier_id: int = Field(..., description="Supplier ID")
    supplier_sku: Optional[str] = Field(
        None, max_length=100, description="Supplier's SKU"
    )
    is_preferred: bool = Field(
        False, description="Whether this is the preferred supplier"
    )
    last_purchase_price: Optional[Decimal] = Field(
        None, ge=0, decimal_places=2, description="Last purchase price from supplier"
    )


class ProductSupplierCreate(ProductSupplierBase):
    """Schema for creating a product supplier link."""

    product_id: int = Field(..., description="Product ID")


class ProductSupplier(ProductSupplierBase):
    """Schema for product supplier API responses."""

    id: int
    product_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductInDB(ProductBase):
    """Schema for product data from database."""

    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Product(ProductInDB):
    """Schema for product API responses."""

    category: Optional[Category] = None
    images: list[ProductImage] = Field(default_factory=list)
    suppliers: list[ProductSupplier] = Field(default_factory=list)


class ProductList(BaseModel):
    """Schema for product list responses."""

    items: list[Product]
    total: int
    page: int
    page_size: int
    pages: int
