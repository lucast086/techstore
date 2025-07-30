# STORY-015: Product List

## Story Metadata
- **Epic**: EPIC-003 - Product Management
- **Priority**: P0 - Critical
- **Estimate**: 13 points
- **Status**: TODO

## User Story
**As** Carlos (Store Manager),
**I want to** view, search, and filter my complete product catalog with real-time stock information,
**So that** I can quickly find products for customers and make informed inventory decisions.

## Acceptance Criteria
1. **List Display**: Show products in a responsive table/grid with key information (name, SKU, price, stock, category)
2. **View Modes**: Toggle between table view (detailed) and card view (visual with images)
3. **Real-time Search**: Search by name, SKU, barcode, brand, or model with instant results
4. **Advanced Filters**: Filter by category, price range, stock level, supplier, and active status
5. **Stock Indicators**: Visual indicators for out-of-stock, low stock, and overstocked items
6. **Sorting Options**: Sort by name, SKU, price, stock level, category, or last updated
7. **Pagination**: Efficient pagination with customizable page size (25, 50, 100 items)
8. **Bulk Selection**: Select multiple products for bulk operations (export, price update, status change)
9. **Quick Actions**: Inline actions for stock adjustment, price edit, and status toggle
10. **Export Options**: Export filtered results to CSV, Excel, or PDF with selected columns
11. **Saved Filters**: Save frequently used filter combinations for quick access
12. **Mobile Responsive**: Fully functional on tablets and smartphones for inventory checks
13. **Print Labels**: Generate and print price labels for selected products
14. **Stock Alerts**: Highlight products below minimum stock or above maximum stock
15. **Performance**: List loads in under 2 seconds for 10,000+ products

## Technical Details

### File Structure
```
app/
├── models/
│   └── product.py          # Query optimizations
├── schemas/
│   ├── product.py          # List schemas
│   └── filters.py          # Filter schemas
├── services/
│   ├── product_service.py  # Enhanced list methods
│   └── export_service.py   # Export functionality
├── api/v1/
│   └── products.py         # List endpoints
├── web/
│   └── products.py         # List routes
├── utils/
│   ├── pagination.py       # Pagination helpers
│   └── export.py           # Export utilities
└── templates/
    └── products/
        ├── index.html      # Main list page
        ├── _table_view.html # Table partial
        ├── _card_view.html  # Card grid partial
        ├── _filters.html    # Filter sidebar
        └── _bulk_actions.html # Bulk action bar
```

### Database Optimizations
```sql
-- Composite indexes for common queries
CREATE INDEX idx_products_search ON products
    USING gin(to_tsvector('spanish', name || ' ' || COALESCE(description, '')));

CREATE INDEX idx_products_sku_barcode ON products(sku, barcode);
CREATE INDEX idx_products_category_active ON products(category_id, is_active);
CREATE INDEX idx_products_stock_levels ON products(current_stock, minimum_stock);
CREATE INDEX idx_products_prices ON products(sale_price, purchase_price);
CREATE INDEX idx_products_updated ON products(updated_at DESC);

-- Materialized view for product list performance
CREATE MATERIALIZED VIEW product_list_view AS
SELECT
    p.id,
    p.sku,
    p.name,
    p.barcode,
    p.brand,
    p.model,
    p.purchase_price,
    p.sale_price,
    p.current_stock,
    p.minimum_stock,
    p.is_active,
    p.updated_at,
    c.id as category_id,
    c.name as category_name,
    c.full_path as category_path,
    pi.image_url as primary_image,
    CASE
        WHEN p.current_stock = 0 THEN 'out_of_stock'
        WHEN p.current_stock <= p.minimum_stock THEN 'low_stock'
        WHEN p.maximum_stock IS NOT NULL
            AND p.current_stock >= p.maximum_stock THEN 'overstock'
        ELSE 'normal'
    END as stock_status,
    (p.sale_price - p.purchase_price) as profit_margin,
    ROUND(((p.sale_price - p.purchase_price) / p.purchase_price * 100), 2) as margin_percentage
FROM products p
JOIN categories c ON p.category_id = c.id
LEFT JOIN product_images pi ON p.id = pi.product_id AND pi.is_primary = true;

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_product_list_view()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY product_list_view;
END;
$$ LANGUAGE plpgsql;

-- Saved filters table
CREATE TABLE saved_filters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    filter_json JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, created_by)
);
```

