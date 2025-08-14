# STORY-073: Enable Advance Payments (Customer Credit)

**Status:** Ready for Review
**Priority:** P1 (High)
**Type:** New Feature
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As a cashier, I need to record advance payments from customers even when they don't have outstanding debt, generating a positive balance (credit) for future work.

## Business Value
- Allows customers to pay in advance for repairs/purchases
- Improves cash flow with advance payments
- Provides flexibility in payment arrangements
- Builds customer trust with transparent credit tracking

## Acceptance Criteria
- [x] Payment form allows entry without existing debt
- [x] When balance >= 0, payment creates positive balance
- [x] UI clearly shows "Saldo a favor: $XXX" in green
- [x] Transaction type shows as "ADVANCE_PAYMENT"
- [x] Notes field is required to specify purpose
- [x] Credit appears in customer statement
- [x] Credit balance is immediately available for use

## Technical Implementation

### Files to Modify
- `/src/app/api/v1/payments.py` - Remove debt validation
- `/src/app/templates/payments/new.html` - Update UI for advances
- `/src/app/models/payment.py` - Add ADVANCE_PAYMENT type
- `/src/app/services/customer_service.py` - Handle positive balances
- `/src/app/templates/customers/detail.html` - Show credit clearly

### Tasks
- [x] Remove validation that blocks payment without debt
- [x] Add payment type: ADVANCE_PAYMENT
- [x] Update UI to show "Registro de Adelanto" when no debt
- [x] Make notes field required for advances
- [x] Update balance calculation for positive amounts
- [x] Style positive balance differently (green)
- [x] Add validation tests
- [x] Update customer statement view

### Implementation Details
```python
# payment.py model
class PaymentType(enum.Enum):
    PAYMENT = "payment"
    ADVANCE_PAYMENT = "advance_payment"
    REFUND = "refund"

# payments API
@router.post("/payments")
def create_payment(payment: PaymentCreate):
    customer = get_customer(payment.customer_id)

    # Determine payment type
    if customer.balance >= 0:
        payment.type = PaymentType.ADVANCE_PAYMENT
        if not payment.notes:
            raise ValueError("Notes required for advance payments")

    # Update balance (can go positive)
    customer.balance += payment.amount

    return payment
```

## Testing Requirements
- Create payment for customer with zero balance
- Create payment for customer with positive balance
- Verify balance increases correctly
- Verify transaction type is ADVANCE_PAYMENT
- Test notes validation (required for advances)
- Verify UI shows credit in green
- Test statement includes advance payments

## UI/UX Considerations
- Show "Adelanto de Pago" title when no debt exists
- Display current balance before payment
- Show resulting credit after payment
- Use success color (green) for positive balances
- Add helper text explaining advance payments

## Dev Notes
- Consider maximum advance payment limit
- Ensure proper audit trail for advances
- Think about refund process for unused credit

---

## Dev Agent Record

### Task Progress
- [ ] Update payment model
- [ ] Modify payment validation
- [ ] Update UI for advances
- [ ] Implement balance display
- [ ] Add tests

### Debug Log

### Completion Notes

### File List

### Change Log

### Agent Model Used
