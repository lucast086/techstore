# STORY-065: Monthly Closing Summary

## 📋 Story Details
- **Epic**: EPIC-006 (Cash Management and Closings)
- **Priority**: MEDIUM
- **Estimate**: 1.5 days
- **Status**: TODO

## 🎯 User Story
**As** Pedro,
**I want** to generate monthly closing summaries,
**So that** I can review financial performance and prepare accounting reports.

## ✅ Acceptance Criteria
1. [ ] Monthly closing accessible from reports menu (Admin only)
2. [ ] Automatically aggregate all daily closings for selected month
3. [ ] Include:
   - Total revenue (sales)
   - Total expenses by category
   - Net profit/loss
   - Daily closing summary table
   - Graphs for visual analysis
4. [ ] Export options: PDF, Excel
5. [ ] Compare with previous months
6. [ ] Email to configured recipients

## 🔧 Technical Tasks
### 1. Create Monthly Summary Model (AC: 2, 3)
- [ ] Create `MonthlyClosingSummary` model in `src/app/models/cash_closing.py`
  - Fields: id, year, month, total_revenue, total_expenses, net_profit, daily_closings_count, generated_by, generated_at
  - Store calculated values for performance
  - Unique constraint on (year, month)

### 2. Create Schemas for Monthly Reports (AC: 3, 4)
- [ ] Extend schemas in `src/app/schemas/cash_closing.py`
  - `MonthlyReportRequest`: year, month, comparison_months
  - `MonthlyReportResponse`: Complete report data
  - `DailyClosingSummary`: Summary data for table
  - `ExpenseCategorySummary`: Expenses grouped by category
  - `MonthlyComparison`: Multi-month comparison data

### 3. Implement Monthly Report Service (AC: 2, 3, 5)
- [ ] Extend service in `src/app/services/cash_closing_service.py`
  - `generate_monthly_report()`: Main report generation
  - `aggregate_daily_closings()`: Sum all daily data
  - `calculate_expense_categories()`: Group expenses
  - `compare_months()`: Multi-month analysis
  - `cache_monthly_summary()`: Store for performance

### 4. Add Chart Data Generation (AC: 3)
- [ ] Create chart service in `src/app/services/chart_service.py`
  - `generate_daily_revenue_chart()`: Daily revenue line chart
  - `generate_expense_pie_chart()`: Expenses by category
  - `generate_profit_trend_chart()`: Multi-month profit trends
  - Return data in Chart.js format

### 5. Implement Export Services (AC: 4)
- [ ] Create export service in `src/app/services/export_service.py`
  - `export_monthly_pdf()`: Professional PDF report
  - `export_monthly_excel()`: Excel with multiple sheets
  - Include charts in PDF export
  - Use openpyxl for Excel generation

### 6. Create API Endpoints (AC: 1, 4, 6)
- [ ] Add routes to `src/app/api/v1/reports.py`
  - `GET /reports/monthly/{year}/{month}`: Get monthly report
  - `GET /reports/monthly/{year}/{month}/pdf`: Export PDF
  - `GET /reports/monthly/{year}/{month}/excel`: Export Excel
  - `POST /reports/monthly/{year}/{month}/email`: Send via email
  - `GET /reports/monthly/comparison`: Multi-month comparison

### 7. Create Web Interface (AC: 1, 3, 5)
- [ ] Add routes to `src/app/web/reports.py`
  - Route for monthly report page
  - HTMX endpoints for month selection
- [ ] Create templates in `src/app/templates/reports/`
  - `monthly_report.html`: Main report page
  - `_monthly_summary.html`: Summary section
  - `_daily_table.html`: Daily closings table
  - `_expense_breakdown.html`: Category breakdown

### 8. Add Chart Integration (AC: 3)
- [ ] Integrate Chart.js for visual reporting
  - Add Chart.js to base template
  - Create chart components for each report type
  - Make charts responsive and interactive
  - Add data export from charts

### 9. Email Report Service (AC: 6)
- [ ] Implement email reporting
  - HTML email template with summary
  - Attach PDF and Excel exports
  - Schedule automatic monthly reports
  - Configure recipient lists

### 10. Write Tests
- [ ] Unit tests for report calculations
- [ ] Service tests for data aggregation
- [ ] API tests for all endpoints
- [ ] Test export functionality
- [ ] Test email service (mocked)
- [ ] Integration tests with daily closings

## 📝 Dev Notes

### Data Aggregation
**Performance Considerations** [Source: architecture/coding-standards.md#performance-standards]
- Cache monthly summaries to avoid recalculation
- Use database aggregation functions
- Index daily closings by date for fast queries
- Consider materialized views for complex reports

### Previous Story Dependencies
- STORY-060: CashClosing model with daily data
- STORY-062: Expense model for category summaries
- Daily closings must exist to generate monthly reports

### Chart Implementation [Source: architecture/tech-stack.md#frontend]
- Use Chart.js for client-side charts
- Generate chart data on server
- Make charts responsive for mobile
- Export chart images for PDF reports

### Export Services
**PDF Generation**: Use reportlab or weasyprint
**Excel Generation**: Use openpyxl for advanced features
- Multiple sheets: Summary, Daily Details, Expenses
- Charts embedded in Excel
- Professional formatting

### Security Requirements [Source: architecture/coding-standards.md#security-protocols]
- Admin-only access to reports
- Audit logging for report generation
- Secure file downloads with tokens
- Email security for attachments

### Email Service
**Configuration**: Email settings in environment
**Templates**: HTML email with inline styles
**Attachments**: PDF and Excel files
**Scheduling**: Consider background tasks for automation

### Caching Strategy [Source: architecture/coding-standards.md#performance-standards]
- Cache generated reports for 24 hours
- Invalidate cache when new daily closing added
- Use Redis if available, memory cache otherwise

### Testing Strategy [Source: architecture/coding-standards.md#testing-standards]
- Mock external services (email)
- Test with various date ranges
- Verify calculation accuracy
- Test export file generation

## 🧪 Testing Requirements
- Report calculation accuracy tests
- Data aggregation tests
- Export functionality tests
- Chart data generation tests
- Email service tests (mocked)
- Cache invalidation tests
- Multi-month comparison tests

## 📋 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-15 | 1.0 | Initial story creation | Bob (Scrum Master) |

## 🤖 Dev Agent Record
*This section will be populated by the development agent during implementation*

### Agent Model Used
*To be filled by dev agent*

### Debug Log References
*To be filled by dev agent*

### Completion Notes
*To be filled by dev agent*

### File List
*To be filled by dev agent*

## ✅ QA Results
*To be filled by QA agent*
