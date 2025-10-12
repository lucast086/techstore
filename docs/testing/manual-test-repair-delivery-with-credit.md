# Manual Testing Guide: Repair Delivery with Customer Credit

## Prerequisites

1. **Create the repair service product** (run once):
   ```bash
   poetry run python scripts/create_repair_service_product.py
   ```

2. **Ensure cash register is open**:
   - Navigate to Cash Closings
   - Open cash register for today with an opening balance

3. **Create a test customer** (if you don't have one):
   - Navigate to Customers
   - Create a customer with name, phone, etc.

## Test Scenarios

### Scenario 1: Repair Delivery WITHOUT Customer Credit

**Steps:**
1. Create a new repair order
   - Select the test customer
   - Device: iPhone 12, Screen broken
   - Save the repair

2. Progress the repair through workflow:
   - Status: Diagnosing → Approved → Repairing → Complete
   - Set final cost: $150.00
   - Status should automatically change to "Ready"

3. Deliver the repair:
   - Click "Deliver" button
   - Should create a sale automatically
   - Check that sale was created with total $150.00

4. **Expected Results:**
   - ✓ Repair status = "Delivered"
   - ✓ Sale created with invoice number (INV-YYYY-XXXXX)
   - ✓ Sale total_amount = $150.00
   - ✓ Sale paid_amount = $0.00 (pending payment)
   - ✓ Sale payment_status = "pending"
   - ✓ Customer account shows $150.00 debt

---

### Scenario 2: Repair Delivery WITH FULL Customer Credit

**Setup:**
1. Give customer credit:
   - Navigate to customer's account
   - Add credit: $200.00 (negative balance = credit)

**Steps:**
1. Create a new repair order for the same customer
   - Device: Dell Laptop, Won't boot
   - Progress through workflow: Diagnosing → Approved → Repairing

2. Complete the repair:
   - Set final cost: $150.00
   - Status → "Ready"

3. Deliver the repair:
   - Click "Deliver" button

4. **Expected Results:**
   - ✓ Repair status = "Delivered"
   - ✓ Sale created automatically
   - ✓ Sale total_amount = $150.00
   - ✓ Sale paid_amount = $150.00 (fully paid with credit)
   - ✓ Sale payment_status = "paid"
   - ✓ Sale payment_method = "account_credit"
   - ✓ Customer credit balance reduced: $200 - $150 = $50 remaining
   - ✓ Customer account balance = -$50.00 (negative = credit)

---

### Scenario 3: Repair Delivery WITH PARTIAL Customer Credit

**Setup:**
1. Adjust customer credit to $50.00:
   - Customer should have $50 credit available

**Steps:**
1. Create a new repair order
   - Device: Samsung Tablet, Battery issue
   - Progress through workflow

2. Complete the repair:
   - Set final cost: $200.00
   - Status → "Ready"

3. Deliver the repair:
   - Click "Deliver" button

4. **Expected Results:**
   - ✓ Repair status = "Delivered"
   - ✓ Sale created automatically
   - ✓ Sale total_amount = $200.00
   - ✓ Sale paid_amount = $50.00 (partial payment with credit)
   - ✓ Sale payment_status = "partial"
   - ✓ Sale payment_method = "account_credit"
   - ✓ Customer credit used completely: $50 - $50 = $0
   - ✓ Customer still owes: $200 - $50 = $150
   - ✓ Customer account balance = $150.00 (positive = debt)

---

### Scenario 4: Cannot Deliver Without Open Cash Register

**Setup:**
1. Close the cash register (if open)

**Steps:**
1. Create and complete a repair order
2. Try to deliver the repair

3. **Expected Results:**
   - ✓ Error message: "Cash register must be open to deliver repairs"
   - ✓ Repair status remains "Ready" (not delivered)
   - ✓ No sale created

---

## Verification Queries (Database)

If you want to verify in the database:

```sql
-- Check the repair service product exists
SELECT id, sku, name, is_service, is_active
FROM products
WHERE sku = 'REPAIR-SERVICE';

-- Check a specific repair and its sale
SELECT
    r.repair_number,
    r.status,
    r.final_cost,
    r.sale_id,
    s.invoice_number,
    s.total_amount,
    s.paid_amount,
    s.payment_status,
    s.payment_method
FROM repairs r
LEFT JOIN sales s ON r.sale_id = s.id
WHERE r.repair_number = 'REP-2025-XXXXX';

-- Check customer account balance and credit
SELECT
    c.name,
    ca.account_balance,
    ca.available_credit,
    ca.total_sales,
    ca.total_payments
FROM customers c
JOIN customer_accounts ca ON c.id = ca.customer_id
WHERE c.id = <customer_id>;

-- Check recent transactions for a customer
SELECT
    transaction_type,
    amount,
    balance_before,
    balance_after,
    description,
    transaction_date
FROM customer_transactions
WHERE customer_id = <customer_id>
ORDER BY transaction_date DESC
LIMIT 10;
```

## Troubleshooting

### Error: "Repair service product (SKU: REPAIR-SERVICE) not found"
**Solution:** Run the script to create the product:
```bash
poetry run python scripts/create_repair_service_product.py
```

### Error: "Cash register must be open"
**Solution:** Open the cash register from the Cash Closings page

### Sale not appearing in reports
**Solution:** Verify that the sale date matches today's date and cash register is for today

### Credit not applying correctly
**Solution:** Check customer account balance:
- Negative balance = credit available
- Positive balance = debt owed
- Use the customer account page to verify transactions
