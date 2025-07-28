# STORY-022: Role Management

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** María (administrator),  
**I want** to define and manage user roles with specific permissions,  
**So that** I can control what different types of users can access and do within the system

## ✅ Acceptance Criteria
1. [ ] Two default roles exist: "admin" and "technician"
2. [ ] Admin role has full system access
3. [ ] Technician role has limited access (no user management, no settings)
4. [ ] Role-permission mapping is defined in configuration
5. [ ] Permissions are granular (e.g., "users.create", "users.read", "products.write")
6. [ ] Role check happens at API and UI level
7. [ ] Unauthorized actions show clear error message
8. [ ] Role changes take effect immediately (no re-login required)
9. [ ] Super admin (first user) cannot be downgraded
10. [ ] Role assignments are logged for audit trail

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── core/
│   └── permissions.py       # Permission system
├── models/
│   ├── role.py             # Role model
│   └── permission.py       # Permission model
├── schemas/
│   └── role.py             # Role schemas
└── config/
    └── roles.py            # Role configuration
```

### Implementation Requirements:

1. **Permission System** (`core/permissions.py`):
```python
from enum import Enum

class Permission(str, Enum):
    # User permissions
    USERS_CREATE = "users.create"
    USERS_READ = "users.read"
    USERS_UPDATE = "users.update"
    USERS_DELETE = "users.delete"
    
    # Product permissions
    PRODUCTS_CREATE = "products.create"
    PRODUCTS_READ = "products.read"
    PRODUCTS_UPDATE = "products.update"
    PRODUCTS_DELETE = "products.delete"
    
    # Sales permissions
    SALES_CREATE = "sales.create"
    SALES_READ = "sales.read"
    SALES_UPDATE = "sales.update"
    
    # Admin permissions
    SETTINGS_MANAGE = "settings.manage"
    ROLES_MANAGE = "roles.manage"
    LOGS_VIEW = "logs.view"

# Role definitions
ROLE_PERMISSIONS = {
    "admin": [p.value for p in Permission],  # All permissions
    "technician": [
        Permission.PRODUCTS_READ,
        Permission.PRODUCTS_UPDATE,
        Permission.SALES_CREATE,
        Permission.SALES_READ,
        Permission.SALES_UPDATE,
    ]
}
```

2. **Permission Decorator**:
```python
def require_permission(permission: Permission):
    def permission_decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not has_permission(user, permission):
                raise HTTPException(403, "Permission denied")
            return await func(*args, **kwargs)
        return wrapper
    return permission_decorator
```

3. **Frontend Permission Check**:
```python
def user_can(user: User, permission: str) -> bool:
    """Check if user has specific permission"""
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    return permission in user_permissions
```

4. **Template Helper**:
```html
<!-- Jinja2 custom filter -->
{% if current_user|can('users.create') %}
    <button>Add User</button>
{% endif %}
```

5. **API Permission Guards**:
```python
@router.post("/users", dependencies=[Depends(require_permission(Permission.USERS_CREATE))])
async def create_user(user_data: UserCreate):
    # Create user logic
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Permission system fully tested
- [ ] Role-based UI elements hide/show correctly
- [ ] API endpoints return 403 for unauthorized access
- [ ] Permission checks < 1ms performance
- [ ] Audit logging implemented
- [ ] Documentation updated with permission list

## 🧪 Testing Approach

### Unit Tests:
- Permission checking logic
- Role-permission mapping
- Permission inheritance

### Integration Tests:
- API endpoint access with different roles
- UI element visibility based on permissions
- Role change effects
- Super admin protection

### Security Tests:
- Permission bypass attempts
- Role escalation prevention
- Token manipulation with different roles

## 🔗 Dependencies
- **Depends on**: 
  - STORY-020 (Authentication system)
  - STORY-021 (Admin Panel)
  - STORY-027 (Database Setup) - Required for role/permission models
- **Blocks**: 
  - STORY-023 (User Management)
  - STORY-024 (Access Control)

## 📌 Notes
- Consider RBAC (Role-Based Access Control) best practices
- Permissions should be additive, not subtractive
- Future: Custom roles with configurable permissions
- Cache permission checks for performance
- Use database for dynamic permissions later

## 📝 Dev Notes

### Key Implementation Details:

1. **Permission Checking Flow**:
   ```
   Request → Auth Middleware → Get User → Check Role → Get Permissions → Allow/Deny
   ```

2. **Caching Strategy**:
   ```python
   # Cache permissions in JWT token
   token_data = {
       "sub": user.id,
       "role": user.role,
       "permissions": ROLE_PERMISSIONS[user.role]  # Include in token
   }
   ```

3. **UI Permission Helper**:
   ```python
   @app.template_filter('can')
   def can_filter(user, permission):
       return permission in ROLE_PERMISSIONS.get(user.role, [])
   ```

4. **Audit Logging**:
   ```python
   def log_permission_denied(user_id, permission, endpoint):
       logger.warning(f"Permission denied: user={user_id}, perm={permission}, endpoint={endpoint}")
   ```

### Testing Standards:
- Test files: `tests/test_core/test_permissions.py`
- Test each role against each permission
- Test permission inheritance
- Mock different user roles

## 📊 Tasks / Subtasks

- [ ] **Define Permission Enum** (AC: 5)
  - [ ] Create comprehensive permission list
  - [ ] Group by resource (users, products, etc.)
  - [ ] Use clear naming convention
  - [ ] Document each permission

- [ ] **Create Role-Permission Mapping** (AC: 1, 2, 3, 4)
  - [ ] Define admin role with all permissions
  - [ ] Define technician role with limited permissions
  - [ ] Store in configuration file
  - [ ] Make it easily extendable

- [ ] **Implement Permission Checker** (AC: 6)
  - [ ] Create has_permission function
  - [ ] Add caching for performance
  - [ ] Handle missing roles gracefully
  - [ ] Log permission checks in debug mode

- [ ] **Create Permission Decorator** (AC: 6, 7)
  - [ ] Build require_permission decorator
  - [ ] Extract user from request context
  - [ ] Return 403 with clear message
  - [ ] Add to all protected endpoints

- [ ] **Add Template Helpers** (AC: 6)
  - [ ] Create Jinja2 filter for permission check
  - [ ] Add to template context
  - [ ] Document usage for developers
  - [ ] Create examples

- [ ] **Update User Model** (AC: 8, 9)
  - [ ] Ensure role field exists
  - [ ] Add role change tracking
  - [ ] Implement super admin check
  - [ ] Add role validation

- [ ] **Implement Role Change Logic** (AC: 8, 9, 10)
  - [ ] Create role update endpoint
  - [ ] Validate role changes
  - [ ] Prevent super admin downgrade
  - [ ] Log all role changes

- [ ] **Update API Endpoints** (AC: 6, 7)
  - [ ] Add permission checks to all endpoints
  - [ ] Use appropriate permissions
  - [ ] Test with different roles
  - [ ] Update API documentation

- [ ] **Update UI Components** (AC: 6, 7)
  - [ ] Hide/show buttons based on permissions
  - [ ] Disable unauthorized actions
  - [ ] Show permission errors clearly
  - [ ] Test all UI elements

- [ ] **Add Comprehensive Tests** (DoD)
  - [ ] Unit test permission logic
  - [ ] Integration test API access
  - [ ] Test UI element visibility
  - [ ] Test audit logging

- [ ] **Create Permission Documentation** (DoD)
  - [ ] List all permissions
  - [ ] Document role assignments
  - [ ] Create permission matrix
  - [ ] Add to developer guide

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