# STORY-071: Fix Repair Cost Calculation in Diagnosis Modal

**Status:** Ready for Review
**Priority:** P0 (Critical)
**Type:** Bug Fix
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As a technician, when I enter labor cost and parts cost in the repair diagnosis modal, I need the total to calculate and display correctly in real-time.

## Current Behavior (Bug)
- Total cost does not update when entering labor cost
- Total cost does not update when entering parts cost
- Sum is not calculated or displayed incorrectly
- Values may not save correctly to database

## Expected Behavior
- Total updates automatically as costs are entered
- Total = labor_cost + parts_cost
- All values display with proper currency formatting
- Values save correctly to database

## Acceptance Criteria
- [x] Total updates in real-time when labor cost changes
- [x] Total updates in real-time when parts cost changes
- [x] Calculation formula: total = labor_cost + parts_cost
- [x] Currency format displays correctly ($X.XX)
- [x] Values persist correctly in database
- [x] Modal shows visual feedback during calculation

## Technical Implementation

### Files to Modify
- `/src/app/templates/repairs/detail.html` - Modal JavaScript
- `/src/app/templates/repairs/_diagnosis_modal.html` - If exists separately
- `/src/app/static/js/repairs.js` - If JavaScript is external
- `/src/app/api/v1/repairs.py` - Backend validation

### Tasks
- [x] Inspect current modal implementation
- [x] Identify JavaScript calculation error
- [x] Fix real-time calculation logic
- [x] Add input validation for numeric values
- [x] Ensure proper number formatting
- [x] Test backend data persistence
- [x] Add error handling for invalid inputs

### JavaScript Fix Example
```javascript
function updateTotalCost() {
    const laborCost = parseFloat(document.getElementById('labor_cost').value) || 0;
    const partsCost = parseFloat(document.getElementById('parts_cost').value) || 0;
    const total = laborCost + partsCost;

    document.getElementById('total_cost').value = total.toFixed(2);
    document.getElementById('total_display').textContent = `$${total.toFixed(2)}`;
}

// Attach listeners
document.getElementById('labor_cost').addEventListener('input', updateTotalCost);
document.getElementById('parts_cost').addEventListener('input', updateTotalCost);
```

## Testing Requirements
- Enter only labor cost, verify total
- Enter only parts cost, verify total
- Enter both costs, verify sum
- Test with decimal values
- Test with zero values
- Test with invalid characters (should handle gracefully)
- Verify database saves correct values

## Dev Notes
- Check if using vanilla JS or Alpine.js
- Ensure no conflicts with HTMX if present
- Consider adding debounce for performance

---

## Dev Agent Record

### Task Progress
- [ ] Fix JavaScript calculation
- [ ] Add input validation
- [ ] Test all scenarios
- [ ] Verify backend integration

### Debug Log

### Completion Notes

### File List

### Change Log

### Agent Model Used
