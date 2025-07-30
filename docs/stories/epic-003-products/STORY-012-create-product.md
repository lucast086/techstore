# STORY-012: Create Product

## Story Metadata
- **Epic**: EPIC-003 - Product Management
- **Priority**: P0 - Critical
- **Estimate**: 13 points
- **Status**: IN PROGRESS (Core functionality implemented, pending Alpine.js, image upload, notifications)

## User Story
**As** María (Store Owner),
**I want to** add new products to my inventory catalog,
**So that** I can keep my product offerings up-to-date and track what I have available for sale.

## Acceptance Criteria
1. **Product Form Access**: Users can access the "Add Product" form from the main products page and dashboard
2. **Required Fields**: The form enforces required fields: name, SKU, category, purchase price, sales prices, and initial stock
3. **SKU Validation**: The system validates SKU uniqueness and format (alphanumeric, no spaces)
4. **Category Selection**: Users can select from existing categories or create a new one inline
5. **Price Validation**: Purchase and sales prices must be positive numbers with up to 2 decimal places
6. **Stock Management**: Initial stock quantity must be a non-negative integer
7. **Optional Fields**: Description, brand, model, barcode, minimum stock level, and location can be optionally provided
8. **Image Upload**: Users can upload up to 1 product images (JPG, PNG, max 5MB)
9. **Supplier Information**: Users can optionally link the product to one or more suppliers
10. **Tax Configuration**: Users can set tax rate (IVA) for the product, defaulting to 21%
11. **Success Feedback**: After successful creation, users see a success message and can choose to add another or view the product
12. **Error Handling**: Clear error messages for validation failures (duplicate SKU, invalid prices, etc.)
13. **Draft Saving**: Users can save products as draft (inactive) without requiring all fields
14. **Audit Trail**: System records who created the product and when
15. **Quick Actions**: After creation, users can immediately print labels or add more stock

## Technical Details

### File Structure
```
app/
├── models/
│   └── product.py          # Product and Category models
├── schemas/
│   └── product.py          # Pydantic schemas for validation
├── services/
│   └── product_service.py  # Business logic for products
├── api/v1/
│   └── products.py         # REST API endpoints
├── web/
│   └── products.py         # HTMX web routes
└── templates/
    └── products/
        ├── create.html     # Create product form
        └── _form.html      # Reusable form partial
```

### Database Schema
```sql
-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    brand VARCHAR(100),
    model VARCHAR(100),
    barcode VARCHAR(50),
    purchase_price DECIMAL(10,2) NOT NULL,
    first_sale_price DECIMAL(10,2) NOT NULL,
    second_sale_price DECIMAL(10,2) NOT NULL,
    third_sale_price DECIMAL(10,2) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 16.00,
    current_stock INTEGER DEFAULT 0,
    minimum_stock INTEGER DEFAULT 0,
    maximum_stock INTEGER,
    location VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product images table
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product suppliers table
CREATE TABLE product_suppliers (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    supplier_sku VARCHAR(100),
    is_preferred BOOLEAN DEFAULT false,
    last_purchase_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, supplier_id)
);
```

## Implementation Requirements

### 1. Pydantic Schemas
```python
# app/schemas/product.py
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True

class ProductBase(BaseModel):
    sku: str = Field(..., regex="^[A-Za-z0-9-]+$", max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: int
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    purchase_price: Decimal = Field(..., ge=0, decimal_places=2)
    first_sale_price: Decimal = Field(..., ge=0, decimal_places=2)
    second_sale_price: Decimal = Field(..., ge=0, decimal_places=2)
    third_sale_price: Decimal = Field(..., ge=0, decimal_places=2)
    tax_rate: Decimal = Field(default=Decimal("16.00"), ge=0, le=100)
    current_stock: int = Field(default=0, ge=0)
    minimum_stock: int = Field(default=0, ge=0)
    maximum_stock: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

    @validator('sale_price')
    def validate_sale_price(cls, v, values):
        if 'purchase_price' in values and v < values['purchase_price']:
            raise ValueError('Sale price cannot be less than purchase price')
        return v

class ProductCreate(ProductBase):
    supplier_ids: Optional[List[int]] = []
    images: Optional[List[str]] = []
```

### 2. Service Layer
```python
# app/services/product_service.py
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.product import Product, Category, ProductImage
from app.schemas.product import ProductCreate
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    async def create_product(
        self,
        product_data: ProductCreate,
        user_id: int
    ) -> Product:
        """Create a new product with images and supplier links"""
        logger.info(f"Creating product with SKU: {product_data.sku}")

        # Check if SKU already exists
        existing = self.db.query(Product).filter(
            Product.sku == product_data.sku
        ).first()
        if existing:
            logger.error(f"Product with SKU {product_data.sku} already exists")
            raise ValueError(f"Product with SKU {product_data.sku} already exists")

        # Create product
        product = Product(
            **product_data.dict(exclude={'supplier_ids', 'images'}),
            created_by=user_id
        )
        self.db.add(product)
        self.db.flush()

        # Add images
        for idx, image_url in enumerate(product_data.images or []):
            image = ProductImage(
                product_id=product.id,
                image_url=image_url,
                is_primary=(idx == 0),
                display_order=idx
            )
            self.db.add(image)

        # Link suppliers
        # TODO: Implement supplier linking

        self.db.commit()
        self.db.refresh(product)

        logger.info(f"Successfully created product: {product.id}")
        return product

    async def validate_category(self, category_id: int) -> bool:
        """Validate that category exists and is active"""
        category = self.db.query(Category).filter(
            Category.id == category_id,
            Category.is_active == True
        ).first()
        return category is not None
```

