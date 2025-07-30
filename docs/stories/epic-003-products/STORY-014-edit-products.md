# STORY-014: Edit Products

## Story Metadata
- **Epic**: EPIC-003 - Product Management
- **Priority**: P0 - Critical
- **Estimate**: 8 points
- **Status**: TODO

## User Story
**As** María (Store Owner),
**I want to** edit existing product information including prices, stock levels, and details,
**So that** I can keep my inventory accurate and respond to market changes quickly.

## Acceptance Criteria
1. **Edit Access**: Users can access edit form from product list, product detail page, or by scanning barcode
2. **Form Pre-population**: Edit form displays all current product information
3. **Field Updates**: All product fields can be modified except SKU (immutable after creation)
4. **Price History**: System tracks price changes with timestamp and user who made the change
5. **Stock Adjustment**: Stock changes require reason selection (sale, purchase, adjustment, damage, return)
6. **Bulk Price Update**: Option to update prices by percentage or fixed amount across multiple products
7. **Category Change**: Products can be moved to different categories with validation
8. **Image Management**: Add, remove, reorder product images; set primary image
9. **Supplier Updates**: Add/remove supplier links, update supplier-specific information
10. **Audit Trail**: All changes are logged with before/after values, timestamp, and user
11. **Validation**: Same validation rules as creation, plus business rules (e.g., minimum margin)
12. **Quick Actions**: Shortcuts for common updates (adjust stock, change price, toggle status)
13. **Comparison View**: Show original vs modified values before saving
14. **Undo Changes**: Option to revert unsaved changes while editing
15. **Concurrent Edit Protection**: Warning if another user modified the product while editing

## Technical Details

### File Structure
```
app/
├── models/
│   ├── product.py          # Add audit fields
│   └── audit.py            # Product audit log model
├── schemas/
│   └── product.py          # Update schemas
├── services/
│   ├── product_service.py  # Enhanced with edit logic
│   └── audit_service.py    # Audit trail service
├── api/v1/
│   └── products.py         # Edit endpoints
├── web/
│   └── products.py         # Edit routes
└── templates/
    └── products/
        ├── edit.html       # Edit form
        ├── _quick_edit.html # Quick edit modal
        └── _diff_view.html  # Changes comparison
```

### Database Schema Additions
```sql
-- Product audit log table
CREATE TABLE product_audit_log (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    field_name VARCHAR(50) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_type VARCHAR(20) NOT NULL, -- 'update', 'price_change', 'stock_adjustment'
    change_reason VARCHAR(100),
    changed_by INTEGER NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock movements table
CREATE TABLE stock_movements (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    movement_type VARCHAR(20) NOT NULL, -- 'purchase', 'sale', 'adjustment', 'damage', 'return'
    quantity INTEGER NOT NULL, -- positive for in, negative for out
    old_stock INTEGER NOT NULL,
    new_stock INTEGER NOT NULL,
    reference_type VARCHAR(20), -- 'sale', 'purchase_order', 'manual'
    reference_id INTEGER,
    notes TEXT,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price history table
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    price_type VARCHAR(20) NOT NULL, -- 'purchase', 'sale'
    old_price DECIMAL(10,2) NOT NULL,
    new_price DECIMAL(10,2) NOT NULL,
    change_percentage DECIMAL(5,2),
    effective_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by INTEGER NOT NULL REFERENCES users(id),
    change_reason VARCHAR(200)
);

-- Add version/lock fields to products
ALTER TABLE products ADD COLUMN
    version INTEGER DEFAULT 1,
    locked_by INTEGER REFERENCES users(id),
    locked_at TIMESTAMP;

-- Indexes for audit queries
CREATE INDEX idx_audit_product_id ON product_audit_log(product_id);
CREATE INDEX idx_audit_changed_at ON product_audit_log(changed_at);
CREATE INDEX idx_stock_movements_product ON stock_movements(product_id);
CREATE INDEX idx_price_history_product ON price_history(product_id);
```

## Implementation Requirements

### 1. Enhanced Product Schemas
```python
# app/schemas/product.py
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class StockMovementType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    DAMAGE = "damage"
    RETURN = "return"

class PriceUpdateType(str, Enum):
    FIXED_AMOUNT = "fixed_amount"
    PERCENTAGE = "percentage"

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    purchase_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    minimum_stock: Optional[int] = Field(None, ge=0)
    maximum_stock: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    version: int  # For optimistic locking

class StockAdjustment(BaseModel):
    product_id: int
    quantity: int  # positive or negative
    movement_type: StockMovementType
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None

class PriceUpdate(BaseModel):
    product_ids: List[int]
    update_type: PriceUpdateType
    purchase_price_value: Optional[Decimal] = None
    sale_price_value: Optional[Decimal] = None
    reason: Optional[str] = None

class ProductEditForm(ProductUpdate):
    """Form data with current values for comparison"""
    current_values: Dict[str, Any]
    stock_adjustment: Optional[StockAdjustment] = None

class ProductChange(BaseModel):
    field: str
    old_value: Any
    new_value: Any

class ProductDiff(BaseModel):
    product_id: int
    changes: List[ProductChange]
    has_changes: bool
```

