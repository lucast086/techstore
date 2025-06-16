# Authentication System Documentation

## Overview

The TechStore authentication system has been simplified to use Django's built-in authentication and authorization framework. This provides a robust, well-tested foundation while keeping the codebase maintainable.

## Key Components

### User Model
- Extends Django's `AbstractUser`
- Additional fields:
  - `phone`: Phone number for contact
  - `date_joined`: Timestamp of user creation
- Uses Django's built-in groups for role management
- Includes audit logging for tracking user actions

### Roles (Groups)
The system uses Django's built-in Group model to represent roles:

1. **Administrador** (Administrator)
   - Full system access
   - Can manage users and permissions
   - Access to all modules

2. **Vendedor** (Salesperson)
   - Sales and customer management
   - Limited user access (view only)
   - Access to sales-related modules

3. **Técnico** (Technician)
   - Technical service management
   - Limited user access (view only)
   - Access to service-related modules

### Permissions
- Uses Django's built-in permission system
- Permissions are assigned to groups (roles)
- Users inherit permissions from their groups
- Custom permissions can be added per model

### Audit Logging
- `UserAuditLog` model tracks all significant user actions
- Records:
  - User who performed the action
  - Action type
  - Timestamp
  - IP address
  - User agent
  - Additional details in JSON format

## Usage Examples

### Checking User Roles
```python
# Check if user has a specific role
if user.has_role("Administrador"):
    # Admin-specific logic
    pass

# Get user's primary role
role = user.get_role()
if role:
    print(f"User role: {role.name}")
```

### Logging User Actions
```python
from users.models import UserAuditLog

# Log a user action
UserAuditLog.log_action(
    user=request.user,
    action="login",
    details={"method": "password"},
    request=request
)
```

### Django Admin Integration
- Custom UserAdmin with role display
- Audit log viewer (read-only)
- Group management with user count

## Migration from Custom System

The authentication system was simplified from a custom Permission/Role system to Django's built-in system. Benefits include:

1. **Reduced Complexity**: No custom permission caching logic
2. **Better Integration**: Works seamlessly with Django admin and third-party packages
3. **Well-Tested**: Django's auth system is battle-tested
4. **Easier Maintenance**: Less custom code to maintain

## Security Considerations

1. **Password Policies**: Configured in settings.py
2. **Session Management**: Uses Django's session framework
3. **CSRF Protection**: Enabled by default
4. **Permission Checks**: Use Django's `@permission_required` decorator

## Future Enhancements

See `pending_features.md` for planned authentication enhancements:
- Two-factor authentication (2FA)
- OAuth integration
- Advanced password policies
- Account lockout mechanisms 