# STORY-013: Manage Categories

## Story Metadata
- **Epic**: EPIC-003 - Product Management
- **Priority**: P0 - Critical
- **Estimate**: 8 points
- **Status**: TODO

## User Story
**As** Carlos (Store Manager),
**I want to** organize products into hierarchical categories,
**So that** I can maintain a well-structured catalog that makes it easy for staff to find and manage products.

## Acceptance Criteria
1. **Categories List View**: Display all categories in a tree structure showing parent-child relationships
2. **Create Category**: Users can create new categories with name and optional description
3. **Hierarchical Structure**: Support up to 3 levels of category nesting (e.g., Electronics > Computers > Laptops)
4. **Edit Category**: Users can edit category name, description, and parent assignment
5. **Category Status**: Categories can be marked as active/inactive without deletion
6. **Move Category**: Users can change a category's parent, moving all subcategories with it
7. **Product Count**: Display number of products in each category (including subcategories)
8. **Delete Protection**: Prevent deletion of categories containing products or subcategories
9. **Search Categories**: Quick search functionality to find categories by name
10. **Bulk Actions**: Select multiple categories for bulk status changes
11. **Import/Export**: Export category structure to CSV, import from CSV template
12. **Category Icons**: Optional icon/emoji assignment for visual identification
13. **Validation**: Prevent circular references and duplicate names at same level
14. **Breadcrumb Navigation**: Show category path in UI (e.g., Electronics > Computers > Laptops)
15. **Drag and Drop**: Reorder categories within the same parent level

## Technical Details

### File Structure
```
app/
├── models/
│   └── product.py          # Category model enhancements
├── schemas/
│   └── category.py         # Category-specific schemas
├── services/
│   └── category_service.py # Category business logic
├── api/v1/
│   └── categories.py       # REST API endpoints
├── web/
│   └── categories.py       # HTMX web routes
└── templates/
    └── categories/
        ├── index.html      # Categories list/tree view
        ├── create.html     # Create category form
        ├── edit.html       # Edit category form
        └── _tree_node.html # Recursive tree node partial
```

### Database Schema Enhancements
```sql
-- Add fields to categories table
ALTER TABLE categories ADD COLUMN IF NOT EXISTS
    icon VARCHAR(50),
    display_order INTEGER DEFAULT 0,
    full_path VARCHAR(500),  -- Materialized path for efficient queries
    level INTEGER DEFAULT 0;

-- Add indexes for performance
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_path ON categories(full_path);
CREATE INDEX idx_categories_active ON categories(is_active);

-- Create view for category statistics
CREATE VIEW category_stats AS
SELECT
    c.id,
    c.name,
    c.full_path,
    COUNT(DISTINCT p.id) as direct_product_count,
    COUNT(DISTINCT p2.id) as total_product_count,
    COUNT(DISTINCT sub.id) as subcategory_count
FROM categories c
LEFT JOIN products p ON p.category_id = c.id
LEFT JOIN categories sub ON sub.parent_id = c.id
LEFT JOIN products p2 ON p2.category_id IN (
    SELECT id FROM categories
    WHERE full_path LIKE c.full_path || '%'
)
GROUP BY c.id, c.name, c.full_path;
```

## Implementation Requirements

### 1. Enhanced Category Schema
```python
# app/schemas/category.py
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = Field(None, max_length=50)
    display_order: int = Field(default=0)
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryNode(CategoryBase):
    id: int
    level: int
    full_path: str
    direct_product_count: int = 0
    total_product_count: int = 0
    children: List['CategoryNode'] = []

    class Config:
        from_attributes = True

CategoryNode.model_rebuild()  # For recursive model

class CategoryMove(BaseModel):
    category_id: int
    new_parent_id: Optional[int] = None
    new_position: int = 0

class CategoryBulkUpdate(BaseModel):
    category_ids: List[int]
    is_active: Optional[bool] = None
```