### 2. Enhanced Product Service
```python
# app/services/product_service.py
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.product import Product, ProductAuditLog, StockMovement
from app.schemas.product import ProductUpdate, StockAdjustment, ProductDiff
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    async def update_product(
        self,
        product_id: int,
        update_data: ProductUpdate,
        user_id: int
    ) -> Product:
        """Update product with audit trail and optimistic locking"""
        logger.info(f"Updating product {product_id}")

        # Get product with lock
        product = self.db.query(Product).filter(
            Product.id == product_id
        ).with_for_update().first()

        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Check version for concurrent update protection
        if product.version != update_data.version:
            raise ValueError(
                "Product has been modified by another user. Please refresh and try again."
            )

        # Track changes for audit
        changes = self._get_changes(product, update_data)

        # Update fields
        for field, value in update_data.dict(
            exclude_unset=True,
            exclude={'version'}
        ).items():
            if value is not None:
                old_value = getattr(product, field)
                if old_value != value:
                    setattr(product, field, value)

                    # Special handling for price changes
                    if field in ['purchase_price', 'sale_price']:
                        await self._record_price_change(
                            product_id, field, old_value, value, user_id
                        )

        # Increment version
        product.version += 1
        product.updated_at = datetime.utcnow()

        # Record audit log
        for change in changes:
            audit_entry = ProductAuditLog(
                product_id=product_id,
                field_name=change.field,
                old_value=str(change.old_value),
                new_value=str(change.new_value),
                change_type='update',
                changed_by=user_id
            )
            self.db.add(audit_entry)

        self.db.commit()
        self.db.refresh(product)

        logger.info(f"Successfully updated product {product_id}")
        return product

    async def adjust_stock(
        self,
        adjustment: StockAdjustment,
        user_id: int
    ) -> Product:
        """Adjust product stock with movement tracking"""
        logger.info(
            f"Adjusting stock for product {adjustment.product_id}: "
            f"{adjustment.quantity} ({adjustment.movement_type})"
        )

        # Get product with lock
        product = self.db.query(Product).filter(
            Product.id == adjustment.product_id
        ).with_for_update().first()

        if not product:
            raise ValueError(f"Product {adjustment.product_id} not found")

        old_stock = product.current_stock
        new_stock = old_stock + adjustment.quantity

        if new_stock < 0:
            raise ValueError(
                f"Insufficient stock. Current: {old_stock}, "
                f"Requested change: {adjustment.quantity}"
            )

        # Update stock
        product.current_stock = new_stock

        # Record movement
        movement = StockMovement(
            product_id=adjustment.product_id,
            movement_type=adjustment.movement_type,
            quantity=adjustment.quantity,
            old_stock=old_stock,
            new_stock=new_stock,
            reference_type=adjustment.reference_type,
            reference_id=adjustment.reference_id,
            notes=adjustment.notes,
            created_by=user_id
        )
        self.db.add(movement)

        # Check stock levels
        if new_stock <= product.minimum_stock:
            logger.warning(
                f"Product {product.id} stock ({new_stock}) "
                f"at or below minimum ({product.minimum_stock})"
            )
            # TODO: Send notification

        self.db.commit()
        self.db.refresh(product)

        return product

    async def bulk_update_prices(
        self,
        update_request: PriceUpdate,
        user_id: int
    ) -> List[Product]:
        """Update prices for multiple products"""
        logger.info(
            f"Bulk updating prices for {len(update_request.product_ids)} products"
        )

        products = self.db.query(Product).filter(
            Product.id.in_(update_request.product_ids)
        ).with_for_update().all()

        updated_products = []

        for product in products:
            if update_request.purchase_price_value is not None:
                old_price = product.purchase_price
                if update_request.update_type == PriceUpdateType.FIXED_AMOUNT:
                    new_price = update_request.purchase_price_value
                else:  # percentage
                    new_price = old_price * (
                        1 + update_request.purchase_price_value / 100
                    )

                product.purchase_price = new_price
                await self._record_price_change(
                    product.id, 'purchase_price',
                    old_price, new_price, user_id,
                    update_request.reason
                )

            if update_request.sale_price_value is not None:
                old_price = product.sale_price
                if update_request.update_type == PriceUpdateType.FIXED_AMOUNT:
                    new_price = update_request.sale_price_value
                else:  # percentage
                    new_price = old_price * (
                        1 + update_request.sale_price_value / 100
                    )

                product.sale_price = new_price
                await self._record_price_change(
                    product.id, 'sale_price',
                    old_price, new_price, user_id,
                    update_request.reason
                )

            product.version += 1
            updated_products.append(product)

        self.db.commit()
        return updated_products

    def _get_changes(
        self,
        product: Product,
        update_data: ProductUpdate
    ) -> List[ProductChange]:
        """Compare current and new values to identify changes"""
        changes = []

        for field, new_value in update_data.dict(
            exclude_unset=True,
            exclude={'version'}
        ).items():
            if new_value is not None:
                old_value = getattr(product, field)
                if old_value != new_value:
                    changes.append(ProductChange(
                        field=field,
                        old_value=old_value,
                        new_value=new_value
                    ))

        return changes

    async def get_product_history(
        self,
        product_id: int,
        limit: int = 50
    ) -> List[ProductAuditLog]:
        """Get audit history for a product"""
        return self.db.query(ProductAuditLog).filter(
            ProductAuditLog.product_id == product_id
        ).order_by(
            ProductAuditLog.changed_at.desc()
        ).limit(limit).all()
```

