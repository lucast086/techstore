# E2E Test Plan: Repair Workflow with Deposits

## Test Environment Setup

### Prerequisites
1. **Users**
   - Admin user (username: admin@techstore.com)
   - Technician user (username: tech@techstore.com)
   - Cashier user (username: cashier@techstore.com)

2. **Test Data**
   - At least 3 customers created:
     - Customer A: "Peter Parker" (regular customer)
     - Customer B: "Alice Williams" (customer with existing credit balance)
     - Customer C: "Jane Smith" (new customer)
   - Sample products in inventory
   - Cash register must be closed initially

3. **System State**
   - All previous repairs should be delivered or cancelled
   - No pending sales
   - Clean customer account balances (except Customer B)

### Initial Setup Commands
```bash
# Run migrations
poetry run alembic upgrade head

# Optional: Reset test data
poetry run python scripts/reset_test_data.py
```

---

## Test Scenarios

### Scenario 1: Complete Repair Flow with Deposits

**Objective**: Test the complete repair lifecycle with partial deposits (señas)

#### Steps:

1. **Open Cash Register**
   - Navigate to: `/cash-register`
   - Click "Open Cash Register"
   - Enter opening amount: $1000
   - Verify: Success message and cash register status shows "OPEN"

2. **Create Repair Order**
   - Navigate to: `/repairs/new`
   - Select Customer: "AlicePeter Parker Williams"
   - Device Type: "Smartphone"
   - Brand: "Samsung"
   - Model: "Galaxy S21"
   - Problem: "Screen broken, needs replacement"
   - Estimated Cost: $500
   - Priority: "Normal"
   - Click "Create Repair"
   - Note the Repair Number (e.g., REP-2025-001)

3. **Add First Deposit (Seña)**
   - From repair detail page, click "Add Deposit"
   - Amount: $200
   - Payment Method: Cash
   - Notes: "Initial deposit from customer"
   - Click "Record Deposit"
   - Verify:
     - Deposit shows in repair details
     - Receipt number is generated
     - Customer account shows -$200 credit

4. **Diagnose and Update Repair**
   - Click "Update Status"
   - Change to "In Diagnosis"
   - Add diagnosis notes: "Screen completely shattered, LCD damaged"
   - Click "Update"

5. **Add Repair Parts**
   - Click "Add Part"
   - Part Name: "Samsung S21 Screen"
   - Cost: $250
   - Quantity: 1
   - Supplier: "TechParts Inc"
   - Click "Add"

6. **Complete Repair**
   - Click "Mark as Completed"
   - Labor Cost: $150
   - Parts Cost: $250 (auto-filled)
   - Final Cost: $400 (total)
   - Solution Notes: "Screen replaced successfully, all functions tested"
   - Click "Complete"
   - Verify: Status changes to "Ready for Pickup"

7. **Add to POS for Delivery**
   - Navigate to: `/pos`
   - Search for repair: Enter repair number
   - Click "Add Repair to Cart"
   - Verify:
     - Repair shows as line item
     - Price shows $200 (remaining after $200 deposit)
     - Deposit amount shown as discount

8. **Complete Sale and Deliver**
   - Payment Method: Cash
   - Amount Received: $200
   - Click "Process Sale"
   - Verify:
     - Sale completes successfully
     - Receipt shows repair details and deposits applied
     - Repair status changes to "Delivered"

9. **Verify Cash Closing**
   - Navigate to: `/cash-register/close`
   - Verify:
     - Total cash shows $1200 ($1000 opening + $200 payment)
     - Repair deposits show $200
     - Sales show $200

**Expected Results**:
- Repair lifecycle complete
- Deposits correctly applied
- Customer account balanced
- Cash register balanced

---

### Scenario 2: Multiple Deposits on Single Repair

**Objective**: Test handling multiple deposits on one repair

#### Steps:

1. **Create Repair** (Follow Scenario 1, Steps 1-2)
   - Estimated Cost: $800

2. **Add First Deposit**
   - Amount: $300
   - Payment Method: Cash
   - Record deposit

