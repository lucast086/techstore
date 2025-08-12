# STORY-077: Analytics Dashboard for Admin Panel

**Status:** Draft
**Priority:** P2 (Medium)
**Type:** New Feature
**Epic:** [EPIC-007](./EPIC-007-system-improvements.md)

## Story
As an administrator, I need an analytics section in the admin panel with a dashboard that displays cash closings and can be filtered by date range.

## Business Value
- Provides business insights at a glance
- Enables data-driven decisions
- Improves financial oversight
- Identifies trends and patterns

## Acceptance Criteria
- [ ] New "Analytics" menu item in admin panel
- [ ] Dashboard shows list of cash closings
- [ ] Date range filter (from/to dates)
- [ ] Filter by cashier
- [ ] Display: date, cashier, opening, sales, expenses, closing
- [ ] Show period totals and averages
- [ ] Export data to CSV/Excel
- [ ] Responsive design for mobile viewing
- [ ] Loading states for data fetching

## Technical Implementation

### Files to Modify
- `/src/app/web/admin.py` - New analytics routes
- `/src/app/templates/admin/base.html` - Add Analytics menu
- `/src/app/templates/admin/analytics/dashboard.html` - Main view
- `/src/app/templates/admin/analytics/cash_closings.html` - Closings list
- `/src/app/services/analytics_service.py` - Business logic
- `/src/app/api/v1/analytics.py` - API endpoints

### Tasks
- [ ] Create analytics service layer
- [ ] Add analytics routes to admin
- [ ] Create dashboard template
- [ ] Implement date range picker
- [ ] Create cash closings query with filters
- [ ] Calculate period aggregates
- [ ] Implement CSV export
- [ ] Add charts/visualizations
- [ ] Create loading states
- [ ] Add pagination for large datasets

### Implementation Structure
```python
# analytics_service.py
class AnalyticsService:
    def get_cash_closings_summary(
        self,
        start_date: date,
        end_date: date,
        cashier_id: Optional[int] = None
    ):
        query = db.query(CashClosing).filter(
            CashClosing.date.between(start_date, end_date)
        )

        if cashier_id:
            query = query.filter(CashClosing.cashier_id == cashier_id)

        closings = query.all()

        return {
            "closings": closings,
            "totals": {
                "sales": sum(c.total_sales for c in closings),
                "expenses": sum(c.total_expenses for c in closings),
                "count": len(closings)
            },
            "averages": {
                "daily_sales": totals["sales"] / len(closings),
                "daily_expenses": totals["expenses"] / len(closings)
            }
        }
```

```html
<!-- Dashboard template structure -->
<div class="analytics-dashboard">
    <!-- Filters -->
    <div class="filters-section">
        <form method="GET">
            <input type="date" name="start_date" />
            <input type="date" name="end_date" />
            <select name="cashier_id">...</select>
            <button type="submit">Filtrar</button>
        </form>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards">
        <div class="card">
            <h3>Total Ventas</h3>
            <p class="value">${{ totals.sales }}</p>
        </div>
        <div class="card">
            <h3>Total Gastos</h3>
            <p class="value">${{ totals.expenses }}</p>
        </div>
    </div>

    <!-- Data Table -->
    <table class="closings-table">
        <!-- Table content -->
    </table>

    <!-- Export -->
    <button onclick="exportToCSV()">Exportar CSV</button>
</div>
```

## Testing Requirements
- Filter by various date ranges
- Filter by specific cashier
- Verify calculations are correct
- Test CSV export format
- Test with no data in range
- Test with large datasets
- Verify responsive design
- Test loading states

## Future Enhancements
- Add charts (sales trends, daily comparisons)
- More metrics (top products, customer analytics)
- Scheduled email reports
- Real-time dashboard updates
- Comparative analysis (period vs period)

## Dev Notes
- Consider using DataTables for advanced features
- Cache calculations for performance
- Add indexes for date queries
- Consider background jobs for heavy calculations

---

## Dev Agent Record

### Task Progress
- [ ] Create analytics service
- [ ] Add admin routes
- [ ] Build dashboard UI
- [ ] Implement filters
- [ ] Add export functionality
- [ ] Create visualizations

### Debug Log

### Completion Notes

### File List

### Change Log

### Agent Model Used
