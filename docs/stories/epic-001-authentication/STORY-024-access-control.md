# STORY-024: Access Control

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** Carlos (technician),  
**I want** the system to enforce proper access control based on my role,  
**So that** I can only access features and data appropriate to my responsibilities while being prevented from accessing administrative functions

## ✅ Acceptance Criteria
1. [ ] All API endpoints enforce role-based permissions
2. [ ] UI elements hide/disable based on user permissions
3. [ ] Direct URL access to unauthorized pages shows 403 error
4. [ ] API calls return 403 Forbidden for unauthorized access
5. [ ] Permission denied messages are user-friendly
6. [ ] Navigation menu only shows accessible items
7. [ ] Buttons/actions are hidden if user lacks permission
8. [ ] Form fields are read-only based on permissions
9. [ ] Bulk operations respect individual item permissions
10. [ ] Access control is consistent between UI and API

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── middleware/
│   └── permissions.py       # Permission middleware
├── core/
│   └── access_control.py    # Access control utilities
├── templates/
│   ├── errors/
│   │   └── 403.html        # Permission denied page
│   └── components/
│       └── permission_check.html
└── static/
    └── js/
        └── permissions.js   # Client-side permission helpers
```

### Implementation Requirements:

1. **Permission Middleware** (`middleware/permissions.py`):
```python
from functools import wraps
from fastapi import HTTPException, Depends
from app.core.permissions import Permission, has_permission

class PermissionChecker:
    def __init__(self, permission: Permission):
        self.permission = permission
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        if not has_permission(current_user, self.permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied. Required: {self.permission.value}"
            )
        return current_user

# Decorator for route protection
def require_permission(permission: Permission):
    return Depends(PermissionChecker(permission))

# Check multiple permissions (AND)
def require_all_permissions(*permissions: Permission):
    def check_all(current_user: User = Depends(get_current_user)):
        for permission in permissions:
            if not has_permission(current_user, permission):
                raise HTTPException(403, f"Missing permission: {permission.value}")
        return current_user
    return Depends(check_all)

# Check any permission (OR)
def require_any_permission(*permissions: Permission):
    def check_any(current_user: User = Depends(get_current_user)):
        if not any(has_permission(current_user, p) for p in permissions):
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return Depends(check_any)
```

2. **Access Control Utilities** (`core/access_control.py`):
```python
from typing import Dict, List, Any
from app.core.permissions import Permission, ROLE_PERMISSIONS

class AccessControl:
    @staticmethod
    def filter_by_permissions(items: List[Dict], user: User, 
                            permission_field: str = "required_permission") -> List[Dict]:
        """Filter list of items based on user permissions"""
        return [
            item for item in items
            if not item.get(permission_field) or 
               has_permission(user, item[permission_field])
        ]
    
    @staticmethod
    def can_access_resource(user: User, resource: Any, 
                          permission: Permission) -> bool:
        """Check if user can access specific resource"""
        # Check base permission
        if not has_permission(user, permission):
            return False
        
        # Check resource-specific rules
        if hasattr(resource, 'owner_id'):
            # Users can always access their own resources
            if resource.owner_id == user.id:
                return True
        
        return True
    
    @staticmethod
    def apply_field_permissions(data: Dict, user: User, 
                              field_permissions: Dict[str, Permission]) -> Dict:
        """Remove fields user doesn't have permission to see"""
        filtered_data = {}
        for field, value in data.items():
            required_perm = field_permissions.get(field)
            if not required_perm or has_permission(user, required_perm):
                filtered_data[field] = value
        return filtered_data
```

3. **Template Permission Helpers**:
```python
# Add to template context
@app.context_processor
def inject_permissions():
    def can(permission: str) -> bool:
        user = get_current_user()
        if not user:
            return False
        return permission in ROLE_PERMISSIONS.get(user.role, [])
    
    def can_any(*permissions: str) -> bool:
        user = get_current_user()
        if not user:
            return False
        user_perms = ROLE_PERMISSIONS.get(user.role, [])
        return any(p in user_perms for p in permissions)
    
    def can_all(*permissions: str) -> bool:
        user = get_current_user()
        if not user:
            return False
        user_perms = ROLE_PERMISSIONS.get(user.role, [])
        return all(p in user_perms for p in permissions)
    
    return dict(can=can, can_any=can_any, can_all=can_all)