3. **Add Second Deposit**
   - Amount: $200
   - Payment Method: Card
   - Record deposit

4. **Add Third Deposit**
   - Amount: $100
   - Payment Method: Transfer
   - Record deposit

5. **Verify Deposits Summary**
   - Total Deposits: $600
   - Three deposit records shown
   - Each with unique receipt number

6. **Complete and Deliver Repair**
   - Final Cost: $800
   - Add to POS
   - Verify: Amount due is $200 ($800 - $600 deposits)

**Expected Results**:
- All deposits tracked individually
- Correct total calculation
- Each payment method recorded

---

### Scenario 3: Repair with Full Deposit

**Objective**: Test repair fully paid with deposits

#### Steps:

1. **Create Repair**
   - Customer: "Alice Williams"
   - Estimated Cost: $300

2. **Add Full Deposit**
   - Amount: $300
   - Payment Method: Cash

3. **Complete Repair**
   - Final Cost: $300

4. **Add to POS**
   - Verify: Shows $0 due
   - Message: "Repair fully paid with deposits"

5. **Process Delivery**
   - No payment required
   - Mark as delivered only

**Expected Results**:
- POS handles $0 transactions
- Repair delivered without additional payment
- Receipt shows fully paid status

---

### Scenario 4: Repair with Customer Credit

**Objective**: Test using existing customer credit for repair payment

#### Prerequisites:
- Customer B has $150 credit balance

#### Steps:

1. **Create Repair**
   - Customer: "Alice Williams" (Customer B)
   - Estimated Cost: $400

2. **View Customer Account**
   - Verify credit balance: -$150

3. **Complete Repair**
   - Final Cost: $400

4. **Add to POS**
   - Apply customer credit: $150
   - Remaining due: $250

5. **Process Payment**
   - Cash payment: $250
   - Complete sale

**Expected Results**:
- Customer credit properly applied
- Credit balance updated to $0
- Receipt shows credit application

---

### Scenario 5: Mixed Sale (Repair + Products)

**Objective**: Test POS handling repairs and regular products together

#### Steps:

1. **Complete a Repair** (from Scenario 1)
   - Ready for pickup
   - Amount due: $200

2. **Start POS Transaction**
   - Add repair to cart
   - Add product: "Phone Case" ($25)
   - Add product: "Screen Protector" ($15)

3. **Verify Cart**
   - Repair: $200
   - Products: $40
   - Total: $240

4. **Process Payment**
   - Cash: $240
   - Complete sale

**Expected Results**:
- Mixed items handled correctly
- Single receipt for all items
- Inventory updated for products
- Repair marked as delivered

---

### Scenario 6: Deposit Refund

**Objective**: Test refunding deposits when repair is cancelled

#### Steps:

1. **Create Repair with Deposit**
   - Create repair
   - Add deposit: $200 cash

2. **Cancel Repair**
   - Change status to "Cancelled"
   - Reason: "Customer declined repair cost"

3. **Refund Deposit**
   - Click "Refund Deposit"
   - Refund amount: $200
   - Refund reason: "Repair cancelled by customer"

4. **Verify Refund**
   - Deposit status: "Refunded"
   - Customer account: Credit removed
   - Cash register: Shows refund transaction

**Expected Results**:
- Deposit refunded successfully
- Customer account updated
- Audit trail maintained

---

### Scenario 7: Cash Closing with Repairs

**Objective**: Verify cash closing with various repair transactions

#### Steps:

1. **Open Cash Register**
   - Opening amount: $500

2. **Process During Day**:
   - Regular sale: $100 cash
   - Repair deposit 1: $150 cash
   - Repair deposit 2: $100 card
   - Repair delivery (with deposits): $200 cash
   - Product sale: $50 cash
   - Deposit refund: -$50 cash

3. **Close Cash Register**
   - Navigate to close screen
   - Verify calculations:
     - Opening: $500
     - Cash sales: $150 ($100 + $50)
     - Repair deposits (cash): $150
     - Repair sales: $200
     - Refunds: -$50
     - Expected cash: $950

4. **Enter Actual Count**
   - Count cash: $950
   - No difference
   - Add closing notes

