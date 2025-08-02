# STORY-053: Update Repair Status

## 📋 Story Details
- **Epic**: EPIC-005 (Repair Management)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: READY_FOR_REVIEW

## 🎯 User Story
**As** Carlos or María,
**I want** to update repair status as work progresses,
**So that** everyone knows the current state of each repair

## ✅ Acceptance Criteria
1. [ ] Status update buttons on repair details
2. [ ] Valid status transitions enforced
3. [ ] Notes required for certain status changes
4. [ ] Timestamp all status changes
5. [ ] Show status history timeline
6. [ ] Auto-notify customer on key statuses (Diagnosed, Ready)
7. [ ] Visual status indicators (colors/icons)
8. [ ] Bulk status update for multiple repairs
9. [ ] Status change permissions by role
10. [ ] Undo last status change (within 5 minutes)

## 🔧 Technical Details

### Files to Update:
```
src/app/
├── services/
│   └── repair_service.py     # Status logic
├── api/v1/
│   └── repairs.py            # Status endpoints
├── web/
│   └── repairs.py            # Status routes
├── templates/
│   └── repairs/
│       ├── detail.html        # Repair details
│       └── partials/
│           ├── status_buttons.html
│           ├── status_timeline.html
│           └── status_modal.html
└── utils/
    └── status_workflow.py    # Status rules
```

### Implementation Requirements:

1. **Status Workflow** (`app/utils/status_workflow.py`):
   ```python
   REPAIR_STATUS_FLOW = {
       'received': ['diagnosing', 'cancelled'],
       'diagnosing': ['waiting_approval', 'repairing', 'cancelled'],
       'waiting_approval': ['approved', 'rejected'],
       'approved': ['repairing'],
       'repairing': ['testing', 'waiting_parts'],
       'waiting_parts': ['repairing'],
       'testing': ['ready', 'repairing'],
       'ready': ['delivered'],
       'delivered': [],
       'cancelled': [],
       'rejected': []
   }
   ```

2. **Status Service Updates**:
   - Validate transitions
   - Create history record
   - Send notifications
   - Handle bulk updates

3. **API Endpoints** (`app/api/v1/repairs.py`):
   - PUT /repairs/{id}/status - Update status
   - GET /repairs/{id}/history - Status history
   - POST /repairs/bulk-status - Bulk update

4. **Web Routes** (`app/web/repairs.py`):
   - POST /repairs/{id}/status - HTMX status update
   - GET /repairs/{id}/timeline - Status timeline

5. **Notification Logic**:
   - 'diagnosed' → Send estimate
   - 'ready' → Pickup notification
   - 'waiting_parts' → Delay notice

## 🧪 Testing Approach

### Unit Tests:
- Status transition validation
- History tracking
- Notification triggers

### Integration Tests:
- Complete status flow
- Bulk updates
- Permission checks

### UI Tests:
- Status button interactions
- Timeline display
- Modal forms

## 📦 Dependencies
- **Depends on**:
  - STORY-051 (Receive Repair)
  - STORY-052 (Diagnose Repair)
- **Blocks**:
  - STORY-054 (Deliver Repair)

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing
- [ ] Status workflow enforced
- [ ] History tracking accurate
- [ ] Notifications working
- [ ] UI updates real-time
- [ ] Permissions enforced
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Color coding: Green (ready), Yellow (in progress), Red (blocked)
- Consider email notifications option
- Add estimated time per status
- Track technician assignments

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
