# Story 007.079: Allow Diagnosis Editing Until Final States

## Status
Draft

## Story
**As a** repair technician,
**I want** to be able to edit the diagnosis at any point before the repair is ready, delivered, or cancelled,
**so that** I can update incorrect or incomplete diagnoses discovered during the repair process without creating a new repair order.

## Acceptance Criteria
1. The "Edit Diagnosis" button/option must be visible and enabled for repairs in states: received, diagnosing, approved, repairing, testing
2. The "Edit Diagnosis" button/option must be disabled (grayed out) for repairs in states: ready, delivered, cancelled
3. When diagnosis is edited from any allowed state, the repair status must automatically change to "diagnosing"
4. The diagnosis edit form must pre-populate with the existing diagnosis information
5. After saving an edited diagnosis, a status history entry must be created showing the transition to "diagnosing"
6. The UI must clearly indicate when diagnosis editing is not allowed with appropriate messaging
7. All existing diagnosis data (problem description, estimated cost, notes) must be editable
8. The system must maintain an audit trail of diagnosis changes in the repair history

## Tasks / Subtasks
- [ ] Backend: Update repair service to allow diagnosis editing (AC: 1, 2, 3)
  - [ ] Add method `can_edit_diagnosis()` to check if current status allows editing
  - [ ] Modify diagnosis update endpoint to accept repairs in multiple states
  - [ ] Add automatic status change to "diagnosing" when diagnosis is edited
  - [ ] Ensure status history is properly recorded
- [ ] Backend: Add validation for diagnosis editing restrictions (AC: 2, 6)
  - [ ] Return appropriate error messages when editing is not allowed
  - [ ] Add unit tests for each status scenario
- [ ] Frontend: Update repair detail page UI (AC: 1, 2, 4, 6)
  - [ ] Show/hide edit diagnosis button based on repair status
  - [ ] Add visual indicator (disabled state) when editing is not allowed
  - [ ] Add tooltip or message explaining why editing is disabled
- [ ] Frontend: Update diagnosis edit form (AC: 4, 7)
  - [ ] Ensure form loads with current diagnosis data
  - [ ] Maintain all existing fields as editable
- [ ] Testing: Comprehensive test coverage (AC: 1-8)
  - [ ] Test diagnosis editing from each allowed state
  - [ ] Test blocking of diagnosis editing in restricted states
  - [ ] Test status transition to "diagnosing"
  - [ ] Test audit trail creation
- [ ] Documentation: Update user documentation
  - [ ] Document the new diagnosis editing workflow
  - [ ] Add notes about status restrictions

## Dev Notes

### Relevant Source Tree
- `/workspace/src/app/models/repair.py` - Repair and RepairStatusHistory models
- `/workspace/src/app/schemas/repair.py` - RepairStatus enum with states: RECEIVED, DIAGNOSING, APPROVED, REPAIRING, TESTING, READY, DELIVERED, CANCELLED
- `/workspace/src/app/services/repair_service.py` - Core repair business logic
- `/workspace/src/app/api/v1/endpoints/repairs.py` - Repair API endpoints
- `/workspace/src/app/web/routes/repairs.py` - HTMX web routes for repairs
- `/workspace/templates/repairs/` - Repair UI templates

### Key Implementation Details
1. **Status Restrictions**:
   - Allowed states for editing: received, diagnosing, approved, repairing, testing
   - Blocked states: ready, delivered, cancelled

2. **Status Transition Logic**:
   - Any edit to diagnosis from an allowed state must trigger immediate transition to "diagnosing"
   - This is a business rule to ensure proper workflow - if diagnosis changes, the repair needs re-evaluation

3. **Existing Diagnosis Fields** (from schemas):
   - problem_description
   - diagnosis_notes
   - estimated_cost
   - diagnosed_at (timestamp)

4. **Status History**:
   - Must create RepairStatusHistory entry for the transition
   - Include appropriate notes about diagnosis being edited

### Testing Standards
- Test files location: `/workspace/tests/test_services/test_repair_service.py` and `/workspace/tests/test_api/test_repairs.py`
- Use pytest framework with fixtures from conftest.py
- Follow existing test patterns for service and API layers
- Ensure both positive and negative test cases
- Mock database sessions using pytest fixtures
- Test HTMX responses for web routes

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-01-23 | 1.0 | Initial story creation | Sarah (PO) |

## Dev Agent Record

### Agent Model Used
[To be populated by dev agent]

### Debug Log References
[To be populated by dev agent]

### Completion Notes List
[To be populated by dev agent]

### File List
[To be populated by dev agent]

## QA Results
[To be populated by QA agent]
