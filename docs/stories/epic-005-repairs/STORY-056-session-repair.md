# STORY-056: Session Repair

## 📋 Story Details
- **Epic**: EPIC-005 (Repair Management)
- **Priority**: MEDIUM
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** Carlos,
**I want** to handle quick repairs done while customer waits,
**So that** simple issues can be resolved immediately

## ✅ Acceptance Criteria
1. [ ] Express repair option on reception form
2. [ ] Simplified workflow (receive → repair → deliver)
3. [ ] Timer starts on repair creation
4. [ ] Quick diagnosis notes
5. [ ] Immediate parts selection from common items
6. [ ] Skip approval step for low-cost repairs
7. [ ] Generate invoice instead of separate receipt
8. [ ] Customer waits indicator on repair
9. [ ] Priority queue display for session repairs
10. [ ] Average session time tracking

## 🔧 Technical Details

### Files to Update:
```
src/app/
├── schemas/
│   └── repair.py             # Express repair flag
├── services/
│   └── repair_service.py     # Express workflow
├── api/v1/
│   └── repairs.py            # Express endpoints
├── web/
│   └── repairs.py            # Express routes
├── templates/
│   └── repairs/
│       ├── express.html      # Express form
│       └── partials/
│           ├── session_timer.html
│           ├── quick_parts.html
│           └── express_queue.html
└── static/
    └── js/
        └── session_timer.js   # Timer functionality
```

### Implementation Requirements:

1. **Express Workflow**:
   - Flag is_express on creation
   - Auto-assign to available tech
   - Skip waiting_approval status
   - Direct to testing after repair
   - Combine delivery with payment

2. **Common Parts List**:
   - Screen protectors
   - Phone cases
   - Charging cables
   - Basic batteries
   - Common screws/parts

3. **API Endpoints** (`app/api/v1/repairs.py`):
   - POST /repairs/express - Create express
   - GET /repairs/express/queue - Active sessions
   - POST /repairs/{id}/complete-express

4. **Web Routes** (`app/web/repairs.py`):
   - GET /repairs/express - Express form
   - GET /repairs/express/queue - Queue view
   - POST /repairs/express/timer - Update timer

5. **Metrics**:
   - Average session time by type
   - Express repair success rate
   - Customer wait times
   - Revenue from express repairs

## 🧪 Testing Approach

### Unit Tests:
- Express workflow validation
- Timer calculations
- Quick parts selection

### Integration Tests:
- Complete express flow
- Queue management
- Concurrent sessions

### UI Tests:
- Timer functionality
- Queue updates
- Express form

## 📦 Dependencies
- **Depends on**:
  - STORY-051 (Receive Repair)
  - STORY-054 (Deliver Repair)
- **Blocks**:
  - None

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing
- [ ] Express workflow functional
- [ ] Timer working correctly
- [ ] Queue view updating
- [ ] Metrics tracking
- [ ] Mobile optimized
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Consider SMS updates for waiting customers
- Add estimated wait time display
- Common repairs price list
- Express repair guarantee terms

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
