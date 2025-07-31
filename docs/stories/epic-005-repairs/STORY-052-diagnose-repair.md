# STORY-052: Diagnose Repair

## 📋 Story Details
- **Epic**: EPIC-005 (Repair Management)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** Carlos,
**I want** to document device diagnosis and repair plan,
**So that** I can provide accurate estimates and track work needed

## ✅ Acceptance Criteria
1. [ ] Diagnosis form accessible from repair details
2. [ ] Detailed diagnosis notes field
3. [ ] Problem category selection (Hardware, Software, Both)
4. [ ] Required parts list with cost entry
5. [ ] Labor time estimation in hours
6. [ ] Auto-calculate total repair cost
7. [ ] Alternative solution options
8. [ ] Photo documentation of issues
9. [ ] Save draft diagnosis for later
10. [ ] Send estimate to customer via WhatsApp

## 🔧 Technical Details

### Files to Update/Create:
```
src/app/
├── schemas/
│   └── repair.py             # Add diagnosis schemas
├── crud/
│   └── repair.py             # Add diagnosis methods
├── api/v1/
│   └── repairs.py            # Add diagnosis endpoints
├── web/
│   └── repairs.py            # Add diagnosis routes
├── templates/
│   └── repairs/
│       ├── diagnose.html     # Diagnosis form
│       └── partials/
│           ├── parts_list.html
│           └── cost_calculator.html
└── models/
    └── repair_part.py        # Parts tracking
```

### Implementation Requirements:

1. **Diagnosis Schema** (`app/schemas/repair.py`):
   - DiagnosisCreate with notes, parts, labor
   - RepairPart with name, cost, quantity
   - CostEstimate calculation model

2. **CRUD Operations** (`app/crud/repair.py`):
   - update_diagnosis method
   - add_repair_parts
   - calculate_total_cost
   - get_parts_by_repair

3. **API Endpoints** (`app/api/v1/repairs.py`):
   - PUT /repairs/{id}/diagnosis - Save diagnosis
   - POST /repairs/{id}/parts - Add parts
   - GET /repairs/{id}/estimate - Get estimate

4. **Web Routes** (`app/web/repairs.py`):
   - GET /repairs/{id}/diagnose - Diagnosis form
   - POST /repairs/{id}/diagnose - Save diagnosis
   - POST /repairs/{id}/send-estimate - Send to customer

5. **Cost Calculation**:
   - Parts cost + markup
   - Labor rate configuration
   - Tax calculation if applicable
   - Round to nearest currency unit

## 🧪 Testing Approach

### Unit Tests:
- Cost calculation accuracy
- Parts list management
- Labor estimation

### Integration Tests:
- Diagnosis save flow
- Estimate generation
- Status update to 'diagnosed'

### UI Tests:
- Parts addition/removal
- Cost auto-calculation
- Photo upload

## 📦 Dependencies
- **Depends on**:
  - STORY-051 (Receive Repair)
- **Blocks**:
  - STORY-053 (Update Status)
  - STORY-054 (Deliver Repair)

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing
- [ ] Cost calculations accurate
- [ ] Parts tracking working
- [ ] Estimate generation tested
- [ ] WhatsApp integration working
- [ ] Draft save functionality
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Consider parts inventory integration
- Add common problems template
- Labor rate by repair type
- Supplier price lookup feature

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
