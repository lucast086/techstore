# STORY-066: Sales Statistics Dashboard

## 📋 Story Details
- **Epic**: EPIC-006 (Cash Management and Closings)
- **Priority**: MEDIUM
- **Estimate**: 2 days
- **Status**: TODO

## 🎯 User Story
**As** Pedro,
**I want** to view comprehensive sales statistics,
**So that** I can analyze business performance and make data-driven decisions.

## ✅ Acceptance Criteria
1. [ ] Dashboard accessible from admin panel
2. [ ] Date range selector (today, week, month, year, custom)
3. [ ] Metrics displayed:
   - Total sales amount and count
   - Average sale value
   - Sales by payment method
   - Top selling products (table and chart)
   - Sales by category
   - Hourly sales distribution
   - Customer metrics (new vs returning)
4. [ ] Interactive charts with drill-down capability
5. [ ] Export data to Excel/CSV
6. [ ] Real-time updates

## 🔧 Technical Tasks
### 1. Create Sales Analytics Service (AC: 2, 3)
- [ ] Create service in `src/app/services/sales_analytics_service.py`
  - `get_sales_overview()`: Basic metrics (total, count, average)
  - `get_payment_method_breakdown()`: Sales by payment type
  - `get_top_products()`: Best sellers with quantities
  - `get_category_breakdown()`: Sales by product category
  - `get_hourly_distribution()`: Sales throughout the day
  - `get_customer_metrics()`: New vs returning analysis

### 2. Create Analytics Schemas (AC: 3, 5)
- [ ] Create schemas in `src/app/schemas/analytics.py`
  - `DateRangeFilter`: Start date, end date, preset options
  - `SalesOverview`: Core metrics summary
  - `PaymentMethodStats`: Payment breakdown
  - `ProductSalesStats`: Product performance data
  - `CategoryStats`: Category performance
  - `HourlyStats`: Time-based sales data
  - `CustomerStats`: Customer analysis

### 3. Extend Sales CRUD for Analytics (AC: 3)
- [ ] Add analytics methods to `src/app/crud/sale.py`
  - `get_sales_by_date_range()`: Base query with filters
  - `get_sales_by_payment_method()`: Group by payment type
  - `get_top_selling_products()`: Product ranking queries
  - `get_sales_by_category()`: Category aggregation
  - `get_hourly_sales()`: Time-based grouping
  - Use database aggregation for performance

### 4. Customer Analytics Integration (AC: 3)
- [ ] Extend customer service for analytics
  - `get_customer_purchase_stats()`: Buying patterns
  - `identify_new_customers()`: Recent registrations
  - `calculate_retention_metrics()`: Return customer analysis
  - Link with existing Customer model

### 5. Create Chart Data Service (AC: 4)
- [ ] Create service in `src/app/services/chart_service.py` (extend from STORY-065)
  - `generate_sales_trend_chart()`: Time series data
  - `generate_payment_method_pie()`: Payment distribution
  - `generate_product_bar_chart()`: Top products
  - `generate_category_doughnut()`: Category breakdown
  - `generate_hourly_line_chart()`: Daily sales pattern

### 6. Create API Endpoints (AC: 1, 5, 6)
- [ ] Add routes to `src/app/api/v1/analytics.py`
  - `GET /analytics/sales/overview`: Main dashboard data
  - `GET /analytics/sales/payment-methods`: Payment breakdown
  - `GET /analytics/sales/products`: Product statistics
  - `GET /analytics/sales/categories`: Category performance
  - `GET /analytics/sales/hourly`: Time distribution
  - `GET /analytics/sales/export`: Data export
  - Add admin role requirement

### 7. Create Dashboard Web Interface (AC: 1, 2, 4)
- [ ] Add routes to `src/app/web/analytics.py`
  - Dashboard page route
  - HTMX endpoints for date range updates
- [ ] Create templates in `src/app/templates/analytics/`
  - `sales_dashboard.html`: Main dashboard layout
  - `_sales_overview.html`: Key metrics cards
  - `_sales_charts.html`: Chart container sections
  - `_date_selector.html`: Date range picker

### 8. Implement Interactive Charts (AC: 4)
- [ ] Add Chart.js integration for interactivity
  - Click-through on charts for detailed views
  - Responsive charts for mobile
  - Chart animations and tooltips
  - Export chart data functionality

### 9. Add Real-time Updates (AC: 6)
- [ ] Implement dashboard refresh mechanism
  - HTMX polling for real-time data
  - WebSocket updates (optional)
  - Cache busting for fresh data
  - Loading indicators during updates

### 10. Export Functionality (AC: 5)
- [ ] Implement data export service
  - Excel export with multiple sheets
  - CSV export for raw data
  - Include chart images in exports
  - Formatted reports with headers

### 11. Write Tests
- [ ] Unit tests for analytics service
- [ ] Test data aggregation accuracy
- [ ] API endpoint tests
- [ ] Chart data generation tests
- [ ] Export functionality tests
- [ ] Performance tests for large datasets

## 📝 Dev Notes

### Data Aggregation Strategy
**Performance Optimization** [Source: architecture/coding-standards.md#performance-standards]
- Use database aggregation functions (SUM, COUNT, GROUP BY)
- Index sales table by date, payment_method, customer_id
- Consider caching for expensive queries
- Implement pagination for large result sets

### Previous Story Dependencies
- Existing Sale and SaleItem models from Epic 004
- Customer model from Epic 002
- Product and Category models from Epic 003
- Chart service foundation from STORY-065

### Chart Implementation [Source: architecture/tech-stack.md#frontend]
- Chart.js for interactive visualizations
- Responsive design for mobile dashboards
- Color schemes consistent with brand
- Accessibility considerations for charts

### Database Queries
**Complex Analytics Queries**:
- Use SQLAlchemy's `func.sum()`, `func.count()` for aggregation
- JOIN with product/category tables for enriched data
- Optimize with proper indexing strategy
- Consider read replicas for heavy analytics

### Security and Access [Source: architecture/coding-standards.md#security-protocols]
- Admin-only access to sales analytics
- Rate limiting on analytics endpoints
- Data privacy considerations
- Audit logging for analytics access

### Caching Strategy [Source: architecture/coding-standards.md#performance-standards]
- Cache analytics results for 15-30 minutes
- Invalidate cache on new sales
- Use Redis if available
- Cache expensive aggregations

### Real-time Updates
**Implementation Options**:
- HTMX polling every 30-60 seconds
- WebSocket for instant updates (advanced)
- Server-sent events for one-way updates
- Consider load impact of real-time features

### Testing Data Requirements
- Need substantial test data for meaningful analytics
- Use Factory Boy to generate test sales
- Test edge cases (zero sales, large datasets)
- Performance testing with realistic data volumes

## 🧪 Testing Requirements
- Analytics calculation accuracy tests
- Database aggregation tests
- Chart data generation tests
- Export functionality tests
- Performance tests with large datasets
- Real-time update mechanism tests
- Mobile responsive tests

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
