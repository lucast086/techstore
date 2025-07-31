# EPIC-005: Repair Management

## 📋 Epic Overview
- **Epic ID**: EPIC-005
- **Epic Name**: Repair Management
- **Priority**: HIGH
- **Status**: TODO
- **Estimated Duration**: 8 days

## 🎯 Business Goal
Enable Carlos and María to efficiently manage the complete repair workflow from device reception to delivery, including diagnosis, status tracking, cost estimation, and customer communication throughout the repair process.

## 👥 User Personas Affected
- **Carlos** (Technician): Primary user for repair reception, diagnosis, and technical work
- **María** (Administrator): Manages repair workflow, pricing, and customer communication
- **Pedro** (Store Owner): Monitors repair performance and profitability

## 📝 Epic Description
Implement a comprehensive repair management system that tracks devices through their entire repair lifecycle. The system must handle multiple device types, track repair status, manage parts inventory, calculate costs, and maintain communication with customers.

## 🎭 User Stories

### STORY-051: Receive Repair
**As** Carlos or María,
**I want** to register new repair orders quickly,
**So that** customers receive proper documentation and devices are tracked

**Acceptance Criteria:**
1. Create repair order with customer selection
2. Device type and brand selection
3. Detailed problem description
4. Device condition documentation (photos optional)
5. Accessories received checklist
6. Generate repair receipt with unique ID
7. Estimated completion date
8. WhatsApp notification to customer

### STORY-052: Diagnose Repair
**As** Carlos,
**I want** to document device diagnosis and repair plan,
**So that** I can provide accurate estimates and track work needed

**Acceptance Criteria:**
1. Add diagnosis notes to repair order
2. List required parts with costs
3. Estimate labor time and cost
4. Total repair cost calculation
5. Customer approval workflow
6. Alternative repair options
7. Photo documentation of issues

### STORY-053: Update Repair Status
**As** Carlos or María,
**I want** to update repair status as work progresses,
**So that** everyone knows the current state of each repair

**Acceptance Criteria:**
1. Status workflow: Received → Diagnosing → Approved → Repairing → Testing → Ready → Delivered
2. Timestamp for each status change
3. Add notes with status updates
4. Automatic customer notifications on key status changes
5. Visual status indicators
6. Reason required for certain transitions
7. Status history tracking

### STORY-054: Deliver Repair
**As** María or Carlos,
**I want** to complete the repair delivery process,
**So that** devices are properly returned and payment is collected

**Acceptance Criteria:**
1. Verify customer identity
2. Device functionality checklist
3. Customer sign-off on completion
4. Process payment (full or partial)
5. Generate delivery receipt
6. Warranty information included
7. Update device status to delivered

### STORY-055: Search Repairs
**As** Carlos or María,
**I want** to search and filter repair orders,
**So that** I can quickly find specific repairs or view workload

**Acceptance Criteria:**
1. Search by repair ID, customer name, or phone
2. Filter by status, technician, date range
3. Filter by device type or brand
4. View repair queue by status
5. Sort by priority or age
6. Export filtered results
7. Quick status overview dashboard

### STORY-056: Session Repair
**As** Carlos,
**I want** to handle quick repairs done while customer waits,
**So that** simple issues can be resolved immediately

**Acceptance Criteria:**
1. Express repair workflow
2. Simplified documentation
3. Immediate invoicing
4. Quick parts selection
5. Timer for session duration
6. Direct to payment after completion
7. Customer satisfaction quick survey

### STORY-057: Repair Cost Management
**As** María,
**I want** to manage repair pricing and costs,
**So that** repairs are profitable and consistently priced

**Acceptance Criteria:**
1. Parts cost tracking with suppliers
2. Labor rate configuration
3. Standard repair price templates
4. Margin calculation
5. Discount authorization
6. Cost history tracking
7. Profitability reports by repair type

### STORY-058: Repair Warranty
**As** María or Carlos,
**I want** to track repair warranties,
**So that** warranty claims are handled properly

**Acceptance Criteria:**
1. Set warranty period per repair
2. Track warranty expiration
3. Link warranty repairs to original
4. Warranty claim workflow
5. Warranty report generation
6. Customer warranty lookup
7. Warranty terms documentation

