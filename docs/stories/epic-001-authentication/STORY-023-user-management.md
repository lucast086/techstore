# STORY-023: User Management

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: HIGH
- **Estimate**: 2 days
- **Status**: TODO

## 🎯 User Story
**As** María (administrator),  
**I want** to create, edit, deactivate, and manage user accounts,  
**So that** I can control who has access to the system and maintain proper user information

## ✅ Acceptance Criteria
1. [ ] User list page shows all users with pagination (20 per page)
2. [ ] Can search users by name, email, or role
3. [ ] Create new user form with all required fields
4. [ ] Edit user information (except email once created)
5. [ ] Deactivate/reactivate users (soft delete only)
6. [ ] Cannot delete or deactivate your own account
7. [ ] Cannot deactivate the last admin user
8. [ ] Password reset sends secure link to user's email
9. [ ] User creation generates temporary password
10. [ ] Audit trail shows who created/modified each user
11. [ ] Bulk actions: activate/deactivate multiple users
12. [ ] Export user list to CSV

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── crud/
│   └── user.py              # User CRUD operations
├── schemas/
│   └── user.py              # User schemas
├── api/v1/
│   └── users.py             # User API endpoints
├── web/
│   └── users.py             # User web routes
├── templates/
│   └── users/
│       ├── list.html        # User list page
│       ├── form.html        # Create/Edit form
│       └── detail.html      # User details
└── services/
    └── user_service.py      # User business logic
```

### Implementation Requirements:

1. **User CRUD Operations** (`crud/user.py`):
```python
class UserCRUD:
    def get_users(self, db: Session, skip: int = 0, limit: int = 20, 
                  search: str = None, role: str = None):
        query = db.query(User)
        if search:
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        if role:
            query = query.filter(User.role == role)
        return query.offset(skip).limit(limit).all()
    
    def create_user(self, db: Session, user: UserCreate, 
                   created_by: int) -> User:
        # Generate temporary password
        temp_password = self.generate_temp_password()
        # Hash password
        password_hash = get_password_hash(temp_password)
        # Create user
        # Send welcome email with temp password
        
    def update_user(self, db: Session, user_id: int, 
                   user_update: UserUpdate, updated_by: int):
        # Update user info
        # Log the change
        
    def deactivate_user(self, db: Session, user_id: int, 
                       deactivated_by: int):
        # Check constraints (last admin, self)
        # Soft delete
        # Log the action
```

2. **User Schemas** (`schemas/user.py`):
```python
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    role: Literal["admin", "technician"]

class UserCreate(UserBase):
    # No password field - system generates it

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(min_length=2, max_length=100)
    role: Optional[Literal["admin", "technician"]]
    is_active: Optional[bool]

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    created_by: Optional[int]
    
class UserList(BaseModel):
    users: List[UserInDB]
    total: int
    page: int
    per_page: int
```

3. **User Web Interface** (`templates/users/list.html`):
```html
<div class="page-header">
    <h1>User Management</h1>
    <button class="btn-primary" hx-get="/users/new">
        Add User
    </button>
</div>

<!-- Search and filters -->
<div class="filters">
    <input type="search" 
           name="search" 
           placeholder="Search users..."
           hx-get="/users"
           hx-trigger="keyup changed delay:500ms"
           hx-target="#user-list">
    
    <select name="role" 
            hx-get="/users"
            hx-target="#user-list">
        <option value="">All Roles</option>
        <option value="admin">Admin</option>
        <option value="technician">Technician</option>
    </select>
</div>