## Implementation Requirements

### 1. Filter and List Schemas
```python
# app/schemas/filters.py
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum

class StockStatus(str, Enum):
    ALL = "all"
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    OVERSTOCK = "overstock"

class ViewMode(str, Enum):
    TABLE = "table"
    CARD = "card"

class SortField(str, Enum):
    NAME = "name"
    SKU = "sku"
    PRICE = "sale_price"
    STOCK = "current_stock"
    CATEGORY = "category_name"
    UPDATED = "updated_at"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class ProductFilter(BaseModel):
    search: Optional[str] = None
    category_ids: Optional[List[int]] = []
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    stock_status: StockStatus = StockStatus.ALL
    is_active: Optional[bool] = None
    supplier_ids: Optional[List[int]] = []
    brands: Optional[List[str]] = []

class ProductListParams(BaseModel):
    filters: ProductFilter = ProductFilter()
    sort_by: SortField = SortField.NAME
    sort_order: SortOrder = SortOrder.ASC
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=10, le=100)
    view_mode: ViewMode = ViewMode.TABLE

class ProductListItem(BaseModel):
    id: int
    sku: str
    name: str
    barcode: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    category_id: int
    category_name: str
    category_path: str
    purchase_price: Decimal
    sale_price: Decimal
    current_stock: int
    minimum_stock: int
    stock_status: str
    profit_margin: Decimal
    margin_percentage: float
    primary_image: Optional[str]
    is_active: bool
    updated_at: datetime

class ProductListResponse(BaseModel):
    items: List[ProductListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: ProductFilter

class SavedFilter(BaseModel):
    name: str
    filter_json: ProductFilter
    is_default: bool = False
```

