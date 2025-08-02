# STORY-063: Purchase Order Management

## 📋 Story Details
- **Epic**: EPIC-006 (Cash Management and Closings)
- **Priority**: HIGH
- **Estimate**: 2 days
- **Status**: TODO

## 🎯 User Story
**As** Carlos or María,
**I want** to register supplier purchases with detailed items,
**So that** inventory is automatically updated and costs are properly tracked.

## ✅ Acceptance Criteria
1. [ ] Purchase form with supplier details:
   - Supplier name (autocomplete from previous)
   - Invoice number
   - Date
   - Payment terms
2. [ ] Line items with:
   - Product search (by code/name)
   - Option to create new product if not found
   - Quantity
   - Unit cost
   - Line total (auto-calculated)
3. [ ] Summary section:
   - Subtotal
   - Tax amount
   - Total amount
4. [ ] On save:
   - Create expense entry for total amount (category: "Supplier Purchases")
   - Update inventory quantities for all items
   - Generate purchase record
5. [ ] Purchase history with search and filters

## 🔧 Technical Tasks
### 1. Create Database Models (AC: 1, 2, 3)
- [ ] Create `Purchase` model in `src/app/models/purchase.py`
  - Fields: id, supplier_name, invoice_number, purchase_date, payment_terms, subtotal, tax_amount, total_amount, notes, created_by
  - Unique constraint on (supplier_name, invoice_number)
  - Index on purchase_date, supplier_name
- [ ] Create `PurchaseItem` model in same file
  - Fields: id, purchase_id, product_id, quantity, unit_cost, line_total
  - Foreign keys: purchase_id, product_id
  - Relationship with Product model

### 2. Create Pydantic Schemas (AC: 1, 2, 3)
- [ ] Create schemas in `src/app/schemas/purchase.py`
  - `PurchaseItemCreate`: product_id, quantity, unit_cost
  - `PurchaseCreate`: supplier details + list of items
  - `PurchaseResponse`: Complete purchase with items
  - `PurchaseListResponse`: Summary for list view
  - `PurchaseFilter`: Date range, supplier filters

### 3. Implement CRUD Operations (AC: 4, 5)
- [ ] Create CRUD in `src/app/crud/purchase.py`
  - `create_purchase()`: Create purchase with items
  - `get_purchases()`: List with filters
  - `get_purchase_by_id()`: Full details
  - `get_suppliers()`: Autocomplete list
  - `search_purchases()`: By supplier, date, invoice

### 4. Product Integration (AC: 2)
- [ ] Extend product CRUD for purchase integration
  - `search_products_for_purchase()`: Product lookup
  - `create_product_from_purchase()`: Quick product creation
  - Check if existing Product model supports this

### 5. Implement Service Layer (AC: 4)
- [ ] Create service in `src/app/services/purchase_service.py`
  - `create_purchase()`: Orchestrate full purchase process
  - `calculate_totals()`: Compute subtotal, tax, total
  - `update_inventory()`: Call inventory service
  - `create_expense_entry()`: Create corresponding expense
  - `get_supplier_suggestions()`: Autocomplete data

### 6. Inventory Integration (AC: 4)
- [ ] Modify inventory/product service
  - Add method to update stock from purchase
  - Update last purchase price
  - Handle new product creation
  - Log stock movements

### 7. Expense Integration (AC: 4)
- [ ] Modify expense service
  - Auto-create expense for "Supplier Purchases" category
  - Link expense to purchase record
  - Ensure category exists (from STORY-061)

### 8. Create API Endpoints (AC: 1, 5)
- [ ] Add routes to `src/app/api/v1/purchases.py`
  - `POST /purchases`: Create new purchase
  - `GET /purchases`: List with filters
  - `GET /purchases/{id}`: Get purchase details
  - `GET /purchases/suppliers`: Supplier autocomplete
  - `POST /purchases/products`: Create product on-the-fly

### 9. Create Web Routes and Templates (AC: 1, 2, 3, 5)
- [ ] Add routes to `src/app/web/purchases.py`
  - Route for purchase form
  - Route for purchase list
  - HTMX endpoints for product search, calculations
- [ ] Create templates in `src/app/templates/purchases/`
  - `purchase_form.html`: Multi-section form
  - `purchase_list.html`: History with filters
  - `_purchase_item.html`: Line item partial
  - `_product_search.html`: Product lookup modal

### 10. Write Tests
- [ ] Unit tests for purchase models
- [ ] Service tests for complex workflows
- [ ] API tests for all endpoints
- [ ] Integration tests with inventory updates
- [ ] Test expense auto-creation
- [ ] Test product creation flow

## 📝 Dev Notes

### Data Models
**Purchase Models** [Source: architecture/source-tree.md#models]
- Two related models: Purchase (header) and PurchaseItem (lines)
- Follow existing patterns from Sale/SaleItem models
- Use SQLAlchemy relationships and cascades

### Previous Story Dependencies
- STORY-061: ExpenseCategory model with "Supplier Purchases" category
- STORY-062: Expense model for auto-created expenses
- Existing Product model from Epic 003

### Complex Workflow [Source: architecture/coding-standards.md#service-layer-pattern]
- Purchase creation involves multiple services:
  1. Purchase service (main orchestrator)
  2. Product service (inventory updates)
  3. Expense service (expense creation)
- Use database transactions for atomicity

### Product Integration
**Existing Product Model** [Source: Current codebase]
- Must check current Product model capabilities
- May need to add fields: last_purchase_price, supplier_name
- Stock updates should use existing inventory system

### Frontend Complexity [Source: architecture/tech-stack.md#frontend]
- Dynamic line item management with HTMX
- Product search with autocomplete
- Real-time total calculations
- Responsive design for mobile data entry

### Security Requirements [Source: architecture/coding-standards.md#security-protocols]
- Role-based access (who can create purchases?)
- Validate product references exist
- Prevent negative quantities/prices
- Audit trail for inventory changes

### Transaction Management [Source: architecture/coding-standards.md#database-standards]
- Use database transactions for:
  1. Purchase creation
  2. Inventory updates
  3. Expense creation
- Rollback on any failure

### Testing Complexity
- Mock inventory service interactions
- Test transaction rollback scenarios
- Verify expense auto-creation
- Test product creation workflow

## 🧪 Testing Requirements
- Models with complex relationships
- Service integration tests
- Transaction rollback tests
- Inventory update verification
- Expense creation validation
- API workflow tests
- Error handling for failed integrations

## 📋 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-15 | 1.0 | Initial story creation | Bob (Scrum Master) |

## 🤖 Dev Agent Record
*This section will be populated by the development agent during implementation*

### Agent Model Used
*To be filled by dev agent*

### Debug Log References
*To be filled by dev agent*

### Completion Notes
*To be filled by dev agent*

### File List
*To be filled by dev agent*

## ✅ QA Results
*To be filled by QA agent*
