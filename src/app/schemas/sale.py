"""Pydantic schemas for sales management."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SaleItemBase(BaseModel):
    """Base schema for sale items."""

    product_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0, decimal_places=2)
    discount_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)


class SaleItemCreate(SaleItemBase):
    """Schema for creating sale items."""

    pass


class SaleItemInDB(SaleItemBase):
    """Schema for sale items in database."""

    id: int
    total_price: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class SaleItemResponse(SaleItemInDB):
    """Schema for sale item responses."""

    product_name: Optional[str] = None
    product_sku: Optional[str] = None


class SaleBase(BaseModel):
    """Base schema for sales."""

    customer_id: Optional[int] = None
    payment_method: Optional[str] = Field(
        None, pattern="^(cash|credit|transfer|mixed)$"
    )
    notes: Optional[str] = None


class SaleCreate(SaleBase):
    """Schema for creating a sale."""

    items: list[SaleItemCreate] = Field(min_length=1)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)

    @field_validator("items")
    @classmethod
    def validate_unique_products(
        cls, items: list[SaleItemCreate]
    ) -> list[SaleItemCreate]:
        """Ensure no duplicate products in sale."""
        product_ids = [item.product_id for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate products not allowed in same sale")
        return items


class SaleUpdate(BaseModel):
    """Schema for updating sale (limited fields)."""

    notes: Optional[str] = None
    payment_status: Optional[str] = Field(None, pattern="^(pending|partial|paid)$")


class SaleInDB(SaleBase):
    """Schema for sale in database."""

    id: int
    invoice_number: str
    user_id: int
    sale_date: datetime
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_status: str
    is_voided: bool
    void_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class SaleResponse(SaleInDB):
    """Schema for sale responses."""

    items: list[SaleItemResponse] = []
    customer_name: Optional[str] = None
    user_name: Optional[str] = None
    amount_paid: Decimal = Field(default=Decimal("0"))
    amount_due: Decimal = Field(default=Decimal("0"))


class SaleListResponse(BaseModel):
    """Schema for sale list responses."""

    id: int
    invoice_number: str
    sale_date: datetime
    customer_name: Optional[str]
    total_amount: Decimal
    payment_status: str
    payment_method: Optional[str]
    is_voided: bool

    class Config:
        """Pydantic config."""

        from_attributes = True


class SaleSummary(BaseModel):
    """Schema for sales summary/analytics."""

    total_sales: Decimal
    total_count: int
    cash_sales: Decimal
    credit_sales: Decimal
    transfer_sales: Decimal
    pending_amount: Decimal
    average_sale: Decimal


class ProductSearchResult(BaseModel):
    """Schema for product search results in POS."""

    id: int
    sku: str
    name: str
    barcode: Optional[str]
    price: Decimal
    stock: int
    category: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class VoidSaleRequest(BaseModel):
    """Schema for voiding a sale."""

    reason: str = Field(min_length=10)


class ReceiptData(BaseModel):
    """Schema for receipt generation."""

    sale: SaleResponse
    company_name: str
    company_address: str
    company_phone: str
    company_email: str
    tax_id: str