<!-- User table -->
<div id="user-list">
    <table class="data-table">
        <thead>
            <tr>
                <th><input type="checkbox" id="select-all"></th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td><input type="checkbox" name="user_ids" value="{{ user.id }}"></td>
                <td>{{ user.full_name }}</td>
                <td>{{ user.email }}</td>
                <td><span class="badge badge-{{ user.role }}">{{ user.role|title }}</span></td>
                <td>
                    {% if user.is_active %}
                        <span class="badge badge-success">Active</span>
                    {% else %}
                        <span class="badge badge-danger">Inactive</span>
                    {% endif %}
                </td>
                <td>{{ user.last_login|timeago if user.last_login else "Never" }}</td>
                <td class="actions">
                    <button hx-get="/users/{{ user.id }}/edit" 
                            hx-target="#modal">Edit</button>
                    {% if user.id != current_user.id %}
                        <button hx-post="/users/{{ user.id }}/toggle"
                                hx-confirm="Toggle user status?">
                            {% if user.is_active %}Deactivate{% else %}Activate{% endif %}
                        </button>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <!-- Pagination -->
    <div class="pagination">
        {{ render_pagination(page, total_pages) }}
    </div>
</div>

<!-- Bulk actions -->
<div class="bulk-actions" style="display:none;">
    <button hx-post="/users/bulk-activate">Activate Selected</button>
    <button hx-post="/users/bulk-deactivate">Deactivate Selected</button>
    <button hx-get="/users/export">Export to CSV</button>
</div>
```

4. **User Service Layer** (`services/user_service.py`):
```python
class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = UserCRUD()
    
    def create_user_with_notification(self, user_data: UserCreate, 
                                    created_by_id: int):
        # Validate unique email
        # Generate secure temporary password
        # Create user
        # Send welcome email
        # Log creation
        return user, temp_password
    
    def can_deactivate_user(self, user_id: int, requesting_user_id: int):
        # Cannot deactivate self
        if user_id == requesting_user_id:
            return False, "Cannot deactivate your own account"
        
        # Cannot deactivate last admin
        user = self.crud.get_user(self.db, user_id)
        if user.role == "admin":
            admin_count = self.crud.count_active_admins(self.db)
            if admin_count <= 1:
                return False, "Cannot deactivate the last admin"
        
        return True, None
    
    def generate_password_reset(self, email: str):
        # Find user
        # Generate secure token
        # Store token with expiration
        # Send reset email
        # Return success (don't reveal if email exists)