```

4. **UI Permission Checks** (`templates/components/permission_check.html`):
```html
<!-- Macro for permission-based rendering -->
{% macro if_can(permission) %}
  {% if can(permission) %}
    {{ caller() }}
  {% endif %}
{% endmacro %}

{% macro unless_can(permission) %}
  {% if not can(permission) %}
    {{ caller() }}
  {% endif %}
{% endmacro %}

<!-- Usage examples -->
{% call if_can('users.create') %}
  <button class="btn-primary">Create User</button>
{% endcall %}

{% call unless_can('settings.manage') %}
  <div class="alert alert-info">
    Contact an administrator to change system settings.
  </div>
{% endcall %}
```

5. **Navigation Filtering**:
```python
# Dynamic navigation based on permissions
NAVIGATION_ITEMS = [
    {
        'label': 'Dashboard',
        'url': '/',
        'icon': 'home',
        'permission': None  # Available to all
    },
    {
        'label': 'Users',
        'url': '/users',
        'icon': 'users',
        'permission': 'users.read'
    },
    {
        'label': 'Products',
        'url': '/products',
        'icon': 'box',
        'permission': 'products.read'
    },
    {
        'label': 'Settings',
        'url': '/settings',
        'icon': 'cog',
        'permission': 'settings.manage'
    }
]

def get_user_navigation(user: User) -> List[Dict]:
    return AccessControl.filter_by_permissions(
        NAVIGATION_ITEMS, user, 'permission'
    )
```

6. **Error Pages** (`templates/errors/403.html`):
```html
{% extends "base.html" %}

{% block content %}
<div class="error-page">
    <div class="error-content">
        <h1 class="error-code">403</h1>
        <h2 class="error-title">Access Denied</h2>
        <p class="error-message">
            You don't have permission to access this resource.
        </p>
        
        {% if specific_permission %}
        <p class="error-detail">
            Required permission: <code>{{ specific_permission }}</code>
        </p>
        {% endif %}
        
        <div class="error-actions">
            <a href="/" class="btn-primary">Go to Dashboard</a>
            <a href="javascript:history.back()" class="btn-secondary">Go Back</a>
        </div>
    </div>
</div>
{% endblock %}
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Permission checks < 1ms overhead
- [ ] No permission bypasses possible
- [ ] UI gracefully handles permission denials
- [ ] API returns consistent error responses
- [ ] Navigation dynamically filtered
- [ ] Test coverage > 90%
- [ ] Security audit passed

## 🧪 Testing Approach

### Unit Tests:
- Permission checking logic
- Access control utilities
- Navigation filtering
- Field-level permissions

### Integration Tests:
- API endpoint protection
- UI element visibility
- Permission inheritance
- Resource access rules

### Security Tests:
- Direct URL access attempts
- API permission bypass attempts
- Token manipulation
- SQL injection via permissions

### UI Tests:
- Button/element visibility
- Form field states
- Navigation menu filtering
- Error page display

## 🔗 Dependencies
- **Depends on**: 
  - STORY-020 (Authentication System)
  - STORY-022 (Role Management)
  - STORY-023 (User Management)
  - STORY-027 (Database Setup) - Required for permission checks
- **Blocks**: 
  - STORY-025 (Dashboard)

## 📌 Notes
- Cache permission checks per request
- Consider Redis for permission caching
- Log all permission denials for security audit
- Implement gradual degradation for UI
- Future: Dynamic permission assignment

## 📝 Dev Notes

### Key Implementation Details:

1. **API Protection Pattern**:
   ```python
   # Protect entire router
   router = APIRouter(dependencies=[Depends(require_permission(Permission.USERS_READ))])
   
   # Protect specific endpoint
   @router.post("/users", dependencies=[Depends(require_permission(Permission.USERS_CREATE))])
   async def create_user(user: UserCreate):
       pass
   
   # Multiple permissions
   @router.delete("/users/{id}", dependencies=[
       Depends(require_all_permissions(Permission.USERS_DELETE, Permission.USERS_WRITE))
   ])
   async def delete_user(id: int):
       pass
   ```

