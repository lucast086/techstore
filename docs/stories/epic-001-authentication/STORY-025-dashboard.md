# STORY-025: Dashboard

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: MEDIUM
- **Estimate**: 2 days
- **Status**: TODO

## 🎯 User Story
**As** María (administrator) or Carlos (technician),  
**I want** a personalized dashboard showing relevant metrics and quick actions,  
**So that** I can quickly understand the current state of the business and access frequently used features

## ✅ Acceptance Criteria
1. [ ] Dashboard loads as the default page after login
2. [ ] Shows role-appropriate widgets and metrics
3. [ ] Admin sees: total sales, active users, system health, recent activities
4. [ ] Technician sees: pending repairs, today's tasks, recent sales
5. [ ] Real-time updates for critical metrics (WebSocket or polling)
6. [ ] Quick action buttons based on user permissions
7. [ ] Time period filters (today, week, month, year)
8. [ ] Responsive grid layout that works on tablets
9. [ ] Loading states for all data widgets
10. [ ] Refresh button to update all widgets
11. [ ] Customizable widget layout (drag and drop)
12. [ ] Export dashboard data as PDF report

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── web/
│   └── dashboard.py         # Dashboard routes
├── services/
│   └── dashboard_service.py # Dashboard business logic
├── schemas/
│   └── dashboard.py         # Dashboard schemas
├── templates/
│   └── dashboard/
│       ├── index.html       # Main dashboard
│       ├── widgets/         # Widget components
│       │   ├── sales_summary.html
│       │   ├── user_activity.html
│       │   ├── repair_status.html
│       │   ├── quick_actions.html
│       │   └── system_health.html
│       └── layouts/
│           ├── admin.html   # Admin layout
│           └── technician.html # Tech layout
└── static/
    ├── js/
    │   └── dashboard.js     # Dashboard interactions
    └── css/
        └── dashboard.css    # Dashboard styles
