# STORY-061: Expense Category Management

## 📋 Story Details
- **Epic**: EPIC-006 (Cash Management and Closings)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** Pedro (admin),
**I want** to manage expense categories,
**So that** all expenses can be properly classified for reporting.

## ✅ Acceptance Criteria
1. [ ] CRUD interface for expense categories (Admin only)
2. [ ] Default categories: General, Suppliers, Utilities, Salaries, Maintenance, Marketing
3. [ ] Category fields: name, description, active status
4. [ ] Cannot delete category with existing expenses (only deactivate)
5. [ ] Categories appear in dropdown when registering expenses

## 🔧 Technical Tasks
### 1. Create Database Models (AC: 1, 3)
- [ ] Create `ExpenseCategory` model in `src/app/models/expense.py`
  - Fields: id, name, description, is_active, created_at, updated_at
  - Unique constraint on name
  - Add seed data migration for default categories
- [ ] Create migration with Alembic

### 2. Create Pydantic Schemas (AC: 3)
- [ ] Create schemas in `src/app/schemas/expense.py`
  - `ExpenseCategoryCreate`: name, description
  - `ExpenseCategoryUpdate`: name, description, is_active
  - `ExpenseCategoryResponse`: Full category details
  - `ExpenseCategoryList`: For dropdown lists (id, name only)

### 3. Implement CRUD Operations (AC: 1, 4)
- [ ] Create CRUD in `src/app/crud/expense_category.py`
  - `get_all_categories()`: Retrieve all categories
  - `get_active_categories()`: Only active for dropdowns
  - `create_category()`: Create new category
  - `update_category()`: Update existing category
  - `deactivate_category()`: Soft delete by setting is_active=False
  - `check_category_has_expenses()`: Verify before deletion

### 4. Implement Service Layer (AC: 2, 4)
- [ ] Create service in `src/app/services/expense_service.py`
  - `create_default_categories()`: Initialize default categories
  - `manage_category()`: Business logic for category operations
  - `validate_category_deletion()`: Check if category can be deleted
  - `get_categories_for_dropdown()`: Return active categories

### 5. Create API Endpoints (AC: 1, 5)
- [ ] Add routes to `src/app/api/v1/expenses.py`
  - `GET /expense-categories`: List all categories
  - `GET /expense-categories/active`: Active categories only
  - `POST /expense-categories`: Create new category
  - `PUT /expense-categories/{id}`: Update category
  - `DELETE /expense-categories/{id}`: Deactivate category
  - Add admin role check for all endpoints

### 6. Create Web Routes and Templates (AC: 1, 5)
- [ ] Add routes to `src/app/web/expenses.py`
  - Route for category management page
  - HTMX endpoints for CRUD operations
- [ ] Create templates in `src/app/templates/expenses/`
  - `categories.html`: Category management page
  - `_category_row.html`: HTMX partial for table row
  - `_category_form.html`: HTMX partial for add/edit form

### 7. Add Seed Data (AC: 2)
- [ ] Create database seeder for default categories
  - Add to initialization scripts
  - Ensure idempotent operation

### 8. Write Tests
- [ ] Unit tests for models and schemas
- [ ] CRUD operation tests
- [ ] Service layer tests
- [ ] API endpoint tests with role checking
- [ ] Test category deletion constraints

## 📝 Dev Notes

### Data Models
**ExpenseCategory Model** [Source: architecture/source-tree.md#models]
- Create in `src/app/models/expense.py`
- Simple model with soft delete pattern (is_active flag)
- Will be referenced by future Expense model

### API Design
**RESTful Endpoints** [Source: architecture/source-tree.md#api]
- Standard CRUD pattern
- Admin-only access using `RequireRole` dependency
- Return `ResponseSchema` for consistency

### Service Layer Pattern [Source: architecture/coding-standards.md#service-layer-pattern]
- Validation logic in service layer
- CRUD layer handles only database operations
- Service orchestrates business rules

### Security Requirements [Source: architecture/coding-standards.md#security-protocols]
- Admin role required for all operations
- Audit logging for category changes
- Input validation with Pydantic

### Frontend Implementation [Source: architecture/tech-stack.md#frontend]
- HTMX for dynamic updates without page reload
- Tailwind CSS for styling
- Modal dialogs for add/edit forms
- Confirmation dialog for deactivation

### Testing Standards [Source: architecture/coding-standards.md#testing-standards]
- Test files in `tests/app/unit/models/test_expense.py`
- Integration tests in `tests/app/integration/api/test_expenses.py`
- Use fixtures for test categories

## 🧪 Testing Requirements
- Unit tests for category model
- CRUD tests with database
- Service tests for business logic
- API tests with admin role verification
- Test constraint on deletion with expenses
- Test default category seeding

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
