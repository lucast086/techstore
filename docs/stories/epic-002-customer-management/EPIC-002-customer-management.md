# EPIC-002: Customer Management

## 📋 Epic Overview
- **Epic ID**: EPIC-002
- **Epic Name**: Customer Management
- **Priority**: HIGH
- **Status**: TODO
- **Estimated Duration**: 5 days

## 🎯 Business Goal
Enable María and Carlos to efficiently manage customer information, track customer accounts with credit/debit balances, and maintain a complete history of customer interactions with the business.

## 👥 User Personas Affected
- **María** (Administrator): Needs to manage all customer data and accounts
- **Carlos** (Technician): Needs to access customer information for sales and repairs

## 📝 Epic Description
Implement a comprehensive customer management system that allows users to register new customers, search existing customers, manage their profiles, and track their account balances. This system will be the foundation for sales on credit and customer relationship management.

## 🎭 User Stories

### STORY-028: Customer Model & Migration
**As a** developer,  
**I want** to create the customer data model and database migration,  
**So that** we can store customer information in the database

**Acceptance Criteria:**
1. Customer model created with all required fields
2. Database migration generated and tested
3. Indexes added for search performance
4. Model includes account balance tracking
5. Relationship with user (created_by) established

### STORY-029: Customer Registration
**As** María or Carlos,  
**I want** to register new customers with their information,  
**So that** I can track their purchases and provide personalized service

**Acceptance Criteria:**
1. Registration form with validation
2. Required fields: name, primary phone
3. Optional fields: secondary phone, email, address, notes
4. Duplicate primary phone shows error
5. Success message after registration
6. Auto-search while typing phone to prevent duplicates
7. Customer is active by default

### STORY-030: Customer Search
**As** María or Carlos,  
**I want** to search for customers by name or phone numbers,  
**So that** I can quickly find customer information during sales or service

**Acceptance Criteria:**
1. Search bar on customer list page
2. Real-time search as user types (debounced)
3. Search by partial name, primary phone, or secondary phone
4. Results show: name, phones, calculated balance
5. Click on result goes to customer profile
6. "No results found" message when appropriate
7. Only show active customers by default
8. Option to include inactive customers in search

### STORY-031: Customer Profile
**As** María or Carlos,  
**I want** to view and edit customer profiles,  
**So that** I can keep customer information up to date and see their history

**Acceptance Criteria:**
1. Profile shows all customer information
2. Edit button for authorized users
3. Transaction history tab (sales and payments)
4. Repair history tab
5. Current account balance prominently displayed
6. Contact information section
7. Notes/comments section

### STORY-032: Customer Account Balance
**As** María,  
**I want** to view customer account balances and transaction history,  
**So that** I can track credit sales and customer payments

**Acceptance Criteria:**
1. Display calculated balance (positive = customer has credit, negative = customer owes)
2. Balance calculated from all sales and payment transactions
3. Transaction history shows all sales and payments
4. Cannot delete customer with non-zero balance
5. Visual indicator for customers with debt
6. Export account statement as PDF
7. WhatsApp button to send balance reminder

## 📊 Success Metrics
- Customer registration time < 30 seconds
- Search results appear in < 500ms
- 100% accuracy in balance calculations
- Zero data loss for customer information

## 🔗 Dependencies
- **Depends on**: 
  - STORY-027 (Database Setup)
  - STORY-020 (Authentication System)
- **Blocks**: 
  - EPIC-004 (Sales Management) - Need customers for sales
  - EPIC-005 (Repair Management) - Need customers for repairs

## 🚀 Technical Considerations

### Database Schema
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    phone_secondary VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,  -- For soft delete
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_phone_secondary ON customers(phone_secondary);
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_active ON customers(is_active);
```

### Technical Decisions (Confirmed):

**Phone Numbers**:
- Two phone fields: primary and secondary contact
- No strict format validation (flexible for different formats)
- Both numbers searchable

**Account Balance**:
- Always calculated from transactions (no stored balance)
- Ensures accuracy and prevents sync issues
- Will optimize with database views if needed

**Customer Deletion**:
- Soft delete implementation (is_active flag)
- Deletion prevented if customer has non-zero balance
- Deleted customers hidden from normal views but data preserved

## 🎨 UI/UX Considerations
- Customer list with infinite scroll or pagination
- Quick actions on customer cards (view, edit, add sale)
- Color coding for account status (green = credit, red = debt)
- Mobile-responsive design for on-the-go access

## ✅ Definition of Done for Epic
- [ ] All user stories completed and tested
- [ ] Customer data model fully implemented
- [ ] Search functionality optimized
- [ ] Account balance tracking accurate
- [ ] UI follows design system
- [ ] API documentation complete
- [ ] Integration tests passing
- [ ] Performance benchmarks met

## 📝 Notes
- All customer communication will be via WhatsApp
- No tax ID tracking in MVP
- Future features (Post-MVP):
  - Customer categories/types (Regular, Wholesale, VIP)
  - Credit limits per customer
  - Bulk import functionality
  - Account balance alerts
  - Customer segmentation for marketing

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-27 | 1.0 | Initial epic creation | Sarah (PO) |