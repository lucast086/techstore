# STORY-072: Repair to Invoice Integration

**Status:** Ready for Review
**Priority:** P1 (High)
**Type:** New Feature
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As a cashier, when I mark a repair as "delivered", I need the system to automatically redirect me to the POS with the repair pre-loaded as a line item for invoicing.

## Business Value
- Streamlines repair billing workflow
- Reduces manual data entry errors
- Ensures all delivered repairs are invoiced
- Improves cashier efficiency

## Acceptance Criteria
- [x] Marking repair as "delivered" triggers redirect to `/sales/pos`
- [x] Repair appears as line item with description "Reparación #[ID] - [device]"
- [x] Price is set to repair's final_cost
- [x] Customer is pre-selected if repair has customer_id
- [x] Other products can still be added to the sale
- [x] After sale completion, repair is marked as paid
- [x] System prevents duplicate invoicing of same repair

## Technical Implementation

### Files to Modify
- `/src/app/api/v1/repairs.py` - Add redirect logic on status change
- `/src/app/web/sales.py` - Handle repair parameter in POS route
- `/src/app/templates/sales/pos.html` - Process repair pre-load
- `/src/app/models/reparacion.py` - Add sale_id reference field
- `/src/app/services/repair_service.py` - Add invoicing logic

### Tasks
- [x] Add sale_id field to repair model (nullable)
- [x] Modify delivered status endpoint to return redirect
- [x] Update POS route to accept repair_id parameter
- [x] Implement repair-to-cart conversion logic
- [x] Add validation to prevent re-invoicing
- [x] Update repair with sale_id after invoicing
- [x] Add UI feedback for repair invoicing
- [x] Create integration tests

### Implementation Flow
```python
# In repairs.py
@router.post("/repairs/{repair_id}/status")
def update_status(repair_id: int, status: str):
    if status == "delivered":
        # Update repair status
        repair.status = "delivered"

        # Return redirect response
        return {
            "redirect": f"/sales/pos?repair_id={repair_id}",
            "message": "Redirecting to invoice..."
        }

# In sales POS
@router.get("/sales/pos")
def pos_view(repair_id: Optional[int] = None):
    if repair_id:
        repair = get_repair(repair_id)
        # Pre-populate cart with repair
```

## Testing Requirements
- Mark repair as delivered → redirects to POS
- Repair appears correctly in cart
- Complete sale with repair item
- Verify repair.sale_id is updated
- Try to invoice same repair twice (should fail)
- Test with and without customer association

## Dev Notes
- Consider using HTMX redirect or JavaScript
- Ensure repair can only be invoiced once
- Handle edge case: repair marked delivered but not invoiced

---

## Dev Agent Record

### Task Progress
- [ ] Database migration for sale_id
- [ ] Update repair status endpoint
- [ ] Modify POS to accept repair
- [ ] Implement invoicing prevention
- [ ] Integration testing

### Debug Log

### Completion Notes

### File List

### Change Log

### Agent Model Used
