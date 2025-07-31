# STORY-044: Refunds and Returns

## 📋 Story Details
- **Epic**: EPIC-004 (Sales Management)
- **Priority**: MEDIUM
- **Estimate**: 1.5 days
- **Status**: TODO

## 🎯 User Story
**As** María,
**I want** to process refunds and returns properly,
**So that** I can maintain customer satisfaction and accurate records

## ✅ Acceptance Criteria
1. [ ] Return form linked from sale details
2. [ ] Select products to return with quantities
3. [ ] Mandatory reason selection (defective, changed mind, wrong product, etc.)
4. [ ] Optional notes for additional details
5. [ ] Calculate refund amount automatically
6. [ ] Option for cash refund or store credit
7. [ ] Update inventory on return approval
8. [ ] Generate credit note with unique number
9. [ ] Link refund to original sale
10. [ ] Require manager authorization for high-value returns

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── models/
│   └── refund.py             # Refund model
├── schemas/
│   └── refund.py             # Refund schemas
├── crud/
│   └── refund.py             # Refund operations
├── api/v1/
│   └── refunds.py            # Refund endpoints
├── web/
│   └── refunds.py            # Refund routes
├── templates/
│   └── refunds/
│       ├── form.html         # Return form
│       ├── credit_note.html  # Credit note
│       └── partials/
│           └── return_item.html
└── services/
    └── refund_service.py     # Refund logic
```

### Implementation Requirements:

1. **Refund Model** (`app/models/refund.py`):
   - Link to original sale
   - Return items with quantities
   - Reason and status tracking
   - Credit note number

2. **Refund Service** (`app/services/refund_service.py`):
   - Validate returnable items
   - Calculate refund amounts
   - Update inventory
   - Generate credit note
   - Update customer balance

3. **API Endpoints** (`app/api/v1/refunds.py`):
   - POST /refunds - Create refund
   - GET /refunds/{id} - Get refund details
   - POST /refunds/{id}/approve - Approve refund

4. **Web Routes** (`app/web/refunds.py`):
   - GET /sales/{id}/return - Return form
   - POST /refunds/create - Process return
   - GET /refunds/{id}/credit-note - View credit note

5. **Authorization**:
   - High-value threshold configuration
   - Manager role check for approval
   - Audit trail for all refunds

## 🧪 Testing Approach

### Unit Tests:
- Refund calculation logic
- Inventory restoration
- Authorization rules
- Credit note generation

### Integration Tests:
- Complete refund flow
- Partial return handling
- Store credit application

### UI Tests:
- Return form functionality
- Reason selection
- Authorization flow

## 📦 Dependencies
- **Depends on**:
  - STORY-040 (Create Sale)
  - STORY-043 (Invoice Management)
  - STORY-022 (Role Management)
- **Blocks**:
  - None

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Credit notes generating
- [ ] Inventory updates verified
- [ ] Authorization working
- [ ] Customer balance updated
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Return window policy (e.g., 30 days)
- Consider restocking fees
- Track refund metrics
- Prevent duplicate returns

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