### 3. Web Interface with Edit Forms
```python
# app/web/products.py
@router.get("/{product_id}/edit", response_class=HTMLResponse)
async def edit_product_form(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Display product edit form"""
    service = ProductService(db)
    product = await service.get_product(product_id)
    categories = await get_categories(db)

    return templates.TemplateResponse(
        "products/edit.html",
        {
            "request": request,
            "product": product,
            "categories": categories,
            "user": current_user
        }
    )

@router.post("/{product_id}/edit", response_class=HTMLResponse)
async def update_product(
    request: Request,
    product_id: int,
    name: str = Form(...),
    category_id: int = Form(...),
    purchase_price: Decimal = Form(...),
    sale_price: Decimal = Form(...),
    version: int = Form(...),
    # ... other form fields
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Handle product update"""
    service = ProductService(db)

    try:
        update_data = ProductUpdate(
            name=name,
            category_id=category_id,
            purchase_price=purchase_price,
            sale_price=sale_price,
            version=version,
            # ... map other fields
        )

        product = await service.update_product(
            product_id,
            update_data,
            current_user.id
        )

        # Return success message
        return HTMLResponse(
            "<div class='alert alert-success'>Product updated successfully</div>",
            headers={"HX-Trigger": "productUpdated"}
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "products/edit.html",
            {
                "request": request,
                "product": product,
                "errors": {"general": str(e)},
                "values": update_data.dict()
            },
            status_code=400
        )

@router.post("/{product_id}/quick-stock", response_class=HTMLResponse)
async def quick_stock_adjustment(
    request: Request,
    product_id: int,
    quantity: int = Form(...),
    movement_type: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Quick stock adjustment from product list"""
    service = ProductService(db)

    adjustment = StockAdjustment(
        product_id=product_id,
        quantity=quantity,
        movement_type=movement_type,
        notes=notes
    )

    product = await service.adjust_stock(adjustment, current_user.id)

    # Return updated stock badge
    return HTMLResponse(
        f'<span class="badge">{product.current_stock}</span>',
        headers={"HX-Trigger": "stockUpdated"}
    )
```

## Definition of Done
- [ ] Product update functionality with all fields editable (except SKU)
- [ ] Audit log model and tracking implemented
- [ ] Stock adjustment with movement tracking
- [ ] Price history tracking with reasons
- [ ] Optimistic locking for concurrent edit protection
- [ ] Edit form with current value display
- [ ] Quick edit modals for common operations
- [ ] Bulk price update interface
- [ ] Changes comparison view before saving
- [ ] Image management in edit form
- [ ] Validation with helpful error messages
- [ ] Success/error notifications
- [ ] Unit tests for all update operations
- [ ] Integration tests for edit workflows
- [ ] UI tests for form interactions
- [ ] Performance tested with large catalogs
- [ ] Documentation updated

## Testing Approach
1. **Unit Tests**: Update logic, audit tracking, version control
2. **Integration Tests**: Edit endpoints, stock adjustments, bulk updates
3. **UI Tests**: Form validation, quick edits, image management
4. **Concurrency Tests**: Simultaneous edits, version conflicts
5. **Edge Cases**: Large updates, decimal precision, stock going negative

## Dependencies
- STORY-012: Create Product (must exist to edit) - Must complete first
- STORY-013: Manage Categories (for category changes) - Can develop in parallel

## Notes
- Consider implementing field-level permissions in future
- May need approval workflow for price changes above threshold
- Think about batch editing UI for seasonal updates
- Mobile-friendly quick edit interface important
- Consider barcode scanner integration for quick stock updates

## Dev Notes
- Use database transactions for all updates
- Implement row-level locking to prevent conflicts
- Store monetary values as DECIMAL to maintain precision
- Index audit tables for efficient history queries
- Consider implementing event sourcing for complex scenarios
- Add database triggers for updated_at timestamp

## Tasks/Subtasks
- [ ] Create audit log and related models
- [ ] Add version field to product model
- [ ] Implement product update service method
- [ ] Add stock adjustment functionality
- [ ] Create price history tracking
- [ ] Build edit form with field comparison
- [ ] Implement quick edit modals
- [ ] Add bulk price update interface
- [ ] Create image management UI
- [ ] Implement optimistic locking
- [ ] Add comprehensive validation
- [ ] Write unit tests for services
- [ ] Write integration tests for endpoints
- [ ] Test concurrent edit scenarios
- [ ] Update documentation

---
## Change Log
- 2024-01-XX: Story created based on requirements
