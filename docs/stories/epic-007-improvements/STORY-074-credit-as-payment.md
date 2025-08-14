# STORY-074: Use Customer Credit as Payment Method

**Status:** In Progress
**Priority:** P1 (High)
**Type:** New Feature
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As a cashier, when a customer has a positive balance (credit), I need to use that credit as a payment method (partial or total) during a sale.

## Business Value
- Simplifies use of customer advances
- Reduces cash handling
- Improves customer experience
- Ensures credit is properly tracked and consumed

## Acceptance Criteria
- [ ] "Saldo a favor" payment option appears ONLY when customer.balance > 0
- [ ] Shows available credit amount: "Disponible: $XXX"
- [ ] Allows partial use of credit
- [ ] Allows combining credit with other payment methods
- [ ] Updates customer balance after use
- [ ] Transaction recorded as "CREDIT_USED"
- [ ] Cannot use more credit than available
- [ ] Receipt shows credit applied

## Technical Implementation

### Files to Modify
- `/src/app/templates/sales/pos.html` - Add credit payment option
- `/src/app/api/v1/sales.py` - Process credit payments
- `/src/app/services/payment_service.py` - Credit application logic
- `/src/app/models/payment_method.py` - Add CUSTOMER_CREDIT type
- `/src/app/static/js/pos.js` - Client-side credit handling

### Tasks
- [x] Add CUSTOMER_CREDIT to payment methods enum
- [x] Fix validation schema to include 'account_credit' payment method
- [x] Implement credit deduction logic in payment processing
- [x] Add apply_customer_credit method to PaymentService
- [x] Handle account_credit payment method in sales checkout
- [x] Handle mixed payment with credit portion
- [ ] Fetch customer credit balance in POS
- [ ] Show/hide credit option based on balance
- [ ] Implement credit amount input with validation
- [ ] Update receipt template
- [ ] Add transaction logging

### Implementation Flow
```javascript
// POS JavaScript
function loadCustomerCredit(customerId) {
    fetch(`/api/v1/customers/${customerId}/balance`)
        .then(response => response.json())
        .then(data => {
            if (data.balance > 0) {
                showCreditOption(data.balance);
            } else {
                hideCreditOption();
            }
        });
}

function showCreditOption(availableCredit) {
    const creditSection = document.getElementById('credit-payment-section');
    creditSection.style.display = 'block';
    document.getElementById('available-credit').textContent = `$${availableCredit}`;
    document.getElementById('credit-amount').max = availableCredit;
}
```

```python
# Sales API
def process_payment(sale_id: int, payment_data: PaymentData):
    if payment_data.credit_amount > 0:
        customer = get_customer(payment_data.customer_id)

        if customer.balance < payment_data.credit_amount:
            raise ValueError("Insufficient credit balance")

        # Apply credit
        customer.balance -= payment_data.credit_amount

        # Record credit transaction
        create_transaction(
            type="CREDIT_USED",
            amount=payment_data.credit_amount,
            sale_id=sale_id
        )
```

## Testing Requirements
- Customer with $100 credit, purchase of $50
- Customer with $50 credit, purchase of $100 (mixed payment)
- Customer with $0 credit (option should not appear)
- Customer with negative balance (option should not appear)
- Try to use more credit than available (should fail)
- Verify balance updates correctly
- Verify transaction history

## UI/UX Considerations
- Credit option prominently displayed when available
- Clear indication of available amount
- Prevent over-use with input validation
- Show remaining credit after application
- Success message when credit applied

## Dev Notes
- Consider partial credit refunds
- Ensure atomic transaction for balance updates
- Add audit log for credit usage
- Think about credit expiration policies

---

## Dev Agent Record

### Task Progress
- [ ] Add payment method type
- [ ] Implement credit detection
- [ ] Create UI components
- [ ] Process credit payments
- [ ] Update customer balance
- [ ] Test all scenarios

### Debug Log
- **2025-08-13**: Fixed validation error - payment_method 'account_credit' not allowed in SaleCreate schema
- **Error**: `String should match pattern '^(cash|transfer|card|mixed)'` - missing 'account_credit'
- **Solution**: Updated payment_method pattern in both `/src/app/schemas/sale.py` and `/src/app/api/v1/sales.py`
- **2025-08-13**: Fixed credit deduction issue - credit wasn't being deducted from customer balance
- **Problem**: Sale processed but customer credit remained unchanged
- **Solution**: Added `apply_customer_credit()` method to PaymentService to create negative payment records

### Completion Notes

### File List
- `/src/app/schemas/sale.py` - Updated payment_method pattern validation
- `/src/app/api/v1/sales.py` - Updated Query pattern validation
- `/src/app/services/payment_service.py` - Added apply_customer_credit method
- `/src/app/web/sales.py` - Added credit deduction logic in checkout process

### Change Log
- 2025-08-13: Fixed Pydantic validation error for 'account_credit' payment method
- 2025-08-13: Updated schemas to accept new payment type
- 2025-08-13: Implemented credit deduction logic for account_credit and mixed payments
- 2025-08-13: Added PaymentService.apply_customer_credit method for proper balance management

### Agent Model Used
claude-sonnet-4-20250514
