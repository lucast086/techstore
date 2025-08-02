# STORY-041: Sales History

## 📋 Story Details
- **Epic**: EPIC-004 (Sales Management)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: READY_FOR_REVIEW

## 🎯 User Story
**As** María or Pedro,
**I want** to view and filter sales history,
**So that** I can track business performance and find specific transactions

## ✅ Acceptance Criteria
1. [ ] Sales list page with pagination (20 per page)
2. [ ] Filter by date range with date pickers
3. [ ] Filter by customer (searchable dropdown)
4. [ ] Filter by user/cashier
5. [ ] Filter by payment method and status
6. [ ] Search by invoice number
7. [ ] View detailed sale information in modal
8. [ ] Export filtered results to Excel/PDF
9. [ ] Show daily/weekly/monthly totals
10. [ ] Quick filters for today, yesterday, this week, this month

## 🔧 Technical Details

### Files to Update/Create:
```
src/app/
├── api/v1/
│   └── sales.py              # Add history endpoints
├── web/
│   └── sales.py              # Add history routes
├── crud/
│   └── sale.py               # Add query methods
├── templates/
│   └── sales/
│       ├── history.html      # Sales history page
│       └── partials/
│           ├── sale_row.html
│           ├── sale_detail_modal.html
│           └── filters.html
└── utils/
    └── export.py             # Export functionality
```

### Implementation Requirements:

1. **CRUD Operations** (`app/crud/sale.py`):
   - get_sales_paginated with filters
   - get_sales_summary by period
   - get_sale_details with items

2. **API Endpoints** (`app/api/v1/sales.py`):
   - GET /sales - List with filters
   - GET /sales/{id} - Sale details
   - GET /sales/export - Export data
   - GET /sales/summary - Period summaries

3. **Web Routes** (`app/web/sales.py`):
   - GET /sales/history - History page
   - GET /sales/history/filter - HTMX filter results
   - GET /sales/history/{id} - Detail modal

4. **Frontend** (`templates/sales/history.html`):
   - Responsive table with key info
   - Advanced filter sidebar
   - Summary cards at top
   - Export buttons

## 🧪 Testing Approach

### Unit Tests:
- Filter query building
- Summary calculations
- Export data formatting

### Integration Tests:
- Pagination with filters
- Date range queries
- Export generation

### UI Tests:
- Filter interactions
- Modal display
- Export downloads

## 📦 Dependencies
- **Depends on**:
  - STORY-040 (Create Sale)
- **Blocks**:
  - STORY-045 (Sales Analytics)

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Export functionality verified
- [ ] Performance: Page load < 1 second
- [ ] Filters working correctly
- [ ] Summary calculations accurate
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Consider caching for summary calculations
- Export format should match accounting needs
- Date filters should respect timezone
- Include voided sales with indicator

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