5. **Generate Report**
   - View closing report
   - Verify all transactions listed
   - Print/save report

**Expected Results**:
- All transactions properly categorized
- Correct cash calculation
- Deposits tracked separately
- Report shows complete detail

---

## Validation Checks

### Critical Validations to Test:

1. **Deposit Amount Validation**
   - Cannot exceed repair estimated cost
   - Must be greater than zero
   - Total deposits cannot exceed final cost

2. **Repair Status Validation**
   - Cannot add deposits to delivered repairs
   - Cannot add deposits to cancelled repairs
   - Cannot deliver without final cost

3. **Cash Register Validation**
   - Cannot deliver repairs without open register
   - Cannot record deposits without open register
   - Cannot process refunds without open register

4. **Customer Account Validation**
   - Deposits create credit entries
   - Applied deposits reduce credit
   - Refunds restore credit

5. **Receipt Number Validation**
   - Unique receipt numbers generated
   - Sequential ordering maintained
   - No duplicates allowed

---

## Error Scenarios to Test

### 1. Attempting Invalid Operations
- Add deposit exceeding repair cost
- Deliver repair without completing
- Refund already applied deposit
- Add deposit to delivered repair

### 2. System Constraints
- Process repair without open cash register
- Create duplicate receipt numbers
- Apply non-existent deposits

### 3. Data Integrity
- Delete customer with active repairs
- Modify deposit after applied
- Change repair cost after deposits

---

## Performance Testing

### Load Testing Scenarios:

1. **Multiple Concurrent Deposits**
   - 10 users adding deposits simultaneously
   - Verify no duplicate receipts
   - Check transaction integrity

2. **Large Number of Repairs**
   - Create 100+ repairs with deposits
   - Test search performance
   - Verify reporting accuracy

3. **Complex Cash Closing**
   - Process 50+ transactions in one day
   - Multiple payment methods
   - Verify closing calculation time

---

## Regression Testing

After each update, verify:

1. **Existing Functionality**
   - Regular sales still work
   - Customer accounts unchanged
   - Cash closing unaffected

2. **Data Migration**
   - Old repairs still accessible
   - Historical data preserved
   - Reports include all data

3. **Integration Points**
   - POS integration stable
   - Customer accounts synced
   - Payment processing works

---

## Test Execution Checklist

### Before Testing:
- [ ] Database backed up
- [ ] Test environment ready
- [ ] Test users created
- [ ] Initial data loaded

### During Testing:
- [ ] Document any issues found
- [ ] Take screenshots of errors
- [ ] Note performance issues
- [ ] Record unexpected behaviors

### After Testing:
- [ ] Generate test report
- [ ] Log all bugs found
- [ ] Verify data consistency
- [ ] Clean test environment

---

## Bug Report Template

When reporting issues, include:

```
**Bug ID**: [Sequential number]
**Date Found**: [Date]
**Tester**: [Name]
**Severity**: [Critical/High/Medium/Low]

**Description**:
[Clear description of the issue]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**:
[What should happen]

**Actual Result**:
[What actually happened]

**Screenshots/Logs**:
[Attach relevant files]

**Environment**:
- Browser: [Chrome/Firefox/Safari]
- User Role: [Admin/Technician/Cashier]
- Module: [Repairs/POS/Cash Register]
```

---

## Sign-off Criteria

The feature is ready for production when:

1. **Functional Requirements**
   - [ ] All test scenarios pass
   - [ ] No critical bugs remain
   - [ ] Performance acceptable

2. **User Acceptance**
   - [ ] UI intuitive and responsive
   - [ ] Error messages clear
   - [ ] Workflow logical

3. **Technical Requirements**
   - [ ] Code review completed
   - [ ] Documentation updated
   - [ ] Database migrations tested

4. **Business Requirements**
   - [ ] Accounting accuracy verified
   - [ ] Audit trail complete
   - [ ] Reports generating correctly

---

## Contact Information

**Development Team**: development@techstore.com
**QA Team**: qa@techstore.com
**Project Manager**: pm@techstore.com

Last Updated: [Current Date]
Version: 1.0