2. **Request-Level Permission Cache**:
   ```python
   # Store computed permissions in request state
   async def cache_user_permissions(request: Request, call_next):
       if hasattr(request.state, "user"):
           user = request.state.user
           request.state.permissions = set(ROLE_PERMISSIONS.get(user.role, []))
       response = await call_next(request)
       return response
   ```

3. **Client-Side Permission Helper**:
   ```javascript
   // permissions.js
   class PermissionManager {
       constructor(userPermissions) {
           this.permissions = new Set(userPermissions);
       }
       
       can(permission) {
           return this.permissions.has(permission);
       }
       
       canAny(...permissions) {
           return permissions.some(p => this.permissions.has(p));
       }
       
       updateUI() {
           // Hide elements with data-permission attribute
           document.querySelectorAll('[data-permission]').forEach(el => {
               const required = el.dataset.permission;
               el.style.display = this.can(required) ? '' : 'none';
           });
           
           // Disable form fields
           document.querySelectorAll('[data-permission-readonly]').forEach(el => {
               const required = el.dataset.permissionReadonly;
               el.disabled = !this.can(required);
           });
       }
   }
   ```

4. **Consistent Error Response**:
   ```python
   class PermissionDeniedResponse(BaseModel):
       error: str = "permission_denied"
       message: str
       required_permission: Optional[str]
       user_role: str
       timestamp: datetime
   ```

### Testing Standards:
- Test files: `tests/test_middleware/test_permissions.py`
- Test all permission combinations
- Mock different user roles
- Verify UI element states
- Check API response consistency

## 📊 Tasks / Subtasks

- [ ] **Create Permission Middleware** (AC: 1, 4, 5)
  - [ ] Build PermissionChecker class
  - [ ] Implement dependency decorators
  - [ ] Add user-friendly error messages
  - [ ] Handle missing permissions gracefully

- [ ] **Build Access Control Utilities** (AC: 9, 10)
  - [ ] Create resource filtering functions
  - [ ] Implement field-level permissions
  - [ ] Add permission checking helpers
  - [ ] Build caching mechanism

- [ ] **Update API Endpoints** (AC: 1, 4, 10)
  - [ ] Add permission decorators to all routes
  - [ ] Implement consistent error responses
  - [ ] Test each endpoint with different roles
  - [ ] Document required permissions

- [ ] **Create Template Helpers** (AC: 2, 7, 8)
  - [ ] Build Jinja2 permission filters
  - [ ] Create permission check macros
  - [ ] Add to template context
  - [ ] Document usage patterns

- [ ] **Implement Navigation Filtering** (AC: 6)
  - [ ] Define navigation structure
  - [ ] Add permission requirements
  - [ ] Filter based on user role
  - [ ] Cache filtered navigation

- [ ] **Build Error Pages** (AC: 3, 5)
  - [ ] Create 403 error template
  - [ ] Add helpful error messages
  - [ ] Include navigation options
  - [ ] Style with design system

- [ ] **Add Client-Side Helpers** (AC: 2, 7)
  - [ ] Create JavaScript permission manager
  - [ ] Hide/show elements dynamically
  - [ ] Handle HTMX responses
  - [ ] Update UI after permission changes

- [ ] **Implement Form Field Control** (AC: 8)
  - [ ] Add permission attributes to forms
  - [ ] Make fields read-only as needed
  - [ ] Handle form submission
  - [ ] Show appropriate messages

- [ ] **Handle Bulk Operations** (AC: 9)
  - [ ] Check permissions per item
  - [ ] Filter unauthorized items
  - [ ] Return partial success results
  - [ ] Log permission denials

- [ ] **Create Permission Tests** (DoD)
  - [ ] Unit test all utilities
  - [ ] Integration test endpoints
  - [ ] Test UI element visibility
  - [ ] Security penetration tests

- [ ] **Optimize Performance** (DoD)
  - [ ] Implement permission caching
  - [ ] Measure check overhead
  - [ ] Optimize database queries
  - [ ] Add performance tests

- [ ] **Document Access Control** (DoD)
  - [ ] List all permissions
  - [ ] Document protection patterns
  - [ ] Create developer guide
  - [ ] Add to API documentation

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