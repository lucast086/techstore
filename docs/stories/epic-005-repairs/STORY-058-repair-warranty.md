# STORY-058: Repair Warranty

## 📋 Story Details
- **Epic**: EPIC-005 (Repair Management)
- **Priority**: MEDIUM
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** María or Carlos,
**I want** to track repair warranties,
**So that** warranty claims are handled properly

## ✅ Acceptance Criteria
1. [ ] Set warranty period on delivery (default 30 days)
2. [ ] Warranty lookup by repair number or customer
3. [ ] Check warranty validity with expiry date
4. [ ] Link warranty repair to original
5. [ ] Warranty claim workflow
6. [ ] Different warranty for parts vs labor
7. [ ] Warranty terms display/print
8. [ ] Warranty statistics report
9. [ ] Email warranty expiry reminders
10. [ ] Void warranty for specific conditions

## 🔧 Technical Details

### Files to Update/Create:
```
src/app/
├── models/
│   └── warranty.py           # Warranty model
├── schemas/
│   └── warranty.py           # Warranty schemas
├── crud/
│   └── warranty.py           # Warranty operations
├── api/v1/
│   └── warranties.py         # Warranty endpoints
├── web/
│   └── warranties.py         # Warranty routes
├── templates/
│   └── warranties/
│       ├── lookup.html       # Warranty lookup
│       ├── claim.html        # Claim form
│       ├── terms.html        # Terms template
│       └── partials/
│           └── warranty_status.html
└── services/
    └── warranty_service.py   # Warranty logic
```

### Implementation Requirements:

1. **Warranty Model** (`app/models/warranty.py`):
   - Link to repair
   - Start/end dates
   - Coverage type
   - Claim history
   - Void status

2. **Warranty Service** (`app/services/warranty_service.py`):
   - Create warranty on delivery
   - Validate warranty claims
   - Process claims
   - Track claim patterns
   - Send reminders

3. **API Endpoints** (`app/api/v1/warranties.py`):
   - GET /warranties/check - Validate warranty
   - POST /warranties/claim - Create claim
   - GET /warranties/report - Statistics
   - PUT /warranties/{id}/void - Void warranty

4. **Web Routes** (`app/web/warranties.py`):
   - GET /warranties - Lookup page
   - GET /warranties/{id} - Details
   - GET /warranties/claim/{id} - Claim form
   - GET /warranties/terms - Terms page

5. **Warranty Rules**:
   - Parts: 90 days
   - Labor: 30 days
   - Screen: 7 days
   - Software: No warranty
   - Water damage voids

## 🧪 Testing Approach

### Unit Tests:
- Warranty creation
- Validity checking
- Claim validation
- Rule application

### Integration Tests:
- Claim workflow
- Reminder sending
- Report generation

### UI Tests:
- Lookup functionality
- Claim submission
- Terms display

## 📦 Dependencies
- **Depends on**:
  - STORY-054 (Deliver Repair)
- **Blocks**:
  - None

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing
- [ ] Warranty tracking functional
- [ ] Claims process working
- [ ] Lookup accurate
- [ ] Reports generating
- [ ] Terms customizable
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Consider extended warranty sales
- Track warranty cost vs revenue
- Multiple warranty tiers
- Warranty transfer option

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
