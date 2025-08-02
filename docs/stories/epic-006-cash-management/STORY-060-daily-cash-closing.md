# STORY-060: Daily Cash Register Closing

## 📋 Story Details
- **Epic**: EPIC-006 (Cash Management and Closings)
- **Priority**: HIGH
- **Estimate**: 2 days
- **Status**: READY_FOR_REVIEW

## 🎯 User Story
**As** María or Carlos,
**I want** to close the cash register at the end of each day,
**So that** I have a complete record of daily financial movements and can generate closing documents.

## ✅ Acceptance Criteria
1. [ ] Cash closing form accessible from main menu (Admin/Manager only)
2. [ ] Form captures:
   - Opening balance (auto-filled from previous closing or editable)
   - System-calculated sales total (from all sales of the day)
   - Manual cash count input
   - Expense summary for the day
   - Closing notes/observations
3. [ ] Calculate and display difference between expected and actual cash
4. [ ] Generate closing document (PDF) with:
   - Date and time
   - User who performed closing
   - All financial movements
   - Opening and closing balances
   - Signature line
5. [ ] Save closing record to database (immutable once saved)
6. [ ] Prevent sales after closing (until new day opening)
7. [ ] Email closing summary to configured recipients

## 🔧 Technical Tasks
### 1. Create Database Models (AC: 1, 5)
- [x] Create `CashClosing` model in `src/app/models/cash_closing.py`
  - Fields: id, closing_date, opening_balance, sales_total, expenses_total, cash_count, expected_cash, cash_difference, notes, closed_by, closed_at, is_finalized
  - Relationships: user (closed_by), related sales, related expenses
  - Unique constraint on closing_date to prevent multiple closings
- [x] Create migration with Alembic

### 2. Create Pydantic Schemas (AC: 2, 3)
- [x] Create schemas in `src/app/schemas/cash_closing.py`
  - `CashClosingCreate`: Input for new closing
  - `CashClosingUpdate`: For editing draft closings
  - `CashClosingResponse`: Full closing details
  - `CashClosingSummary`: List view summary
  - `DailySummary`: Aggregated daily financial data

### 3. Implement CRUD Operations (AC: 1, 5, 6)
- [x] Create CRUD in `src/app/crud/cash_closing.py`
  - `get_by_date()`: Retrieve closing for specific date
  - `get_last_closing()`: Get most recent closing for opening balance
  - `create_closing()`: Create new daily closing
  - `finalize_closing()`: Mark closing as final (immutable)
  - `check_closing_exists()`: Verify if date already has closing
  - `get_daily_summary()`: Aggregate sales and expenses for a date

### 4. Implement Service Layer (AC: 2, 3, 6)
- [x] Create service in `src/app/services/cash_closing_service.py`
  - `start_daily_closing()`: Initialize closing with calculations
  - `calculate_daily_totals()`: Aggregate sales and expenses
  - `validate_cash_difference()`: Check if difference is within threshold
  - `finalize_closing()`: Complete closing and lock the day
  - `check_can_process_sale()`: Verify if sales are allowed
  - Add method to prevent operations after closing

### 5. Create API Endpoints (AC: 1, 2, 3, 5)
- [x] Add routes to `src/app/api/v1/cash_closings.py`
  - `POST /cash-closings/start`: Initialize new closing
  - `GET /cash-closings/current`: Get today's closing status
  - `PUT /cash-closings/{id}`: Update draft closing
  - `POST /cash-closings/{id}/finalize`: Finalize closing
  - `GET /cash-closings/{date}`: Get closing by date
  - Add role check for Admin/Manager only

### 6. Create Web Routes and Templates (AC: 1, 2, 3)
- [x] Add routes to `src/app/web/cash_closings.py`
  - Route for closing form page
  - HTMX endpoints for dynamic updates
- [x] Create templates in `src/app/templates/cash_closings/`
  - `closing_form.html`: Main closing form
  - `_closing_summary.html`: HTMX partial for summary
  - `_daily_totals.html`: HTMX partial for calculations

### 7. Implement PDF Generation (AC: 4)
- [x] Add PDF generation service
  - Use reportlab or weasyprint for PDF creation
  - Create professional closing document template
  - Include all required fields and signature area
  - Return PDF as downloadable response

### 8. Add Email Notification (AC: 7)
- [ ] Implement email service for closing notifications
  - Configure email settings in environment
  - Create HTML email template
  - Send to configured recipient list
  - Include PDF attachment

### 9. Add Sales Prevention Logic (AC: 6)
- [x] Modify sale creation service
  - Check if current date has finalized closing
  - Return appropriate error if closed
  - Add override for next day opening

### 10. Write Tests
- [ ] Unit tests for models and schemas
- [ ] Service layer tests with mocked dependencies
- [ ] API endpoint tests
- [ ] Integration tests for closing workflow
- [ ] Test PDF generation
- [ ] Test email sending (mocked)

## 📝 Dev Notes

### Data Models
**CashClosing Model** [Source: architecture/source-tree.md#models]
- Create in `src/app/models/cash_closing.py`
- Inherits from `BaseModel` (includes id, created_at, updated_at)
- Use SQLAlchemy 2.0+ syntax with type hints
- Add appropriate indexes for date queries

### API Design
**Endpoint Structure** [Source: architecture/source-tree.md#api]
- Follow RESTful conventions
- Use FastAPI dependency injection for auth/roles
- Return standardized `ResponseSchema` from base schemas
- Implement proper error handling with HTTPException

### Service Layer Pattern [Source: architecture/coding-standards.md#service-layer-pattern]
- All business logic in service classes
- Services orchestrate CRUD operations
- Keep API routes thin (validation and delegation only)
- Use dependency injection for service instantiation

### Security Requirements [Source: architecture/coding-standards.md#security-protocols]
- Role-based access control using `RequireRole` dependency
- Only Admin and Manager roles can access cash closing
- Audit logging for all closing operations
- Immutable closings once finalized

### Testing Standards [Source: architecture/coding-standards.md#testing-standards]
- Test files in `tests/app/unit/`, `tests/app/integration/`
- Use pytest fixtures from `conftest.py`
- Minimum 80% coverage, 100% for financial operations
- Use Factory Boy for test data generation

### PDF Generation
- No specific guidance found in architecture docs
- Recommend using reportlab for flexibility or weasyprint for HTML-to-PDF
- Store generated PDFs temporarily for download
- Consider adding PDF storage service for archival

### Email Configuration
- No specific email service found in architecture docs
- Will need to add email configuration to settings
- Use async email sending to not block requests
- Consider using FastAPI-Mail or similar

### Frontend Implementation [Source: architecture/tech-stack.md#frontend]
- Use HTMX for dynamic form updates
- Tailwind CSS for styling (utility classes only)
- Jinja2 templates with template inheritance
- Alpine.js for any complex interactivity

## 🧪 Testing Requirements
- Unit tests for all CRUD operations
- Service layer tests with business logic validation
- API tests with role-based access scenarios
- Integration test for complete closing workflow
- Test immutability after finalization
- Test sales prevention after closing
- Mock external services (email, PDF)

## 📋 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-15 | 1.0 | Initial story creation | Bob (Scrum Master) |

## 🤖 Dev Agent Record
*This section will be populated by the development agent during implementation*

### Agent Model Used
Claude Sonnet 4 (claude-sonnet-4-20250514)

### Debug Log References
*To be filled by dev agent*

### Completion Notes
*To be filled by dev agent*

### File List
*To be filled by dev agent*

## ✅ QA Results
*To be filled by QA agent*