## 📊 Success Metrics
- Average repair turnaround < 48 hours
- Customer notification rate 100%
- Repair status accuracy 100%
- Zero lost devices
- Warranty claim rate < 5%
- Customer satisfaction > 90%

## 🔗 Dependencies
- **Depends on**:
  - EPIC-002 (Customer Management) - Need customers for repairs
  - STORY-027 (Database Setup)
  - STORY-020 (Authentication System)
- **Blocks**:
  - EPIC-006 (Dashboard) - Need repair metrics

## 🚀 Technical Considerations

### Database Schema
```sql
CREATE TABLE repairs (
    id SERIAL PRIMARY KEY,
    repair_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    device_brand VARCHAR(50) NOT NULL,
    device_model VARCHAR(100),
    serial_number VARCHAR(100),
    problem_description TEXT NOT NULL,
    device_condition TEXT,
    accessories_received TEXT,
    status VARCHAR(20) DEFAULT 'received',
    diagnosis_notes TEXT,
    repair_notes TEXT,
    estimated_cost DECIMAL(10,2),
    final_cost DECIMAL(10,2),
    labor_cost DECIMAL(10,2),
    parts_cost DECIMAL(10,2),
    received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_completion DATE,
    completed_date TIMESTAMP,
    delivered_date TIMESTAMP,
    warranty_days INTEGER DEFAULT 30,
    warranty_expires DATE,
    assigned_technician INTEGER REFERENCES users(id),
    received_by INTEGER REFERENCES users(id),
    delivered_by INTEGER REFERENCES users(id),
    is_express BOOLEAN DEFAULT FALSE,
    customer_approved BOOLEAN DEFAULT FALSE,
    approval_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repair_status_history (
    id SERIAL PRIMARY KEY,
    repair_id INTEGER REFERENCES repairs(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    notes TEXT,
    changed_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repair_parts (
    id SERIAL PRIMARY KEY,
    repair_id INTEGER REFERENCES repairs(id) ON DELETE CASCADE,
    part_name VARCHAR(200) NOT NULL,
    part_cost DECIMAL(10,2) NOT NULL,
    quantity INTEGER DEFAULT 1,
    supplier VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE repair_photos (
    id SERIAL PRIMARY KEY,
    repair_id INTEGER REFERENCES repairs(id) ON DELETE CASCADE,
    photo_url VARCHAR(500) NOT NULL,
    photo_type VARCHAR(20), -- before, during, after
    description TEXT,
    uploaded_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_repairs_customer ON repairs(customer_id);
CREATE INDEX idx_repairs_status ON repairs(status);
CREATE INDEX idx_repairs_number ON repairs(repair_number);
CREATE INDEX idx_repairs_received ON repairs(received_date);
CREATE INDEX idx_repair_status_history_repair ON repair_status_history(repair_id);
```

### Technical Decisions:
- **Repair Numbering**: Format REP-YYYY-NNNNN (e.g., REP-2024-00001)
- **Status Workflow**: Enforced transitions with validation
- **Photo Storage**: Cloud storage with URL references
- **Notification System**: WhatsApp API integration
- **Express Repairs**: Simplified workflow for quick fixes

## 🎨 UI/UX Considerations
- Visual kanban board for repair status
- Color coding by urgency/age
- Mobile-friendly for workshop use
- Quick actions for common updates
- Photo capture integration
- Barcode/QR code for repair tracking

## ✅ Definition of Done for Epic
- [ ] All user stories completed and tested
- [ ] Repair workflow fully functional
- [ ] Status tracking accurate
- [ ] Customer notifications working
- [ ] Cost calculations verified
- [ ] Warranty tracking implemented
- [ ] Search and filtering optimized
- [ ] API documentation complete
- [ ] Mobile interface tested

## 📝 Notes
- Consider SMS notifications as backup
- Future features (Post-MVP):
  - Parts inventory integration
  - Technician performance metrics
  - Repair time estimates by type
  - Customer portal for status checking
  - Automated diagnosis suggestions
  - Integration with supplier catalogs

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-27 | 1.0 | Initial epic creation | Sarah (PO) |
