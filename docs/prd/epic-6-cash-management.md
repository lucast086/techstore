# Epic 6: Cash Management and Closings

## Epic Overview
Enable comprehensive cash management, financial closing processes, and business analytics to provide complete financial visibility and control for the tech store operations.

## User Stories

### Story 6.1: Daily Cash Register Closing
**As** María or Carlos,
**I want** to close the cash register at the end of each day,
**So that** I have a complete record of daily financial movements and can generate closing documents.

**Acceptance Criteria:**
1. Cash closing form accessible from main menu (Admin/Manager only)
2. Form captures:
   - Opening balance (auto-filled from previous closing or editable)
   - System-calculated sales total (from all sales of the day)
   - Manual cash count input
   - Expense summary for the day
   - Closing notes/observations
3. Calculate and display difference between expected and actual cash
4. Generate closing document (PDF) with:
   - Date and time
   - User who performed closing
   - All financial movements
   - Opening and closing balances
   - Signature line
5. Save closing record to database (immutable once saved)
6. Prevent sales after closing (until new day opening)
7. Email closing summary to configured recipients

### Story 6.2: Expense Category Management
**As** Pedro (admin),
**I want** to manage expense categories,
**So that** all expenses can be properly classified for reporting.

**Acceptance Criteria:**
1. CRUD interface for expense categories (Admin only)
2. Default categories: General, Suppliers, Utilities, Salaries, Maintenance, Marketing
3. Category fields: name, description, active status
4. Cannot delete category with existing expenses (only deactivate)
5. Categories appear in dropdown when registering expenses

### Story 6.3: Expense Registration
**As** María, Carlos, or Pedro,
**I want** to register business expenses,
**So that** all costs are tracked and categorized for financial reporting.

**Acceptance Criteria:**
1. Expense form accessible from main menu
2. Required fields:
   - Amount
   - Category (dropdown)
   - Description/detail
   - Date (defaults to today)
   - Payment method (cash, transfer, card)
3. Optional fields:
   - Receipt number
   - Supplier name
   - File attachment for receipt/invoice
4. List view with filters by date range, category, amount
5. Edit allowed only same day, view-only after
6. Expenses automatically included in daily closing

### Story 6.4: Purchase Order Management
**As** Carlos or María,
**I want** to register supplier purchases with detailed items,
**So that** inventory is automatically updated and costs are properly tracked.

**Acceptance Criteria:**
1. Purchase form with supplier details:
   - Supplier name (autocomplete from previous)
   - Invoice number
   - Date
   - Payment terms
2. Line items with:
   - Product search (by code/name)
   - Option to create new product if not found
   - Quantity
   - Unit cost
   - Line total (auto-calculated)
3. Summary section:
   - Subtotal
   - Tax amount
   - Total amount
4. On save:
   - Create expense entry for total amount (category: "Supplier Purchases")
   - Update inventory quantities for all items
   - Generate purchase record
5. Purchase history with search and filters

### Story 6.5: Automatic Inventory Updates
**As** the system,
**I want** to automatically update product inventory from purchases,
**So that** stock levels remain accurate without manual intervention.

**Acceptance Criteria:**
1. When purchase order is saved:
   - Add purchased quantities to product stock
   - Update last purchase price
   - Calculate new average cost
2. For new products created during purchase:
   - Create product with provided details
   - Set initial stock to purchased quantity
   - Set cost to purchase price
3. Stock movement history shows purchase entries
4. Inventory reports reflect purchase updates

### Story 6.6: Monthly Closing Summary
**As** Pedro,
**I want** to generate monthly closing summaries,
**So that** I can review financial performance and prepare accounting reports.

**Acceptance Criteria:**
1. Monthly closing accessible from reports menu (Admin only)
2. Automatically aggregate all daily closings for selected month
3. Include:
   - Total revenue (sales)
   - Total expenses by category
   - Net profit/loss
   - Daily closing summary table
   - Graphs for visual analysis
4. Export options: PDF, Excel
5. Compare with previous months
6. Email to configured recipients

### Story 6.7: Sales Statistics Dashboard
**As** Pedro,
**I want** to view comprehensive sales statistics,
**So that** I can analyze business performance and make data-driven decisions.

**Acceptance Criteria:**
1. Dashboard accessible from admin panel
2. Date range selector (today, week, month, year, custom)
3. Metrics displayed:
   - Total sales amount and count
   - Average sale value
   - Sales by payment method
   - Top selling products (table and chart)
   - Sales by category
   - Hourly sales distribution
   - Customer metrics (new vs returning)
4. Interactive charts with drill-down capability
5. Export data to Excel/CSV
6. Real-time updates

### Story 6.8: Repair Statistics Dashboard
**As** Pedro,
**I want** to view repair service statistics,
**So that** I can monitor service department performance.

**Acceptance Criteria:**
1. Dashboard showing:
   - Active repairs by status
   - Average repair duration by type
   - Technician performance metrics
   - Most repaired device types
   - Revenue from repairs
   - Customer satisfaction metrics
   - Warranty claim statistics
2. Filters by date range, technician, device type
3. Graphical representations
4. Export capabilities

### Story 6.9: Financial Analytics Dashboard
**As** Pedro,
**I want** to view comprehensive financial analytics,
**So that** I can monitor overall business health.

**Acceptance Criteria:**
1. Combined financial dashboard showing:
   - Revenue streams (sales vs repairs)
   - Expense breakdown by category
   - Profit margins and trends
   - Cash flow analysis
   - Accounts receivable (customer credit)
   - Inventory value
   - Key performance indicators (KPIs)
2. Customizable date ranges and comparisons
3. Automated alerts for anomalies
4. Forecast projections based on historical data
5. Export comprehensive reports
