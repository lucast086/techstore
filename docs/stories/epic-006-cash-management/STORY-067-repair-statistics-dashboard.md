# STORY-067: Repair Statistics Dashboard

## 📋 Story Details
- **Epic**: EPIC-006 (Cash Management and Closings)
- **Priority**: MEDIUM
- **Estimate**: 1.5 days
- **Status**: TODO

## 🎯 User Story
**As** Pedro,
**I want** to view repair service statistics,
**So that** I can monitor service department performance.

## ✅ Acceptance Criteria
1. [ ] Dashboard showing:
   - Active repairs by status
   - Average repair duration by type
   - Technician performance metrics
   - Most repaired device types
   - Revenue from repairs
   - Customer satisfaction metrics
   - Warranty claim statistics
2. [ ] Filters by date range, technician, device type
3. [ ] Graphical representations
4. [ ] Export capabilities

## 🔧 Technical Tasks
### 1. Create Repair Analytics Service (AC: 1, 2)
- [ ] Create service in `src/app/services/repair_analytics_service.py`
  - `get_repair_status_overview()`: Current status distribution
  - `get_average_repair_duration()`: Time metrics by device type
  - `get_technician_performance()`: Individual performance stats
  - `get_device_type_breakdown()`: Most common repairs
  - `get_repair_revenue()`: Financial metrics
  - `get_warranty_statistics()`: Warranty claim data

### 2. Create Repair Analytics Schemas (AC: 1, 3)
- [ ] Create schemas in `src/app/schemas/repair_analytics.py`
  - `RepairStatusOverview`: Status distribution data
  - `RepairDurationStats`: Time-based metrics
  - `TechnicianPerformance`: Individual tech stats
  - `DeviceTypeStats`: Device breakdown
  - `RepairRevenueStats`: Financial performance
  - `WarrantyStats`: Warranty claim metrics
  - `RepairAnalyticsFilter`: Date, technician, device filters

### 3. Extend Repair CRUD for Analytics (AC: 1, 2)
- [ ] Add analytics methods to existing `src/app/crud/repair.py`
  - `get_repairs_by_status()`: Status distribution queries
  - `get_repair_duration_stats()`: Time calculations
  - `get_technician_stats()`: Performance by technician
  - `get_device_type_stats()`: Device breakdown
  - `get_repair_revenue_data()`: Financial queries
  - Use existing Repair model from Epic 005

### 4. Customer Satisfaction Integration (AC: 1)
- [ ] Extend repair service for satisfaction metrics
  - `get_customer_satisfaction()`: Rating analysis
  - `get_completion_rate()`: On-time delivery stats
  - Link with existing Customer and Repair models
  - May need satisfaction rating field in repairs

### 5. Warranty Analytics Integration (AC: 1)
- [ ] Integrate with warranty system from STORY-058
  - `get_warranty_claim_stats()`: Claim frequency
  - `get_warranty_coverage_stats()`: Coverage analysis
  - Link with existing Warranty model
  - Calculate warranty claim rates

### 6. Create Chart Data for Repairs (AC: 3)
- [ ] Extend chart service for repair analytics
  - `generate_status_pie_chart()`: Current status distribution
  - `generate_duration_bar_chart()`: Average repair times
  - `generate_technician_performance_chart()`: Performance comparison
  - `generate_device_trend_chart()`: Device type trends
  - `generate_revenue_line_chart()`: Repair revenue over time

### 7. Create API Endpoints (AC: 1, 4)
- [ ] Add routes to `src/app/api/v1/analytics.py` (extend existing)
  - `GET /analytics/repairs/overview`: Main dashboard data
  - `GET /analytics/repairs/duration`: Time-based stats
  - `GET /analytics/repairs/technicians`: Technician performance
  - `GET /analytics/repairs/devices`: Device type breakdown
  - `GET /analytics/repairs/revenue`: Financial metrics
  - `GET /analytics/repairs/export`: Data export

### 8. Create Repair Dashboard Interface (AC: 1, 2, 3)
- [ ] Extend `src/app/web/analytics.py` for repair dashboard
  - Repair dashboard page route
  - HTMX endpoints for filter updates
- [ ] Create templates in `src/app/templates/analytics/`
  - `repair_dashboard.html`: Main repair analytics page
  - `_repair_overview.html`: Key metrics cards
  - `_repair_charts.html`: Chart containers
  - `_repair_filters.html`: Filter controls

### 9. Technician Performance Features (AC: 1)
- [ ] Implement detailed technician analytics
  - Individual performance dashboards
  - Workload distribution analysis
  - Quality metrics (rework rates)
  - Customer feedback integration

### 10. Export and Reporting (AC: 4)
- [ ] Extend export service for repair analytics
  - Repair performance reports
  - Technician productivity reports
  - Device failure analysis reports
  - Excel/CSV export capabilities

### 11. Write Tests
- [ ] Unit tests for repair analytics service
- [ ] Test duration calculations
- [ ] API endpoint tests
- [ ] Chart data generation tests
- [ ] Integration tests with existing repair system
- [ ] Performance tests for analytics queries

## 📝 Dev Notes

### Integration with Existing Systems
**Epic 005 Dependencies** [Source: Current system]
- Existing Repair model with status tracking
- Technician user relationships
- Device type categorization
- Status workflow (received, diagnosing, repairing, testing, ready, delivered)

### Previous Story Dependencies
- STORY-058: Warranty model for warranty analytics
- Epic 005: Complete repair management system
- User model for technician relationships
- Chart service from previous analytics stories

### Duration Calculations
**Time Metrics**:
- Use repair status history for duration calculations
- Calculate average time between status changes
- Identify bottlenecks in repair workflow
- Consider business hours vs. calendar time

### Performance Considerations [Source: architecture/coding-standards.md#performance-standards]
- Index repairs by status, technician, device_type, dates
- Cache expensive analytics queries
- Use database aggregation for large datasets
- Consider materialized views for complex calculations

### Technician Privacy
**Data Sensitivity**:
- Ensure technician performance data is used constructively
- Admin-only access to individual performance metrics
- Focus on workflow improvement, not punitive measures
- Anonymize data for general trends

### Chart Implementation [Source: architecture/tech-stack.md#frontend]
- Consistent chart styling with sales dashboard
- Interactive charts for drill-down analysis
- Mobile-responsive design
- Accessibility considerations

### Testing Strategy [Source: architecture/coding-standards.md#testing-standards]
- Generate test repair data with various statuses
- Test with multiple technicians
- Verify duration calculations
- Test edge cases (repairs without completion)

### Security and Access [Source: architecture/coding-standards.md#security-protocols]
- Admin access for comprehensive analytics
- Technician access to own performance data
- Audit logging for analytics access
- Data privacy considerations

## 🧪 Testing Requirements
- Repair analytics calculation tests
- Duration calculation accuracy tests
- Technician performance metric tests
- Chart data generation tests
- Integration with existing repair system
- Export functionality tests
- Performance tests with large repair datasets

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
