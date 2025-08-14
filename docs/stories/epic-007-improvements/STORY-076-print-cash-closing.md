# STORY-076: Direct Print Cash Closing

**Status:** Ready for Review
**Priority:** P2 (Medium)
**Type:** UX Improvement
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As a cashier, I want to print the cash closing report directly from the browser without having to download the PDF first.

## Current Behavior
- User must click "Download PDF"
- Save PDF to computer
- Open PDF
- Print from PDF viewer

## Desired Behavior
- Click "Print" button
- Browser print dialog opens immediately
- Print directly without intermediate steps

## Acceptance Criteria
- [x] Add "Imprimir" button next to "Descargar PDF"
- [x] Button triggers browser print dialog directly
- [x] Print view is properly formatted for paper
- [x] Navigation and buttons hidden in print view
- [x] Page breaks are logical (no cut tables)
- [x] Header/footer appropriate for printing
- [x] Original PDF download still works

## Technical Implementation

### Files to Modify
- `/src/app/templates/cash_closings/detail.html` - Add print button
- `/src/app/static/css/print.css` - Print-specific styles
- `/src/app/templates/base.html` - Include print CSS

### Tasks
- [ ] Add print button to cash closing detail
- [ ] Create JavaScript print function
- [ ] Create print.css with @media print rules
- [ ] Hide non-printable elements
- [ ] Format tables for printing
- [ ] Add page break rules
- [ ] Test in multiple browsers
- [ ] Ensure A4 and Letter compatibility

### Implementation
```html
<!-- Add to cash_closings/detail.html -->
<button onclick="window.print()"
        class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
    <svg class="w-4 h-4 inline mr-2">...</svg>
    Imprimir
</button>
```

```css
/* print.css */
@media print {
    /* Hide navigation and buttons */
    nav, .no-print, button, .sidebar {
        display: none !important;
    }

    /* Format for printing */
    body {
        font-size: 12pt;
        color: black;
        background: white;
    }

    /* Avoid breaking tables */
    table {
        page-break-inside: avoid;
    }

    /* Add page margins */
    @page {
        margin: 2cm;
    }

    /* Header for each page */
    .print-header {
        position: running(header);
    }
}
```

```javascript
// Optional: Enhanced print function
function printCashClosing() {
    // Store current title
    const originalTitle = document.title;

    // Set print-friendly title
    document.title = `Cierre de Caja - ${closingDate}`;

    // Trigger print
    window.print();

    // Restore title
    document.title = originalTitle;
}
```

## Testing Requirements
- Test print in Chrome, Firefox, Safari
- Verify layout in print preview
- Check page breaks don't cut content
- Test with long transaction lists
- Verify all data is visible
- Check margins and spacing
- Test landscape vs portrait

## Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Test print margins
- Mobile: Consider alternative approach

## Dev Notes
- Consider using CSS Grid for print layout
- May need JavaScript for complex formatting
- Consider adding print date/time
- Think about signature lines for physical filing

---

## Dev Agent Record

### Task Progress
- [x] Add print button
- [x] Create print stylesheet
- [x] Hide non-printable elements
- [x] Format for paper
- [x] Test across browsers

### Debug Log

### Completion Notes
- Created dedicated receipt template for cash closings following payment receipt pattern
- Added /cash-closings/{id}/print route for clean print view
- Optimized print layout for A5 size (half A4 page) with ultra-compact typography
- Print template opens in new tab with automatic print dialog
- All navigation and UI elements hidden in print mode
- Maintains all essential cash closing information in compact format

### File List
- `/src/app/templates/cash_closings/receipt.html` - New print-optimized template
- `/src/app/templates/cash_closings/detail.html` - Updated print button
- `/src/app/web/cash_closings.py` - Added print route

### Change Log
- 2025-08-13: Created dedicated cash closing receipt template
- 2025-08-13: Added print route and updated detail template
- 2025-08-13: Optimized print layout for A5 size with compact formatting

### Agent Model Used
claude-sonnet-4-20250514