### 2. Enhanced Product Service
```python
# app/services/product_service.py
from typing import List, Tuple
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session
from app.models.product import Product, ProductListView
from app.schemas.filters import ProductFilter, ProductListParams

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    async def get_product_list(
        self,
        params: ProductListParams
    ) -> Tuple[List[ProductListItem], int]:
        """Get paginated product list with filters"""
        logger.info(f"Fetching product list with params: {params}")

        # Start with base query
        query = self.db.query(ProductListView)

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

        # Convert to schema
        items = [
            ProductListItem.from_orm(p) for p in products
        ]

        logger.info(f"Found {total} products, returning page {params.page}")
        return items, total

    def _apply_filters(
        self,
        query,
        filters: ProductFilter
    ):
        """Apply filters to query"""

        # Text search
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    ProductListView.name.ilike(search_term),
                    ProductListView.sku.ilike(search_term),
                    ProductListView.barcode.ilike(search_term),
                    ProductListView.brand.ilike(search_term),
                    ProductListView.model.ilike(search_term)
                )
            )

        # Category filter
        if filters.category_ids:
            query = query.filter(
                ProductListView.category_id.in_(filters.category_ids)
            )

        # Price range
        if filters.price_min is not None:
            query = query.filter(
                ProductListView.sale_price >= filters.price_min
            )
        if filters.price_max is not None:
            query = query.filter(
                ProductListView.sale_price <= filters.price_max
            )

        # Stock status
        if filters.stock_status != StockStatus.ALL:
            query = query.filter(
                ProductListView.stock_status == filters.stock_status
            )

        # Active status
        if filters.is_active is not None:
            query = query.filter(
                ProductListView.is_active == filters.is_active
            )

        # Brand filter
        if filters.brands:
            query = query.filter(
                ProductListView.brand.in_(filters.brands)
            )

        return query

    def _apply_sorting(self, query, sort_by: SortField, order: SortOrder):
        """Apply sorting to query"""
        sort_column = getattr(ProductListView, sort_by.value)

        if order == SortOrder.DESC:
            return query.order_by(sort_column.desc())
        else:
            return query.order_by(sort_column.asc())

    async def export_products(
        self,
        params: ProductListParams,
        format: str = 'csv',
        columns: List[str] = None
    ) -> bytes:
        """Export filtered products to specified format"""
        logger.info(f"Exporting products to {format}")

        # Get all products without pagination
        query = self.db.query(ProductListView)
        query = self._apply_filters(query, params.filters)
        query = self._apply_sorting(query, params.sort_by, params.sort_order)

        products = query.all()

        if format == 'csv':
            return self._export_csv(products, columns)
        elif format == 'excel':
            return self._export_excel(products, columns)
        elif format == 'pdf':
            return self._export_pdf(products, columns)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def save_filter(
        self,
        name: str,
        filters: ProductFilter,
        user_id: int,
        is_default: bool = False
    ) -> SavedFilter:
        """Save a filter configuration"""
        logger.info(f"Saving filter '{name}' for user {user_id}")

        # If setting as default, unset other defaults
        if is_default:
            self.db.query(SavedFilter).filter(
                SavedFilter.created_by == user_id,
                SavedFilter.is_default == True
            ).update({"is_default": False})

        saved_filter = SavedFilter(
            name=name,
            filter_json=filters.dict(),
            is_default=is_default,
            created_by=user_id
        )

        self.db.add(saved_filter)
        self.db.commit()

        return saved_filter

    async def get_filter_options(self) -> dict:
        """Get available filter options"""
        # Get unique brands
        brands = self.db.query(
            Product.brand
        ).filter(
            Product.brand.isnot(None)
        ).distinct().all()

        # Get price range
        price_stats = self.db.query(
            func.min(Product.sale_price).label('min_price'),
            func.max(Product.sale_price).label('max_price')
        ).first()

        return {
            "brands": [b[0] for b in brands if b[0]],
            "price_range": {
                "min": float(price_stats.min_price or 0),
                "max": float(price_stats.max_price or 0)
            }
        }
```

### 3. Web Interface with Advanced Features
```python
# app/web/products.py
@router.get("/", response_class=HTMLResponse)
async def product_list(
    request: Request,
    search: str = Query(None),
    category: int = Query(None),
    stock_status: str = Query("all"),
    sort_by: str = Query("name"),
    page: int = Query(1),
    view: str = Query("table"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Display product list with filters"""
    service = ProductService(db)

    # Build filter params
    filters = ProductFilter(
        search=search,
        category_ids=[category] if category else None,
        stock_status=stock_status
    )

    params = ProductListParams(
        filters=filters,
        sort_by=sort_by,
        page=page,
        view_mode=view
    )

    # Get products
    products, total = await service.get_product_list(params)

    # Get filter options
    filter_options = await service.get_filter_options()
    categories = await get_categories(db)

    # Calculate pagination
    total_pages = (total + params.page_size - 1) // params.page_size

    template = "products/index.html" if not request.headers.get("HX-Request") \
               else f"products/_{view}_view.html"

    return templates.TemplateResponse(
        template,
        {
            "request": request,
            "products": products,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "params": params,
            "categories": categories,
            "filter_options": filter_options,
            "user": current_user
        }
    )

@router.post("/bulk-update", response_class=HTMLResponse)
async def bulk_update_products(
    request: Request,
    product_ids: List[int] = Form(...),
    action: str = Form(...),
    value: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Handle bulk product updates"""
    service = ProductService(db)

    if action == "activate":
        await service.bulk_update_status(product_ids, True, current_user.id)
    elif action == "deactivate":
        await service.bulk_update_status(product_ids, False, current_user.id)
    elif action == "update_prices":
        # Parse price update params
        update_type = request.form.get("update_type")
        amount = Decimal(request.form.get("amount"))
        await service.bulk_update_prices(
            product_ids, update_type, amount, current_user.id
        )
    elif action == "export":
        format = request.form.get("format", "csv")
        data = await service.export_products(product_ids, format)
        return Response(
            content=data,
            media_type=f"application/{format}",
            headers={
                "Content-Disposition": f"attachment; filename=products.{format}"
            }
        )

    return HTMLResponse(
        headers={"HX-Trigger": "productsUpdated"}
    )

@router.get("/search", response_class=HTMLResponse)
async def search_products(
    request: Request,
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """Real-time product search endpoint"""
    service = ProductService(db)

    # Quick search with limit
    products = await service.quick_search(q, limit=10)

    return templates.TemplateResponse(
        "products/_search_results.html",
        {
            "request": request,
            "products": products,
            "query": q
        }
    )

@router.post("/save-filter", response_class=HTMLResponse)
async def save_filter(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Save current filter configuration"""
    # Extract filter params from form
    filters = ProductFilter(
        search=request.form.get("search"),
        category_ids=request.form.getlist("categories"),
        stock_status=request.form.get("stock_status", "all")
    )

    service = ProductService(db)
    saved = await service.save_filter(
        name, filters, current_user.id
    )

    return HTMLResponse(
        f'<div class="alert alert-success">Filter "{name}" saved</div>',
        headers={"HX-Trigger": "filterSaved"}
    )
```

