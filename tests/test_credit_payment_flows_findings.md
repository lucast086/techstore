# Credit Payment System Findings

## Current System Behavior

When a sale is paid with customer credit (`payment_method = "account_credit"`):

1. **Credit Application Transaction**: The system first records a payment with `payment_type = "credit_application"`, which consumes the credit (makes balance less negative/more positive)
2. **Sale Transaction**: Then it records the full sale amount as a debit, increasing the customer's debt

### Example: $769 sale paid with $769 credit
- Initial balance: -$769 (customer has credit)
- After credit application: -$769 + $769 = $0
- After sale recording: $0 + $769 = $769 (customer now owes money!)

## Issues Identified

1. **Incorrect Final Balance**: When paying entirely with credit, the customer ends up owing the full sale amount instead of having a zero balance.

2. **Transaction Order**: The credit is consumed before the sale is recorded, leading to a temporary zero balance that then becomes debt.

3. **Double Recording**: The system essentially records the sale twice - once as a credit consumption and once as a debt creation.

## Expected Behavior

For a sale paid entirely with credit:
- Initial balance: -$769 (credit)
- Final balance: $0 (credit used, no debt)

## Root Cause

The issue stems from the sale creation logic in `src/app/crud/sale.py`:

1. It creates a payment record with type "credit_application"
2. `record_payment()` is called, which correctly consumes the credit
3. But then `record_sale()` is ALSO called, which adds the full sale amount as debt

This was intentionally changed in commit 80f0647 to ensure all sales are recorded for proper accounting, but it breaks credit payment logic.

## Potential Solutions

### Option 1: Skip Sale Recording for Full Credit Payments
When `payment_method == "account_credit"` and `amount_paid >= total_amount`, skip the `record_sale()` call.

### Option 2: Use Different Transaction Type
Create a new transaction type like `CREDIT_SALE` that doesn't affect the balance.

### Option 3: Offset Logic
After recording both transactions, create an adjustment transaction to correct the balance.

### Option 4: Redesign Credit Payment Flow
Instead of using the payment system, handle credit sales as a special case with its own logic.

## Recommendation

The current implementation appears to be a bug introduced by the recent change to always record full sale amounts. The system should be fixed to properly handle credit payments without creating unintended debt.

For testing purposes, we'll document the actual behavior while noting it as a bug.