```

5. **Security Considerations**:
- Temporary passwords must be cryptographically secure
- Password reset tokens expire after 1 hour
- Email existence is not revealed on password reset
- All user modifications are logged
- Bulk operations require confirmation

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] User CRUD operations fully tested
- [ ] Email notifications working
- [ ] Pagination and search optimized
- [ ] Security audit passed
- [ ] No SQL injection vulnerabilities
- [ ] Audit trail complete
- [ ] CSV export includes proper escaping

## 🧪 Testing Approach

### Unit Tests:
- User CRUD operations
- Permission validations
- Password generation
- Search and filter logic

### Integration Tests:
- User creation flow with email
- Deactivation constraints
- Bulk operations
- CSV export

### UI Tests:
- Form validation
- HTMX interactions
- Pagination behavior
- Bulk selection

### Security Tests:
- SQL injection attempts
- XSS in user inputs
- CSRF protection
- Authorization checks

## 🔗 Dependencies
- **Depends on**: 
  - STORY-020 (Authentication System)
  - STORY-021 (Admin Panel) 
  - STORY-022 (Role Management)
  - STORY-027 (Database Setup) - Required for User CRUD operations
- **Blocks**: 
  - STORY-024 (Access Control)

## 📌 Notes
- Use database transactions for user creation
- Implement optimistic locking for concurrent edits
- Consider adding user import feature later
- Profile photos in future iteration
- Activity logging should be async

## 📝 Dev Notes

### Key Implementation Details:

1. **Temporary Password Generation**:
   ```python
   import secrets
   import string
   
   def generate_temp_password(length=12):
       alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
       return ''.join(secrets.choice(alphabet) for _ in range(length))
   ```

2. **Email Template for Welcome**:
   ```
   Subject: Welcome to TechStore - Account Created
   
   Hello {{ user.full_name }},
   
   An account has been created for you at TechStore.
   
   Email: {{ user.email }}
   Temporary Password: {{ temp_password }}
   
   Please log in and change your password immediately.
   
   Login at: {{ login_url }}
   ```

3. **Audit Trail Structure**:
   ```python
   class UserAuditLog(Base):
       id = Column(Integer, primary_key=True)
       user_id = Column(Integer, ForeignKey("users.id"))
       action = Column(String)  # created, updated, deactivated, reactivated
       performed_by = Column(Integer, ForeignKey("users.id"))
       changes = Column(JSON)  # {"field": {"old": "value", "new": "value"}}
       timestamp = Column(DateTime, default=datetime.utcnow)
   ```

4. **Search Optimization**:
   ```sql
   -- Add indexes for search performance
   CREATE INDEX idx_users_full_name_trgm ON users USING gin(full_name gin_trgm_ops);
   CREATE INDEX idx_users_email_trgm ON users USING gin(email gin_trgm_ops);
   ```

### Testing Standards:
- Test files: `tests/test_crud/test_user.py`, `tests/test_services/test_user_service.py`
- Mock email sending in tests
- Use factory pattern for test users
- Test all constraint scenarios
- Verify audit logs are created

## 📊 Tasks / Subtasks

- [ ] **Create User Model Extensions** (AC: 10)
  - [ ] Add audit log model
  - [ ] Create indexes for search
  - [ ] Add created_by relationship
  - [ ] Run migrations

- [ ] **Implement User CRUD** (AC: 1, 2, 3, 4, 5)
  - [ ] Create get_users with pagination
  - [ ] Implement search functionality
  - [ ] Create user creation logic
  - [ ] Add update functionality
  - [ ] Implement soft delete

- [ ] **Build User Schemas** (AC: 3, 4)
  - [ ] Define input/output schemas
  - [ ] Add validation rules
  - [ ] Create response models
  - [ ] Add pagination schema

- [ ] **Create User Service Layer** (AC: 6, 7, 8, 9)
  - [ ] Implement business rules
  - [ ] Add constraint validations
  - [ ] Create password generation
  - [ ] Build email notifications

- [ ] **Develop API Endpoints** (AC: 1-12)
  - [ ] GET /api/v1/users (list with filters)
  - [ ] POST /api/v1/users (create)
  - [ ] PUT /api/v1/users/{id} (update)
  - [ ] POST /api/v1/users/{id}/toggle (activate/deactivate)
  - [ ] POST /api/v1/users/bulk (bulk operations)
  - [ ] GET /api/v1/users/export (CSV export)

- [ ] **Build Web Interface** (AC: 1, 2, 3, 4, 5, 11)
  - [ ] Create user list template
  - [ ] Build create/edit form
  - [ ] Add search and filters
  - [ ] Implement bulk selection
  - [ ] Add HTMX interactions

- [ ] **Implement Email System** (AC: 8, 9)
  - [ ] Set up email templates
  - [ ] Configure SMTP settings
  - [ ] Create welcome email
  - [ ] Build password reset email
  - [ ] Add email queue

- [ ] **Add Audit Trail** (AC: 10)
  - [ ] Create audit log table
  - [ ] Log all user changes
  - [ ] Build audit view
  - [ ] Add to user detail page

- [ ] **Implement CSV Export** (AC: 12)
  - [ ] Create export logic
  - [ ] Handle large datasets
  - [ ] Add proper escaping
  - [ ] Include selected columns

- [ ] **Add Security Measures** (DoD)
  - [ ] Validate all inputs
  - [ ] Add rate limiting
  - [ ] Implement CSRF protection
  - [ ] Test authorization

- [ ] **Create Comprehensive Tests** (DoD)
  - [ ] Unit test all CRUD operations
  - [ ] Integration test workflows
  - [ ] Test constraint validations
  - [ ] Security testing

- [ ] **Update Documentation** (DoD)
  - [ ] API documentation
  - [ ] User management guide
  - [ ] Security considerations
  - [ ] Audit trail explanation

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