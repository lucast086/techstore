# STORY-040: Create Sale

## 📋 Story Details
- **Epic**: EPIC-004 (Sales Management)
- **Priority**: HIGH
- **Estimate**: 2 days
- **Status**: TODO

## 🎯 User Story
**As** María or Carlos,
**I want** to create new sales transactions quickly,
**So that** I can serve customers efficiently during busy periods

## ✅ Acceptance Criteria
1. [ ] Product search with autocomplete (by name, code, or barcode)
2. [ ] Add multiple products with quantities to cart
3. [ ] Real-time price calculation with subtotal and total
4. [ ] Apply discounts (percentage or fixed amount per item or total)
5. [ ] Select payment method (cash, credit, transfer, mixed)
6. [ ] Link sale to existing customer or mark as walk-in
7. [ ] Auto-update inventory levels on completion
8. [ ] Generate and display sale receipt
9. [ ] Quick product buttons for frequently sold items
10. [ ] Keyboard shortcuts for common actions

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── api/v1/
│   └── sales.py              # Sales API endpoints
├── web/
│   └── sales.py              # Sales web routes
├── schemas/
│   └── sale.py               # Sale validation schemas
├── crud/
│   └── sale.py               # Sale database operations
├── templates/
│   └── sales/
│       ├── pos.html          # Point of sale interface
│       ├── receipt.html      # Receipt template
│       └── partials/
│           ├── cart_item.html
│           ├── product_search.html
│           └── payment_form.html
└── static/
    └── js/
        └── pos.js            # POS interactions
```

### Implementation Requirements:

1. **Sale Schema** (`app/schemas/sale.py`):
   - CreateSale with items, customer, payment info
   - SaleItem with product, quantity, price, discount
   - Payment details with method and amount

2. **CRUD Operations** (`app/crud/sale.py`):
   - Create sale with transaction integrity
   - Update inventory levels atomically
   - Calculate totals and discounts

3. **API Endpoints** (`app/api/v1/sales.py`):
   - POST /sales - Create new sale
   - GET /sales/products/search - Product search
   - GET /sales/receipt/{id} - Get receipt

4. **Web Routes** (`app/web/sales.py`):
   - GET /pos - Point of sale interface
   - POST /pos/add-item - Add item to cart (HTMX)
   - POST /pos/checkout - Process sale

5. **Frontend** (`templates/sales/pos.html`):
   - Clean POS interface with cart
   - Product search with debounce
   - Real-time calculations
   - Mobile responsive design

## 🧪 Testing Approach

### Unit Tests:
- Sale creation with multiple items
- Discount calculations
- Inventory update logic
- Payment validation

### Integration Tests:
- Complete sale flow
- Concurrent sales handling
- Stock validation

### UI Tests:
- Product search functionality
- Cart management
- Payment processing

## 📦 Dependencies
- **Depends on**:
  - STORY-028 (Customer Model)
  - STORY-015 (Product List)
- **Blocks**:
  - STORY-041 (Sales History)
  - STORY-042 (Payment Processing)

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] API documentation updated
- [ ] Performance: Sale creation < 2 seconds
- [ ] Inventory updates verified
- [ ] Receipt generation working
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Consider implementing offline mode for reliability
- Barcode scanner integration planned for future
- Quick keys configuration will be added later
- Focus on speed and reliability for MVP

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
