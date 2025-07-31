"""Pydantic schemas package for TechStore SaaS."""

from .auth import LoginRequest, TokenResponse, UserCreate, UserResponse
from .base import (
    BaseSchema,
    ErrorResponse,
    PaginationParams,
    ResponseSchema,
    TimestampSchema,
)
from .product import (
    Category,
    CategoryCreate,
    CategoryUpdate,
    Product,
    ProductCreate,
    ProductImage,
    ProductImageCreate,
    ProductList,
    ProductSupplier,
    ProductSupplierCreate,
    ProductUpdate,
)
from .sale import (
    ProductSearchResult,
    ReceiptData,
    SaleCreate,
    SaleInDB,
    SaleItemCreate,
    SaleItemInDB,
    SaleItemResponse,
    SaleListResponse,
    SaleResponse,
    SaleSummary,
    SaleUpdate,
    VoidSaleRequest,
)
from .supplier import Supplier, SupplierCreate, SupplierList, SupplierUpdate

__all__ = [
    # Auth
    "LoginRequest",
    "TokenResponse",
    "UserCreate",
    "UserResponse",
    # Base
    "BaseSchema",
    "TimestampSchema",
    "ResponseSchema",
    "ErrorResponse",
    "PaginationParams",
    # Product
    "Category",
    "CategoryCreate",
    "CategoryUpdate",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "ProductList",
    "ProductImage",
    "ProductImageCreate",
    "ProductSupplier",
    "ProductSupplierCreate",
    # Supplier
    "Supplier",
    "SupplierCreate",
    "SupplierUpdate",
    "SupplierList",
    # Sale
    "SaleCreate",
    "SaleUpdate",
    "SaleInDB",
    "SaleResponse",
    "SaleListResponse",
    "SaleItemCreate",
    "SaleItemInDB",
    "SaleItemResponse",
    "ProductSearchResult",
    "VoidSaleRequest",
    "ReceiptData",
    "SaleSummary",
]