## Definition of Done
- [ ] Product list view with table and card layouts
- [ ] Real-time search functionality
- [ ] Advanced filtering system
- [ ] Sorting options implemented
- [ ] Pagination with size options
- [ ] Bulk selection and operations
- [ ] Quick inline actions
- [ ] Export functionality (CSV, Excel, PDF)
- [ ] Saved filters feature
- [ ] Mobile responsive design
- [ ] Stock status indicators
- [ ] Performance optimizations (indexes, materialized view)
- [ ] Print label functionality
- [ ] Loading states and error handling
- [ ] Keyboard shortcuts for power users
- [ ] Unit tests for filtering and pagination
- [ ] Integration tests for all endpoints
- [ ] Performance tests with large datasets
- [ ] Documentation updated

## Testing Approach
1. **Unit Tests**: Filter logic, pagination, sorting algorithms
2. **Integration Tests**: List endpoints, bulk operations, exports
3. **UI Tests**: Filter interactions, view switching, search behavior
4. **Performance Tests**: Large datasets (10k+ products), complex filters
5. **Load Tests**: Concurrent users, real-time search load

## Dependencies
- STORY-012: Create Product - Must complete first
- STORY-013: Manage Categories - Needed for category filtering
- STORY-014: Edit Products - Needed for inline editing

## Notes
- Consider implementing infinite scroll as alternative to pagination
- May need Redis caching for frequently accessed lists
- Think about saved searches/smart lists feature
- Barcode scanner integration for quick search
- Consider GraphQL for flexible field selection
- Real-time updates when other users modify products

## Dev Notes
- Use database views for complex aggregations
- Implement query result caching with TTL
- Consider Elasticsearch for advanced search features
- Use indexes strategically to optimize common queries
- Implement lazy loading for images in card view
- Use WebSockets for real-time stock updates
- Consider server-side rendering for SEO if public catalog

## Tasks/Subtasks
- [ ] Create materialized view for list performance
- [ ] Add database indexes for common queries
- [ ] Implement filter schemas and validation
- [ ] Create paginated list service method
- [ ] Build advanced filter UI with Alpine.js
- [ ] Implement table view with sorting
- [ ] Create card view layout
- [ ] Add real-time search functionality
- [ ] Implement bulk selection system
- [ ] Create quick action dropdowns
- [ ] Add export functionality
- [ ] Implement saved filters
- [ ] Create mobile-responsive layouts
- [ ] Add keyboard shortcuts
- [ ] Write comprehensive tests
- [ ] Performance optimization
- [ ] Update documentation

---
## Change Log
- 2024-01-XX: Story created based on requirements