### 2. Category Service
```python
# app/services/category_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Category, Product
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryNode
import logging

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.max_depth = 3

    async def get_category_tree(self) -> List[CategoryNode]:
        """Get all categories organized in tree structure"""
        logger.info("Fetching category tree")

        # Get all categories with stats
        categories = self.db.query(
            Category,
            func.count(Product.id).label('product_count')
        ).outerjoin(
            Product, Category.id == Product.category_id
        ).group_by(Category.id).all()

        # Build tree structure
        category_map = {}
        roots = []

        for cat, count in categories:
            node = CategoryNode(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                parent_id=cat.parent_id,
                icon=cat.icon,
                display_order=cat.display_order,
                is_active=cat.is_active,
                level=cat.level,
                full_path=cat.full_path,
                direct_product_count=count,
                children=[]
            )
            category_map[cat.id] = node

            if cat.parent_id is None:
                roots.append(node)

        # Link children to parents
        for cat, _ in categories:
            if cat.parent_id and cat.parent_id in category_map:
                category_map[cat.parent_id].children.append(
                    category_map[cat.id]
                )

        # Sort by display order
        self._sort_tree(roots)
        return roots

    async def create_category(
        self,
        category_data: CategoryCreate
    ) -> Category:
        """Create a new category"""
        logger.info(f"Creating category: {category_data.name}")

        # Validate parent and depth
        if category_data.parent_id:
            parent = await self._get_category(category_data.parent_id)
            if parent.level >= self.max_depth - 1:
                raise ValueError(
                    f"Maximum nesting depth ({self.max_depth}) exceeded"
                )
            level = parent.level + 1
            full_path = f"{parent.full_path}/{category_data.name}"
        else:
            level = 0
            full_path = category_data.name

        # Check for duplicate names at same level
        existing = self.db.query(Category).filter(
            Category.name == category_data.name,
            Category.parent_id == category_data.parent_id
        ).first()
        if existing:
            raise ValueError(
                f"Category '{category_data.name}' already exists at this level"
            )

        # Create category
        category = Category(
            **category_data.dict(),
            level=level,
            full_path=full_path
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        logger.info(f"Created category: {category.id}")
        return category

    async def update_category(
        self,
        category_id: int,
        category_data: CategoryUpdate
    ) -> Category:
        """Update a category"""
        logger.info(f"Updating category: {category_id}")

        category = await self._get_category(category_id)

        # Handle parent change
        if category_data.parent_id is not None and \
           category_data.parent_id != category.parent_id:
            await self._validate_move(category, category_data.parent_id)
            await self._move_category(category, category_data.parent_id)

        # Update fields
        for field, value in category_data.dict(exclude_unset=True).items():
            if field != 'parent_id':  # Already handled
                setattr(category, field, value)

        # Update path if name changed
        if category_data.name and category_data.name != category.name:
            await self._update_paths(category)

        self.db.commit()
        self.db.refresh(category)

        logger.info(f"Updated category: {category.id}")
        return category

    async def delete_category(self, category_id: int) -> bool:
        """Delete a category (soft delete)"""
        logger.info(f"Deleting category: {category_id}")

        category = await self._get_category(category_id)

        # Check for products
        product_count = self.db.query(Product).filter(
            Product.category_id == category_id
        ).count()
        if product_count > 0:
            raise ValueError(
                f"Cannot delete category with {product_count} products"
            )

        # Check for subcategories
        subcat_count = self.db.query(Category).filter(
            Category.parent_id == category_id
        ).count()
        if subcat_count > 0:
            raise ValueError(
                f"Cannot delete category with {subcat_count} subcategories"
            )

        category.is_active = False
        self.db.commit()

        logger.info(f"Soft deleted category: {category_id}")
        return True

    async def _validate_move(
        self,
        category: Category,
        new_parent_id: Optional[int]
    ):
        """Validate category move operation"""
        if new_parent_id is None:
            return  # Moving to root is always valid

        # Check for circular reference
        current = await self._get_category(new_parent_id)
        while current:
            if current.id == category.id:
                raise ValueError("Circular reference detected")
            current = await self._get_category(current.parent_id) \
                     if current.parent_id else None

        # Check depth
        new_parent = await self._get_category(new_parent_id)
        if new_parent.level + self._get_subtree_depth(category) >= self.max_depth:
            raise ValueError("Move would exceed maximum depth")

    def _sort_tree(self, nodes: List[CategoryNode]):
        """Recursively sort tree nodes by display_order"""
        nodes.sort(key=lambda x: (x.display_order, x.name))
        for node in nodes:
            if node.children:
                self._sort_tree(node.children)

    async def _get_category(self, category_id: Optional[int]) -> Optional[Category]:
        """Get category by ID"""
        if category_id is None:
            return None
        category = self.db.query(Category).filter(
            Category.id == category_id
        ).first()
        if not category:
            raise ValueError(f"Category {category_id} not found")
        return category
```

