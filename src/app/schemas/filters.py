"""Filter schemas for product list functionality."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StockStatus(str, Enum):
    """Stock status filter options."""

    ALL = "all"
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    OVERSTOCK = "overstock"


class ViewMode(str, Enum):
    """Product list view modes."""

    TABLE = "table"
    CARD = "card"


class SortField(str, Enum):
    """Fields available for sorting."""

    NAME = "name"
    SKU = "sku"
    PRICE = "first_sale_price"
    STOCK = "current_stock"
    CATEGORY = "category_name"
    UPDATED = "updated_at"


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class ProductFilter(BaseModel):
    """Product list filter parameters."""

    search: Optional[str] = None
    category_ids: Optional[list[int]] = []
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    stock_status: StockStatus = StockStatus.ALL
    is_active: Optional[bool] = None
    supplier_ids: Optional[list[int]] = []
    brands: Optional[list[str]] = []


class ProductListParams(BaseModel):
    """Parameters for product list request."""

    filters: ProductFilter = Field(default_factory=ProductFilter)
    sort_by: SortField = SortField.NAME
    sort_order: SortOrder = SortOrder.ASC
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=10, le=100)
    view_mode: ViewMode = ViewMode.TABLE


class ProductListItem(BaseModel):
    """Simplified product item for list display."""

    id: int
    sku: str
    name: str
    barcode: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    category_id: int
    category_name: str
    purchase_price: Decimal
    first_sale_price: Decimal
    second_sale_price: Decimal
    third_sale_price: Decimal
    current_stock: int
    minimum_stock: int
    stock_status: str
    profit_margin: Decimal
    margin_percentage: float
    primary_image: Optional[str]
    is_active: bool
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProductListResponse(BaseModel):
    """Response for product list endpoint."""

    items: list[ProductListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: ProductFilter


class SavedFilter(BaseModel):
    """Saved filter configuration."""

    name: str
    filter_json: ProductFilter
    is_default: bool = False
