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
]
