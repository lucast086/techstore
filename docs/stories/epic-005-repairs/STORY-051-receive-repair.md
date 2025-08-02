# STORY-051: Receive Repair

## 📋 Story Details
- **Epic**: EPIC-005 (Repair Management)
- **Priority**: HIGH
- **Estimate**: 1.5 days
- **Status**: READY_FOR_REVIEW

## 🎯 User Story
**As** Carlos or María,
**I want** to register new repair orders quickly,
**So that** customers receive proper documentation and devices are tracked

## ✅ Acceptance Criteria
1. [ ] Repair form accessible from main menu
2. [ ] Customer search/selection (required)
3. [ ] Device type dropdown (Phone, Tablet, Laptop, Other)
4. [ ] Brand and model fields
5. [ ] Problem description text area (required)
6. [ ] Device condition notes
7. [ ] Accessories checklist (charger, case, etc.)
8. [ ] Photo upload for device condition
9. [ ] Generate repair receipt with unique ID (REP-YYYY-NNNNN)
10. [ ] WhatsApp receipt to customer automatically

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── models/
│   └── repair.py             # Repair model
├── schemas/
│   └── repair.py             # Repair schemas
├── crud/
│   └── repair.py             # Repair operations
├── api/v1/
│   └── repairs.py            # Repair endpoints
├── web/
│   └── repairs.py            # Repair routes
├── templates/
│   └── repairs/
│       ├── receive.html      # Reception form
│       ├── receipt.html      # Repair receipt
│       └── partials/
│           ├── device_form.html
│           └── accessories_checklist.html
└── services/
    └── repair_service.py     # Repair logic
```

### Implementation Requirements:

1. **Repair Model** (`app/models/repair.py`):
   - All fields from schema
   - Status enum with workflow
   - Relationships to customer, users
   - Timestamps for tracking

2. **Repair Service** (`app/services/repair_service.py`):
   - Generate repair number
   - Create initial status
   - Send notifications
   - Handle photo uploads

3. **API Endpoints** (`app/api/v1/repairs.py`):
   - POST /repairs - Create repair
   - GET /repairs/{id} - Get repair details
   - POST /repairs/{id}/photos - Upload photos

4. **Web Routes** (`app/web/repairs.py`):
   - GET /repairs/new - Reception form
   - POST /repairs/create - Process form
   - GET /repairs/{id}/receipt - View receipt

5. **Frontend** (`templates/repairs/receive.html`):
   - Clean form layout
   - Customer autocomplete
   - Dynamic accessory list
   - Photo preview
   - Print receipt button

## 🧪 Testing Approach

### Unit Tests:
- Repair number generation
- Model validation
- Status initialization

### Integration Tests:
- Complete reception flow
- Customer association
- Notification sending

### UI Tests:
- Form validation
- Photo upload
- Receipt generation

## 📦 Dependencies
- **Depends on**:
  - STORY-028 (Customer Model)
  - STORY-027 (Database Setup)
- **Blocks**:
  - STORY-052 (Diagnose Repair)
  - STORY-053 (Update Status)

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Receipt generation working
- [ ] WhatsApp notification sent
- [ ] Photo upload functional
- [ ] Repair number unique
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Consider barcode/QR for repair tracking
- Template accessories by device type
- Add signature capture for legal protection
- Estimated completion date calculation

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