### 3. Web Interface
```python
# app/web/products.py
from fastapi import APIRouter, Depends, Request, Form, UploadFile
from fastapi.responses import HTMLResponse
from app.dependencies import get_current_user, get_db
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/create", response_class=HTMLResponse)
async def create_product_form(
    request: Request,
    current_user=Depends(get_current_user)
):
    """Display the create product form"""
    categories = await get_categories(request.state.db)
    return templates.TemplateResponse(
        "products/create.html",
        {
            "request": request,
            "categories": categories,
            "user": current_user
        }
    )

@router.post("/create", response_class=HTMLResponse)
async def create_product(
    request: Request,
    sku: str = Form(...),
    name: str = Form(...),
    category_id: int = Form(...),
    purchase_price: Decimal = Form(...),
    sale_price: Decimal = Form(...),
    current_stock: int = Form(0),
    # ... other form fields
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Handle product creation"""
    service = ProductService(db)

    try:
        product_data = ProductCreate(
            sku=sku,
            name=name,
            category_id=category_id,
            purchase_price=purchase_price,
            sale_price=sale_price,
            current_stock=current_stock,
            # ... map other fields
        )

        product = await service.create_product(
            product_data,
            current_user.id
        )

        # Return success partial with HX-Trigger for notifications
        return HTMLResponse(
            status_code=201,
            headers={
                "HX-Trigger": "productCreated",
                "HX-Redirect": f"/products/{product.id}"
            }
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "products/_form.html",
            {
                "request": request,
                "errors": {"general": str(e)},
                "values": product_data.dict()
            },
            status_code=400
        )
```

## Definition of Done
- [ ] Product model created with all required fields
- [ ] Category model created with hierarchical support
- [ ] Database migrations created and applied
- [ ] Pydantic schemas with validation rules implemented
- [ ] Product service with creation logic implemented
- [ ] Web routes for displaying and handling form submission
- [ ] HTML templates with Tailwind CSS styling
- [ ] Form includes all required and optional fields
- [ ] Client-side validation with Alpine.js
- [ ] Server-side validation with helpful error messages
- [ ] Image upload functionality working
- [ ] Success and error notifications implemented
- [ ] Unit tests for models and services (>90% coverage)
- [ ] Integration tests for web routes
- [ ] Manual testing of complete workflow
- [ ] Documentation updated

## Testing Approach
1. **Unit Tests**: Product model, validation logic, service methods
2. **Integration Tests**: API endpoints, form submission, database operations
3. **UI Tests**: Form interactions, validation feedback, image uploads
4. **Edge Cases**: Duplicate SKUs, invalid prices, large images, special characters

## Dependencies
- EPIC-001: Foundation (database, auth) - COMPLETED
- EPIC-002: Customer Management (for linking sales) - IN PROGRESS
- No blocking dependencies for basic product creation

## Notes
- Consider implementing barcode scanning in future iteration
- May need bulk import feature for initial catalog setup
- Image storage strategy needs to be decided (local vs cloud)
- Consider product variants (size, color) in future version

## Dev Notes
- Use decimal type for prices to avoid floating point issues
- Implement soft delete for products (is_active flag)
- Index on SKU and barcode fields for performance
- Consider full-text search on name and description
- Image optimization/resizing on upload
- Category hierarchy depth limit (suggest max 3 levels)

## Tasks/Subtasks
- [x] Create product and category models
- [x] Create database migrations
- [x] Implement Pydantic schemas with validation
- [x] Create product service class
- [x] Implement web routes for create form
- [x] Design HTML form with Tailwind CSS
- [ ] Add client-side validation with Alpine.js
- [ ] Implement image upload handling
- [ ] Create success/error notification system
- [x] Write unit tests for models and services
- [x] Write integration tests for web routes
- [ ] Manual testing of complete flow
- [ ] Update documentation

---
## Dev Agent Record

### Agent Model Used
claude-opus-4-20250514

### Debug Log References
- N/A

### Completion Notes
- Implemented product and category models with full relationships
- Created supplier model to support ProductSupplier relationship
- Generated database migrations for all models
- Implemented comprehensive Pydantic schemas with validation
- Created service layer with CategoryService and ProductService
- Implemented web routes for product listing, creation, and detail views
- Designed responsive HTML templates using Tailwind CSS
- Written unit tests for models and services with good coverage
- Created integration tests for web routes
- Pending: Alpine.js validation, image upload, notifications, manual testing

### File List
- src/app/models/product.py - Product, Category, ProductImage, ProductSupplier models
- src/app/models/supplier.py - Supplier model
- src/app/schemas/product.py - Product-related Pydantic schemas
- src/app/schemas/supplier.py - Supplier schemas
- src/app/schemas/base.py - Base schemas for common functionality
- src/app/services/product_service.py - Product and Category services
- src/app/web/products.py - Product web routes (HTMX)
- src/app/templates/products/create.html - Product creation form
- src/app/templates/products/_form.html - Reusable form partial
- src/app/templates/products/list.html - Product list view
- src/app/templates/products/detail.html - Product detail view
- src/app/templates/products/_search_results.html - Search results partial
- tests/unit/models/test_product.py - Product model unit tests
- tests/unit/services/test_product_service.py - Product service unit tests
- tests/integration/web/test_products.py - Product web routes integration tests
- alembic/versions/7d1c1d54160f_add_product_category_and_supplier_models.py - Database migration

---
## Change Log
- 2024-01-XX: Story created based on requirements
- 2025-07-30: Implemented core product functionality (models, services, web routes, templates, tests)