```

### Implementation Requirements:

1. **Dashboard Service** (`services/dashboard_service.py`):
```python
from datetime import datetime, timedelta
from typing import Dict, Any

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_admin_metrics(self, period: str = "today") -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = self._get_period_start(period)
        
        return {
            "sales": {
                "total": self._get_total_sales(start_date, end_date),
                "count": self._get_sales_count(start_date, end_date),
                "growth": self._calculate_growth("sales", period)
            },
            "users": {
                "total": self._get_total_users(),
                "active": self._get_active_users(start_date, end_date),
                "new": self._get_new_users(start_date, end_date)
            },
            "products": {
                "total": self._get_total_products(),
                "low_stock": self._get_low_stock_count(),
                "top_selling": self._get_top_products(5)
            },
            "repairs": {
                "pending": self._get_repairs_by_status("pending"),
                "in_progress": self._get_repairs_by_status("in_progress"),
                "completed": self._get_repairs_count(start_date, end_date, "completed")
            },
            "system": {
                "uptime": self._get_system_uptime(),
                "database_size": self._get_database_size(),
                "active_sessions": self._get_active_sessions()
            }
        }
    
    def get_technician_metrics(self, user_id: int, period: str = "today") -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = self._get_period_start(period)
        
        return {
            "my_repairs": {
                "pending": self._get_user_repairs(user_id, "pending"),
                "in_progress": self._get_user_repairs(user_id, "in_progress"),
                "completed_today": self._get_user_repairs_count(user_id, start_date, end_date)
            },
            "sales": {
                "today": self._get_user_sales(user_id, start_date, end_date),
                "count": self._get_user_sales_count(user_id, start_date, end_date)
            },
            "tasks": {
                "urgent": self._get_urgent_tasks(user_id),
                "upcoming": self._get_upcoming_tasks(user_id)
            }
        }
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        # Combine different activity types
        activities = []
        
        # Recent sales
        recent_sales = self.db.query(Sale).order_by(Sale.created_at.desc()).limit(5).all()
        for sale in recent_sales:
            activities.append({
                "type": "sale",
                "description": f"New sale: ${sale.total}",
                "user": sale.user.full_name,
                "timestamp": sale.created_at,
                "icon": "shopping-cart"
            })
        
        # Recent repairs
        recent_repairs = self.db.query(Repair).order_by(Repair.created_at.desc()).limit(5).all()
        for repair in recent_repairs:
            activities.append({
                "type": "repair",
                "description": f"Repair {repair.status}: {repair.device}",
                "user": repair.technician.full_name,
                "timestamp": repair.updated_at,
                "icon": "wrench"
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
```

2. **Dashboard Routes** (`web/dashboard.py`):
```python
@router.get("/")
async def dashboard(request: Request, 
                   current_user: User = Depends(get_current_user),
                   period: str = Query("today", regex="^(today|week|month|year)$")):
    
    service = DashboardService(request.state.db)
    
    if current_user.role == "admin":
        metrics = service.get_admin_metrics(period)
        template = "dashboard/layouts/admin.html"
    else:
        metrics = service.get_technician_metrics(current_user.id, period)
        template = "dashboard/layouts/technician.html"
    
    activities = service.get_recent_activities()
    
    return templates.TemplateResponse(template, {
        "request": request,
        "metrics": metrics,
        "activities": activities,
        "period": period,
        "current_user": current_user
    })

@router.get("/widgets/{widget_name}")
async def get_widget(widget_name: str,
                    request: Request,
                    current_user: User = Depends(get_current_user),
                    period: str = Query("today")):
    """HTMX endpoint for individual widget updates"""
    
    allowed_widgets = {
        "admin": ["sales_summary", "user_activity", "system_health", "repair_status"],
        "technician": ["my_repairs", "recent_sales", "tasks"]
    }
    
    if widget_name not in allowed_widgets.get(current_user.role, []):
        raise HTTPException(403, "Widget not allowed for your role")
    
    # Get widget-specific data
    service = DashboardService(request.state.db)
    widget_data = service.get_widget_data(widget_name, current_user, period)
    
    return templates.TemplateResponse(
        f"dashboard/widgets/{widget_name}.html",
        {"request": request, "data": widget_data}
    )
```

3. **Admin Dashboard Layout** (`templates/dashboard/layouts/admin.html`):
```html
{% extends "base.html" %}

{% block content %}
<div class="dashboard">
    <div class="dashboard-header">
        <h1>Dashboard</h1>
        
        <div class="dashboard-controls">
            <!-- Period Filter -->
            <select name="period" 
                    hx-get="/dashboard"
                    hx-target="#dashboard-content"
                    hx-indicator="#loading">
                <option value="today" {% if period == 'today' %}selected{% endif %}>Today</option>
                <option value="week" {% if period == 'week' %}selected{% endif %}>This Week</option>
                <option value="month" {% if period == 'month' %}selected{% endif %}>This Month</option>
                <option value="year" {% if period == 'year' %}selected{% endif %}>This Year</option>
            </select>
            
            <button class="btn-icon" 
                    hx-get="/dashboard"
                    hx-target="#dashboard-content"
                    title="Refresh">
                <svg><!-- refresh icon --></svg>
            </button>
            
            <button class="btn-secondary" onclick="exportDashboard()">
                Export PDF
            </button>
        </div>
    </div>
    
    <div id="dashboard-content" class="dashboard-grid">
        <!-- Sales Summary Widget -->
        <div class="widget widget-sales" data-widget="sales_summary">
            <div class="widget-header">
                <h3>Sales Overview</h3>
                <span class="widget-refresh" 
                      hx-get="/widgets/sales_summary?period={{ period }}"
                      hx-target="closest .widget"
                      hx-swap="outerHTML">
                    <svg><!-- refresh icon --></svg>
                </span>
            </div>
            <div class="widget-content">
                <div class="metric-group">
                    <div class="metric">
                        <span class="metric-value">${{ metrics.sales.total|format_currency }}</span>
                        <span class="metric-label">Total Sales</span>
                        <span class="metric-change {% if metrics.sales.growth > 0 %}positive{% else %}negative{% endif %}">
                            {{ metrics.sales.growth }}%
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">{{ metrics.sales.count }}</span>
                        <span class="metric-label">Transactions</span>
                    </div>
                </div>
                <div class="widget-chart" id="sales-chart"></div>
            </div>
        </div>
        
        <!-- User Activity Widget -->
        <div class="widget widget-users" data-widget="user_activity">
            <div class="widget-header">
                <h3>User Activity</h3>
            </div>
            <div class="widget-content">
                <div class="metric-grid">
                    <div class="metric-card">
                        <span class="metric-icon">👥</span>
                        <span class="metric-value">{{ metrics.users.total }}</span>
                        <span class="metric-label">Total Users</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-icon">🟢</span>
                        <span class="metric-value">{{ metrics.users.active }}</span>
                        <span class="metric-label">Active Today</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-icon">✨</span>
                        <span class="metric-value">{{ metrics.users.new }}</span>
                        <span class="metric-label">New Users</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions Widget -->
        <div class="widget widget-actions">
            <div class="widget-header">
                <h3>Quick Actions</h3>
            </div>
            <div class="widget-content">
                <div class="quick-actions">
                    {% if can('users.create') %}
                    <a href="/users/new" class="action-button">
                        <svg><!-- user-plus icon --></svg>
                        <span>Add User</span>
                    </a>
                    {% endif %}
                    
                    {% if can('products.create') %}
                    <a href="/products/new" class="action-button">
                        <svg><!-- box icon --></svg>
                        <span>Add Product</span>
                    </a>
                    {% endif %}
                    
                    {% if can('sales.create') %}
                    <a href="/sales/new" class="action-button">
                        <svg><!-- cart icon --></svg>
                        <span>New Sale</span>
                    </a>
                    {% endif %}
                    
                    <a href="/reports" class="action-button">
                        <svg><!-- chart icon --></svg>
                        <span>View Reports</span>
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Recent Activity Feed -->
        <div class="widget widget-activity widget-wide">
            <div class="widget-header">
                <h3>Recent Activity</h3>
            </div>
            <div class="widget-content">
                <div class="activity-feed">
                    {% for activity in activities %}
                    <div class="activity-item">
                        <div class="activity-icon">
                            <svg><!-- {{ activity.icon }} icon --></svg>
                        </div>
                        <div class="activity-content">
                            <p class="activity-description">{{ activity.description }}</p>
                            <span class="activity-meta">
                                {{ activity.user }} • {{ activity.timestamp|timeago }}
                            </span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<div id="loading" class="htmx-indicator">
    <div class="spinner"></div>
</div>
{% endblock %}
```

4. **Dashboard JavaScript** (`static/js/dashboard.js`):
```javascript
// Dashboard widget management
class DashboardManager {
    constructor() {
        this.widgets = new Map();
        this.refreshInterval = 30000; // 30 seconds
        this.init();
    }
    
    init() {
        // Initialize drag and drop
        this.initDragDrop();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        // Initialize charts
        this.initCharts();
        
        // WebSocket for real-time updates
        this.initWebSocket();
    }
    
    initDragDrop() {
        const grid = document.querySelector('.dashboard-grid');
        new Sortable(grid, {
            animation: 150,
            handle: '.widget-header',
            onEnd: (evt) => {
                this.saveLayout();
            }
        });
    }
    
    startAutoRefresh() {
        // Refresh widgets periodically
        setInterval(() => {
            document.querySelectorAll('[data-widget]').forEach(widget => {
                const refreshBtn = widget.querySelector('.widget-refresh');
                if (refreshBtn && !widget.classList.contains('no-auto-refresh')) {
                    htmx.trigger(refreshBtn, 'click');
                }
            });
        }, this.refreshInterval);
    }
    
    initWebSocket() {
        const ws = new WebSocket(`ws://${window.location.host}/ws/dashboard`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleRealtimeUpdate(data);
        };
    }
    
    handleRealtimeUpdate(data) {
        // Update specific widget based on event type
        switch(data.type) {
            case 'new_sale':
                this.updateWidget('sales_summary', data);
                this.addActivityItem(data);
                break;
            case 'user_login':
                this.updateWidget('user_activity', data);
                break;
            // More event types...
        }
    }
    
    saveLayout() {
        const layout = Array.from(document.querySelectorAll('[data-widget]'))
            .map(w => w.dataset.widget);
        
        fetch('/api/v1/user/preferences', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                dashboard_layout: layout
            })
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});

// Export dashboard as PDF
function exportDashboard() {
    const period = document.querySelector('select[name="period"]').value;
    window.open(`/dashboard/export?period=${period}`, '_blank');
}
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Dashboard loads in < 1 second
- [ ] Real-time updates working
- [ ] Responsive on tablets (768px+)
- [ ] Widget drag-and-drop saves preferences
- [ ] PDF export includes all metrics
- [ ] No memory leaks from WebSocket
- [ ] Accessibility: keyboard navigation works

## 🧪 Testing Approach

### Unit Tests:
- Dashboard service calculations
- Period filtering logic
- Permission-based widget filtering
- Activity feed aggregation

### Integration Tests:
- Widget loading via HTMX
- WebSocket connections
- Layout persistence
- PDF generation

### Performance Tests:
- Dashboard load time
- Widget refresh performance
- Concurrent user handling
- Database query optimization

### UI Tests:
- Responsive layout
- Drag and drop functionality
- Chart rendering
- Loading states

## 🔗 Dependencies
- **Depends on**: 
  - STORY-020 (Authentication System)
  - STORY-022 (Role Management)
  - STORY-024 (Access Control)
  - STORY-027 (Database Setup) - Required for querying metrics
- **Blocks**: None

## 📌 Notes
- Consider caching dashboard metrics
- Use database views for complex calculations
- Implement progressive loading for better UX
- Add widget marketplace in future
- Consider GraphQL for flexible data fetching

## 📝 Dev Notes

### Key Implementation Details:

1. **Period Calculations**:
   ```python
   def _get_period_start(self, period: str) -> datetime:
       now = datetime.now()
       if period == "today":
           return now.replace(hour=0, minute=0, second=0)
       elif period == "week":
           return now - timedelta(days=now.weekday())
       elif period == "month":
           return now.replace(day=1)
       elif period == "year":
           return now.replace(month=1, day=1)
   ```

2. **Chart Data Structure**:
   ```python
   def get_chart_data(self, metric_type: str, period: str) -> Dict:
       return {
           "labels": self._get_period_labels(period),
           "datasets": [{
               "label": metric_type.title(),
               "data": self._get_period_values(metric_type, period),
               "borderColor": "#2563EB",
               "tension": 0.1
           }]
       }
   ```

3. **WebSocket Updates**:
   ```python
   async def dashboard_websocket(websocket: WebSocket, user_id: int):
       await websocket.accept()
       
       # Subscribe to relevant events
       pubsub = redis_client.pubsub()
       pubsub.subscribe(f"dashboard:{user_id}", "dashboard:global")
       
       try:
           while True:
               message = pubsub.get_message()
               if message:
                   await websocket.send_json(message['data'])
               await asyncio.sleep(0.1)
       except WebSocketDisconnect:
           pubsub.unsubscribe()
   ```

4. **PDF Export**:
   ```python
   async def export_dashboard_pdf(user: User, period: str):
       # Get dashboard data
       metrics = get_dashboard_metrics(user, period)
       
       # Render HTML template
       html = render_template("dashboard/export.html", metrics=metrics)
       
       # Convert to PDF
       pdf = HTML(string=html).write_pdf()
       
       return StreamingResponse(
           io.BytesIO(pdf),
           media_type="application/pdf",
           headers={"Content-Disposition": f"attachment; filename=dashboard_{period}.pdf"}
       )
   ```

### Testing Standards:
- Test files: `tests/test_services/test_dashboard.py`
- Mock time-based calculations
- Test with different user roles
- Verify metric accuracy
- Performance benchmarks for large datasets

## 📊 Tasks / Subtasks

- [ ] **Create Dashboard Service** (AC: 2, 3, 4)
  - [ ] Implement metric calculation methods
  - [ ] Add period filtering logic
  - [ ] Create role-based metric selection
  - [ ] Optimize database queries

- [ ] **Build Dashboard Routes** (AC: 1, 7)
  - [ ] Create main dashboard endpoint
  - [ ] Add widget refresh endpoints
  - [ ] Implement period filtering
  - [ ] Add export endpoint

- [ ] **Design Admin Layout** (AC: 3, 8, 9)
  - [ ] Create admin dashboard template
  - [ ] Build metric widgets
  - [ ] Add activity feed
  - [ ] Implement responsive grid

- [ ] **Design Technician Layout** (AC: 4, 8, 9)
  - [ ] Create technician template
  - [ ] Build task widgets
  - [ ] Add repair status widget
  - [ ] Ensure responsive design

- [ ] **Implement Quick Actions** (AC: 6)
  - [ ] Create action buttons component
  - [ ] Filter by user permissions
  - [ ] Add icons and styling
  - [ ] Link to appropriate pages

- [ ] **Add Real-time Updates** (AC: 5)
  - [ ] Set up WebSocket endpoint
  - [ ] Implement event publishing
  - [ ] Create client-side handler
  - [ ] Update widgets dynamically

- [ ] **Build Widget Refresh** (AC: 10)
  - [ ] Add refresh buttons to widgets
  - [ ] Implement HTMX triggers
  - [ ] Show loading states
  - [ ] Handle errors gracefully

- [ ] **Create Drag & Drop** (AC: 11)
  - [ ] Add sortable.js library
  - [ ] Make widgets draggable
  - [ ] Save layout preferences
  - [ ] Restore on page load

- [ ] **Implement PDF Export** (AC: 12)
  - [ ] Create export template
  - [ ] Generate PDF with metrics
  - [ ] Include charts as images
  - [ ] Add proper formatting

- [ ] **Add Loading States** (AC: 9)
  - [ ] Create skeleton loaders
  - [ ] Show during data fetch
  - [ ] Handle slow connections
  - [ ] Implement error states

- [ ] **Create Dashboard Tests** (DoD)
  - [ ] Unit test calculations
  - [ ] Test role-based filtering
  - [ ] Verify WebSocket updates
  - [ ] Performance testing

- [ ] **Optimize Performance** (DoD)
  - [ ] Add metric caching
  - [ ] Optimize queries
  - [ ] Implement lazy loading
  - [ ] Monitor load times

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |

## 🤖 Dev Agent Record
*To be populated during implementation*

### Agent Model Used
*[Agent model and version]*

### Completion Notes
*[Implementation notes]*

### File List
*[List of created/modified files]*

## ✅ QA Results
*To be populated during QA review*