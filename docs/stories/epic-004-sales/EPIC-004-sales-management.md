# EPIC-004: Sales Management

## 📋 Epic Overview
- **Epic ID**: EPIC-004
- **Epic Name**: Sales Management
- **Priority**: HIGH
- **Status**: TODO
- **Estimated Duration**: 7 days

## 🎯 Business Goal
Enable María and Carlos to process sales efficiently, manage credit sales, track payment history, and generate invoices while maintaining accurate inventory levels and financial records.

## 👥 User Personas Affected
- **María** (Administrator): Needs full sales management capabilities including reports and refunds
- **Carlos** (Technician): Needs to process daily sales quickly and efficiently
- **Pedro** (Store Owner): Needs sales analytics and financial reporting

## 📝 Epic Description
Implement a comprehensive sales management system that handles cash and credit sales, payment processing, invoice generation, and refund management. The system must integrate with customer accounts for credit tracking and product inventory for stock management.

## 🎭 User Stories

### STORY-040: Create Sale
**As** María or Carlos,
**I want** to create new sales transactions quickly,
**So that** I can serve customers efficiently during busy periods

**Acceptance Criteria:**
1. Product search with barcode scanning support
2. Add multiple products with quantities
3. Apply discounts (percentage or fixed amount)
4. Select payment method (cash, credit, transfer)
5. Link sale to existing customer or walk-in
6. Auto-update inventory levels
7. Generate sale receipt/invoice

### STORY-041: Sales History
**As** María or Pedro,
**I want** to view and filter sales history,
**So that** I can track business performance and find specific transactions

**Acceptance Criteria:**
1. List all sales with pagination
2. Filter by date range, customer, user, payment method
3. Search by invoice number or customer name
4. View sale details including all products
5. Export sales report to Excel/PDF
6. Calculate daily/weekly/monthly totals
7. Show payment status for credit sales

### STORY-042: Payment Processing
**As** María,
**I want** to record customer payments for credit sales,
**So that** I can track customer account balances accurately

**Acceptance Criteria:**
1. Record partial or full payments
2. Multiple payment methods per transaction
3. Auto-update customer balance
4. Generate payment receipt
5. Payment history per customer
6. Overdue payment alerts
7. WhatsApp payment reminder integration

### STORY-043: Invoice Management
**As** María or Carlos,
**I want** to generate and manage invoices,
**So that** customers have proper documentation for their purchases

**Acceptance Criteria:**
1. Generate PDF invoices with company branding
2. Sequential invoice numbering
3. Include all legal requirements
4. Email or WhatsApp invoice delivery
5. Reprint invoices from history
6. Void invoice with reason tracking
7. Credit note generation for returns

### STORY-044: Refunds and Returns
**As** María,
**I want** to process refunds and returns properly,
**So that** I can maintain customer satisfaction and accurate records

**Acceptance Criteria:**
1. Return products with reason selection
2. Full or partial refunds
3. Store credit option
4. Auto-update inventory on returns
5. Link refund to original sale
6. Refund approval workflow
7. Generate credit notes

### STORY-045: Sales Analytics
**As** Pedro or María,
**I want** to view sales analytics and reports,
**So that** I can make informed business decisions

**Acceptance Criteria:**
1. Daily sales summary dashboard
2. Top selling products report
3. Sales by category analysis
4. Customer purchase patterns
5. Payment method breakdown
6. Profit margin analysis
7. Comparison with previous periods

## 📊 Success Metrics
- Average sale processing time < 2 minutes
- Invoice generation < 5 seconds
- Zero discrepancies in financial calculations
- 100% traceability for all transactions
- Payment recording accuracy 100%

## 🔗 Dependencies
- **Depends on**:
  - EPIC-002 (Customer Management) - Need customers for credit sales
  - EPIC-003 (Product Management) - Need products to sell
  - STORY-027 (Database Setup)
- **Blocks**:
  - EPIC-006 (Dashboard) - Need sales data for metrics

## 🚀 Technical Considerations

### Database Schema
```sql
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    user_id INTEGER REFERENCES users(id) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, partial, paid
    notes TEXT,
    is_voided BOOLEAN DEFAULT FALSE,
    void_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sale_items (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES sales(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    total_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES sales(id),
    customer_id INTEGER REFERENCES customers(id),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL, -- cash, credit, transfer, mixed
    reference_number VARCHAR(50),
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_invoice ON sales(invoice_number);
CREATE INDEX idx_payments_customer ON payments(customer_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
```

### Technical Decisions:
- **Invoice Numbering**: Sequential with prefix (e.g., INV-2024-0001)
- **Inventory Updates**: Real-time deduction on sale completion
- **Payment Flexibility**: Support partial payments and multiple methods
- **Transaction Integrity**: Use database transactions for consistency
- **Audit Trail**: Complete history of all modifications

## 🎨 UI/UX Considerations
- Quick product search with autocomplete
- Keyboard shortcuts for common actions
- Mobile-optimized POS interface
- Clear visual feedback for actions
- Offline capability with sync

## ✅ Definition of Done for Epic
- [ ] All user stories completed and tested
- [ ] Sales workflow fully functional
- [ ] Payment processing accurate
- [ ] Invoice generation working
- [ ] Inventory integration tested
- [ ] Financial calculations verified
- [ ] Reports generating correctly
- [ ] API documentation complete
- [ ] Performance optimized for high volume

## 📝 Notes
- Consider barcode scanner integration
- Future features (Post-MVP):
  - Loyalty program integration
  - Multi-currency support
  - POS hardware integration
  - Advanced discount rules
  - Sales commission tracking

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-27 | 1.0 | Initial epic creation | Sarah (PO) |
