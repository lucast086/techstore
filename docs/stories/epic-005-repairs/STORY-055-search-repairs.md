# STORY-055: Search Repairs

## 📋 Story Details
- **Epic**: EPIC-005 (Repair Management)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** Carlos or María,
**I want** to search and filter repair orders,
**So that** I can quickly find specific repairs or view workload

## ✅ Acceptance Criteria
1. [ ] Search by repair number (exact or partial)
2. [ ] Search by customer name or phone
3. [ ] Filter by current status (multi-select)
4. [ ] Filter by technician assigned
5. [ ] Filter by date range (received, completed)
6. [ ] Filter by device type or brand
7. [ ] Sort by age, priority, or status
8. [ ] Kanban view by status columns
9. [ ] Export filtered results to Excel
10. [ ] Save frequent searches

## 🔧 Technical Details

### Files to Update/Create:
```
src/app/
├── crud/
│   └── repair.py             # Search methods
├── api/v1/
│   └── repairs.py            # Search endpoints
├── web/
│   └── repairs.py            # Search routes
├── templates/
│   └── repairs/
│       ├── list.html          # Repair list/search
│       ├── kanban.html        # Kanban view
│       └── partials/
│           ├── repair_card.html
│           ├── search_filters.html
│           └── kanban_column.html
└── static/
    └── js/
        └── repair_search.js   # Search interactions
```

### Implementation Requirements:

1. **Search Operations** (`app/crud/repair.py`):
   - Advanced search with multiple criteria
   - Full-text search on descriptions
   - Efficient pagination
   - Count by status for overview

2. **API Endpoints** (`app/api/v1/repairs.py`):
   - GET /repairs - List with filters
   - GET /repairs/search - Advanced search
   - GET /repairs/stats - Status counts
   - GET /repairs/export - Export data

3. **Web Routes** (`app/web/repairs.py`):
   - GET /repairs - List view
   - GET /repairs/kanban - Kanban view
   - POST /repairs/filter - HTMX filter
   - GET /repairs/export - Download Excel

4. **Views**:
   - **List View**: Traditional table
   - **Kanban View**: Drag-drop status
   - Quick stats dashboard
   - Mobile-optimized cards

5. **Performance**:
   - Index key search fields
   - Cache status counts
   - Lazy load in kanban
   - Optimize queries

## 🧪 Testing Approach

### Unit Tests:
- Search query building
- Filter combinations
- Sort functionality

### Integration Tests:
- Search accuracy
- Export functionality
- View switching

### UI Tests:
- Filter interactions
- Kanban drag-drop
- Mobile responsiveness

## 📦 Dependencies
- **Depends on**:
  - STORY-051 (Receive Repair)
- **Blocks**:
  - None

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing
- [ ] Search returning accurate results
- [ ] Filters working correctly
- [ ] Kanban view functional
- [ ] Export working
- [ ] Performance < 1s
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Add quick filters for common searches
- Color code by age/urgency
- Include repair age indicator
- Saved search preferences

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