### 3. Web Interface with Tree View
```python
# app/web/categories.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_class=HTMLResponse)
async def categories_index(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Display category tree view"""
    service = CategoryService(db)
    tree = await service.get_category_tree()

    return templates.TemplateResponse(
        "categories/index.html",
        {
            "request": request,
            "category_tree": tree,
            "user": current_user
        }
    )

@router.post("/reorder", response_class=HTMLResponse)
async def reorder_categories(
    request: Request,
    category_id: int = Form(...),
    new_position: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Handle drag-and-drop reordering"""
    service = CategoryService(db)
    await service.reorder_category(category_id, new_position)

    # Return updated tree partial
    tree = await service.get_category_tree()
    return templates.TemplateResponse(
        "categories/_tree.html",
        {"request": request, "category_tree": tree}
    )
```

## Definition of Done
- [ ] Category model enhanced with hierarchy support
- [ ] Database migrations for new fields and indexes
- [ ] Category service with full CRUD operations
- [ ] Tree view UI with expand/collapse functionality
- [ ] Create/edit forms with parent selection
- [ ] Drag-and-drop reordering implemented
- [ ] Product count display at each level
- [ ] Search functionality with highlighting
- [ ] Bulk operations UI and backend
- [ ] Import/export functionality
- [ ] Validation for circular references and depth
- [ ] Proper error handling and user feedback
- [ ] Unit tests for all service methods
- [ ] Integration tests for web routes
- [ ] UI tests for tree interactions
- [ ] Performance tested with 1000+ categories
- [ ] Documentation updated

## Testing Approach
1. **Unit Tests**: Category hierarchy logic, path calculations, validations
2. **Integration Tests**: CRUD operations, tree building, move operations
3. **UI Tests**: Tree interactions, drag-and-drop, form submissions
4. **Performance Tests**: Large category trees, deep nesting, bulk operations
5. **Edge Cases**: Circular references, max depth, special characters in names

## Dependencies
- STORY-012: Create Product (needs categories) - Can develop in parallel
- No external blocking dependencies

## Notes
- Consider caching category tree for performance
- May need to implement lazy loading for very large trees
- Full-text search on category names and descriptions
- Consider category templates for common structures
- Think about category-specific attributes in future

## Dev Notes
- Use materialized path pattern for efficient tree queries
- Implement recursive CTE for complex tree operations
- Consider using MPTT (Modified Preorder Tree Traversal) if performance issues
- Add database triggers to maintain path consistency
- Use transactions for all tree modification operations
- Implement optimistic locking for concurrent updates

## Tasks/Subtasks
- [ ] Enhance category model with hierarchy fields
- [ ] Create database migrations with indexes
- [ ] Implement category service with tree operations
- [ ] Create tree view template with Tailwind CSS
- [ ] Implement expand/collapse with Alpine.js
- [ ] Add drag-and-drop with SortableJS
- [ ] Create category forms with parent selector
- [ ] Implement search with real-time filtering
- [ ] Add bulk operations UI and backend
- [ ] Implement import/export functionality
- [ ] Write comprehensive unit tests
- [ ] Write integration tests
- [ ] Performance testing and optimization
- [ ] Update documentation

---
## Change Log
- 2024-01-XX: Story created based on requirements
