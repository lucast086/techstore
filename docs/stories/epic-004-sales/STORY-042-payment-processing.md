# STORY-042: Payment Processing

## 📋 Story Details
- **Epic**: EPIC-004 (Sales Management)
- **Priority**: HIGH
- **Estimate**: 1.5 days
- **Status**: TODO

## 🎯 User Story
**As** María,
**I want** to record customer payments for credit sales,
**So that** I can track customer account balances accurately

## ✅ Acceptance Criteria
1. [ ] Payment form accessible from customer profile and sales
2. [ ] Record partial or full payments
3. [ ] Support multiple payment methods in one transaction
4. [ ] Auto-calculate remaining balance
5. [ ] Update customer account balance immediately
6. [ ] Generate payment receipt with unique number
7. [ ] Payment history visible on customer profile
8. [ ] Send WhatsApp receipt to customer
9. [ ] Prevent overpayment without authorization
10. [ ] Reference number field for bank transfers

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── api/v1/
│   └── payments.py           # Payment API endpoints
├── web/
│   └── payments.py           # Payment web routes
├── schemas/
│   └── payment.py            # Payment schemas
├── crud/
│   └── payment.py            # Payment operations
├── templates/
│   └── payments/
│       ├── form.html         # Payment form
│       ├── receipt.html      # Payment receipt
│       └── partials/
│           ├── payment_method.html
│           └── balance_display.html
└── services/
    └── payment_service.py    # Payment logic
```

### Implementation Requirements:

1. **Payment Schema** (`app/schemas/payment.py`):
   - CreatePayment with amount, methods, reference
   - PaymentMethod with type and amount
   - PaymentReceipt response model

2. **Payment Service** (`app/services/payment_service.py`):
   - Process payment with validation
   - Update customer balance
   - Generate receipt number
   - Handle mixed payment methods

3. **API Endpoints** (`app/api/v1/payments.py`):
   - POST /payments - Process payment
   - GET /payments/customer/{id} - Customer payments
   - GET /payments/receipt/{id} - Get receipt

4. **Web Routes** (`app/web/payments.py`):
   - GET /payments/new - Payment form
   - POST /payments/process - Process payment
   - GET /payments/receipt/{id} - View receipt

5. **Integration**:
   - Update customer balance calculation
   - Add payment links to customer profile
   - Show outstanding balances in POS

## 🧪 Testing Approach

### Unit Tests:
- Payment validation logic
- Balance calculations
- Mixed payment processing
- Receipt generation

### Integration Tests:
- Payment flow with customer update
- Concurrent payment handling
- Balance accuracy after payment

### UI Tests:
- Payment form validation
- Method selection
- Receipt display

## 📦 Dependencies
- **Depends on**:
  - STORY-032 (Customer Account Balance)
  - STORY-040 (Create Sale)
- **Blocks**:
  - None

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Payment receipts generating
- [ ] Customer balances updating correctly
- [ ] WhatsApp integration tested
- [ ] Transaction integrity verified
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Payment numbering: PAY-YYYY-NNNNN
- Consider payment reversal workflow
- Add payment reminder scheduling
- Track payment methods for reporting

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
