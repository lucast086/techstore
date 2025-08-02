# STORY-064: Automatic Inventory Updates from Purchases

## 📋 Story Details
- **Epic**: EPIC-006 (Cash Management and Closings)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** the system,
**I want** to automatically update product inventory from purchases,
**So that** stock levels remain accurate without manual intervention.

## ✅ Acceptance Criteria
1. [ ] When purchase order is saved:
   - Add purchased quantities to product stock
   - Update last purchase price
   - Calculate new average cost
2. [ ] For new products created during purchase:
   - Create product with provided details
   - Set initial stock to purchased quantity
   - Set cost to purchase price
3. [ ] Stock movement history shows purchase entries
4. [ ] Inventory reports reflect purchase updates

## 🔧 Technical Tasks
### 1. Extend Product Model (AC: 1, 2)
- [ ] Add fields to existing Product model in `src/app/models/product.py`
  - last_purchase_price: Decimal field
  - average_cost: Decimal field (calculated)
  - last_purchase_date: DateTime field
  - Ensure stock_quantity field exists and is updatable

### 2. Create Stock Movement Tracking (AC: 3)
- [ ] Create `StockMovement` model in `src/app/models/inventory.py`
  - Fields: id, product_id, movement_type, quantity, unit_cost, reference_type, reference_id, notes, created_at, created_by
  - movement_type: ENUM (purchase, sale, adjustment, return)
  - reference_type: ENUM (purchase, sale, manual)
  - Indexes on product_id, movement_type, created_at

### 3. Create Inventory Service (AC: 1, 2, 3)
- [ ] Create service in `src/app/services/inventory_service.py`
  - `update_stock_from_purchase()`: Main method called from purchase
  - `calculate_average_cost()`: Weighted average calculation
  - `record_stock_movement()`: Log movement history
  - `create_product_from_purchase()`: New product creation
  - `get_stock_movements()`: History for reporting

### 4. Extend Product CRUD (AC: 2, 4)
- [ ] Extend `src/app/crud/product.py`
  - `update_stock_quantity()`: Update stock levels
  - `update_purchase_info()`: Last price, average cost
  - `create_from_purchase()`: Quick product creation
  - Add methods for stock movement queries

### 5. Create Inventory Schemas (AC: 1, 3)
- [ ] Create schemas in `src/app/schemas/inventory.py`
  - `StockMovementCreate`: For recording movements
  - `StockMovementResponse`: For history display
  - `StockUpdateRequest`: For manual adjustments
  - `InventoryReport`: Current stock levels

### 6. Integration with Purchase Service (AC: 1, 2)
- [ ] Modify purchase service to call inventory service
  - Call `update_stock_from_purchase()` after purchase creation
  - Handle transaction rollback if inventory update fails
  - Pass all necessary data for cost calculations

### 7. Product Creation Workflow (AC: 2)
- [ ] Implement quick product creation from purchase
  - Minimal required fields: name, code, cost
  - Auto-generate product code if needed
  - Set appropriate defaults for new products
  - Validate product data before creation

### 8. Add API Endpoints (AC: 3, 4)
- [ ] Add routes to `src/app/api/v1/inventory.py`
  - `GET /inventory/stock-movements`: Movement history
  - `GET /inventory/products/{id}/movements`: Product-specific history
  - `POST /inventory/adjustments`: Manual stock adjustments
  - `GET /inventory/reports`: Current inventory status

### 9. Add Reporting Features (AC: 4)
- [ ] Create inventory reporting
  - Current stock levels with last purchase info
  - Stock movement reports by date range
  - Cost analysis reports
  - Low stock alerts

### 10. Write Tests
- [ ] Unit tests for inventory service
- [ ] Stock movement recording tests
- [ ] Average cost calculation tests
- [ ] Integration tests with purchase workflow
- [ ] Test new product creation
- [ ] Test error handling and rollbacks

## 📝 Dev Notes

### Data Models
**Stock Movement Tracking** [Source: architecture/source-tree.md#models]
- New StockMovement model for audit trail
- Reference to purchases via reference_type/reference_id
- Use ENUMs for movement and reference types

### Previous Story Dependencies
- STORY-063: Purchase and PurchaseItem models
- Existing Product model from Epic 003
- Must coordinate with purchase service integration

### Cost Calculation Logic
**Average Cost Formula**:
```
new_average = ((current_stock * current_average) + (purchased_qty * purchase_price)) / (current_stock + purchased_qty)
```

### Service Integration Pattern [Source: architecture/coding-standards.md#service-layer-pattern]
- Inventory service called by purchase service
- Clear separation: purchase service handles orders, inventory service handles stock
- Use dependency injection for service coupling

### Transaction Management [Source: architecture/coding-standards.md#database-standards]
- Stock updates must be in same transaction as purchase
- Rollback stock changes if purchase fails
- Atomic operations for data consistency

### Error Handling
- Validate product exists before stock update
- Handle negative stock scenarios
- Graceful failure with rollback
- Log all inventory operations for debugging

### Testing Strategy [Source: architecture/coding-standards.md#testing-standards]
- Mock purchase service in inventory tests
- Test cost calculations with various scenarios
- Verify transaction rollback behavior
- Test concurrent stock updates

### Performance Considerations
- Index stock movements by product_id
- Consider caching current stock levels
- Batch updates for large purchases
- Optimize average cost calculations

## 🧪 Testing Requirements
- Inventory service unit tests
- Cost calculation algorithm tests
- Stock movement recording tests
- Integration with purchase workflow
- Transaction rollback scenarios
- Concurrent update handling
- New product creation validation

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
