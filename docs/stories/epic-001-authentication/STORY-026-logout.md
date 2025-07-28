# STORY-026: Logout

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: MEDIUM
- **Estimate**: 0.5 days
- **Status**: TODO

## 🎯 User Story
**As** any authenticated user (María or Carlos),  
**I want** to securely log out of the system,  
**So that** my session is properly terminated and my account remains secure when I'm not using the application

## ✅ Acceptance Criteria
1. [ ] Logout button/link available in user menu
2. [ ] Logout clears all authentication tokens (access and refresh)
3. [ ] Server-side session is invalidated
4. [ ] Browser cookies are cleared
5. [ ] Redirect to login page after logout
6. [ ] Show success message "You have been logged out"
7. [ ] Cannot access protected pages after logout
8. [ ] Browser back button doesn't show cached protected pages
9. [ ] Logout works even if refresh token is expired
10. [ ] Audit log records logout event with timestamp

## 🔧 Technical Details

### Files to Update:
```
src/app/
├── api/v1/
│   └── auth.py              # Add logout endpoint
├── web/
│   └── auth.py              # Add logout route
├── templates/
│   ├── partials/
│   │   └── header.html      # Add logout button
│   └── auth/
│       └── logout_success.html # Logout confirmation
└── static/
    └── js/
        └── auth.js          # Logout handling
```

### Implementation Requirements:

1. **Logout API Endpoint** (Update `api/v1/auth.py`):
```python
@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user and invalidate session
    """
    try:
        # Get refresh token from cookies
        refresh_token = request.cookies.get("refresh_token")
        
        # Invalidate refresh token in database
        if refresh_token:
            db.execute(
                "UPDATE refresh_tokens SET revoked = true WHERE token = :token",
                {"token": refresh_token}
            )
            db.commit()
        
        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        # Log the logout event
        audit_log = AuditLog(
            user_id=current_user.id,
            action="logout",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        # Even if something fails, clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return {"message": "Logged out"}
```

2. **Web Logout Route** (Update `web/auth.py`):
```python
@router.post("/logout")
async def logout_web(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Web logout with redirect
    """
    if current_user:
        # Call API logout
        await logout(request, response, current_user, request.state.db)
    
    # Clear any session data
    request.session.clear()
    
    # Set cache control headers
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    # Redirect to login with message
    return RedirectResponse(
        url="/login?message=You have been logged out",
        status_code=303  # See Other - proper redirect after POST
    )

@router.get("/logout")
async def logout_get(request: Request):
    """
    Handle GET logout (from links) - show confirmation
    """
    return templates.TemplateResponse("auth/logout_confirm.html", {
        "request": request
    })
```

3. **Update Header Template** (`templates/partials/header.html`):
```html
<header class="app-header">
    <div class="header-content">
        <div class="header-left">
            <a href="/" class="logo">TechStore</a>
        </div>
        
        <div class="header-right">
            {% if current_user %}
            <div class="user-menu">
                <button class="user-menu-trigger">
                    <span>{{ current_user.full_name }}</span>
                    <svg><!-- chevron-down icon --></svg>
                </button>
                
                <div class="user-menu-dropdown">
                    <a href="/profile" class="menu-item">
                        <svg><!-- user icon --></svg>
                        Profile
                    </a>
                    
                    {% if current_user.role == 'admin' %}
                    <a href="/admin" class="menu-item">
                        <svg><!-- settings icon --></svg>
                        Admin Panel
                    </a>
                    {% endif %}
                    
                    <hr class="menu-divider">
                    
                    <form action="/logout" method="POST" class="logout-form">
                        <button type="submit" class="menu-item logout-button">
                            <svg><!-- logout icon --></svg>
                            Logout
                        </button>
                    </form>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</header>
```

4. **Logout Confirmation Page** (`templates/auth/logout_confirm.html`):
```html
{% extends "base.html" %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <h2>Confirm Logout</h2>
        <p>Are you sure you want to log out?</p>
        
        <form action="/logout" method="POST" class="logout-confirm-form">
            <button type="submit" class="btn-primary">
                Yes, Log Out
            </button>
            <a href="{{ request.headers.get('referer', '/') }}" class="btn-secondary">
                Cancel
            </a>
        </form>
    </div>
</div>
{% endblock %}
```

5. **Client-Side Logout Handling** (`static/js/auth.js`):
```javascript
// Enhanced logout with cleanup
class AuthManager {
    async logout() {
        try {
            // Show loading state
            this.showLoading('Logging out...');
            
            // Call logout endpoint
            const response = await fetch('/api/v1/auth/logout', {
                method: 'POST',
                credentials: 'same-origin'
            });
            
            // Clear local storage
            localStorage.clear();
            sessionStorage.clear();
            
            // Clear any cached data
            if ('caches' in window) {
                const cacheNames = await caches.keys();
                await Promise.all(
                    cacheNames.map(name => caches.delete(name))
                );
            }
            
            // Redirect to login
            window.location.href = '/login?message=You have been logged out';
            
        } catch (error) {
            console.error('Logout error:', error);
            // Even on error, redirect to login
            window.location.href = '/login';
        }
    }
    
    // Auto-logout on token expiration
    setupAutoLogout() {
        // Listen for 401 responses
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            
            if (response.status === 401) {
                // Token expired, auto logout
                this.logout();
            }
            
            return response;
        };
    }
    
    // Prevent back button after logout
    preventBackButton() {
        // Replace current history entry
        history.pushState(null, '', location.href);
        
        window.addEventListener('popstate', () => {
            history.pushState(null, '', location.href);
            
            // Check if still authenticated
            fetch('/api/v1/auth/me')
                .then(res => {
                    if (!res.ok) {
                        window.location.href = '/login';
                    }
                })
                .catch(() => {
                    window.location.href = '/login';
                });
        });
    }
}

// Initialize on protected pages
document.addEventListener('DOMContentLoaded', () => {
    const authManager = new AuthManager();
    authManager.setupAutoLogout();
    authManager.preventBackButton();
});
```

6. **Security Headers Middleware**:
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Prevent caching of protected pages
    if request.url.path not in ['/login', '/static', '/']:
        response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
        response.headers["Expires"] = "-1"
        response.headers["Pragma"] = "no-cache"
    
    return response
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Logout completes in < 500ms
- [ ] All tokens properly invalidated
- [ ] No security vulnerabilities
- [ ] Audit trail working
- [ ] Browser caching prevented
- [ ] Mobile-friendly logout
- [ ] Works across all browsers

## 🧪 Testing Approach

### Unit Tests:
- Token invalidation logic
- Cookie clearing
- Audit log creation
- Error handling

### Integration Tests:
- Complete logout flow
- Protected page access after logout
- Multiple session handling
- Expired token handling

### Security Tests:
- Token reuse after logout
- Session fixation
- Back button behavior
- Cache clearing

### UI Tests:
- Logout button visibility
- Confirmation flow
- Redirect behavior
- Message display

## 🔗 Dependencies
- **Depends on**: 
  - STORY-020 (Authentication System)
  - STORY-021 (Admin Panel)
  - STORY-027 (Database Setup) - Required for token/session management
- **Blocks**: None

## 📌 Notes
- Consider implementing "Logout from all devices" feature
- Add logout reason tracking for security
- Implement session timeout warnings
- Consider WebSocket disconnection on logout
- Future: Single Sign-Out (SSO) support

## 📝 Dev Notes

### Key Implementation Details:

1. **Refresh Token Revocation**:
   ```python
   # Database table for refresh tokens
   class RefreshToken(Base):
       __tablename__ = "refresh_tokens"
       
       id = Column(Integer, primary_key=True)
       token = Column(String, unique=True, index=True)
       user_id = Column(Integer, ForeignKey("users.id"))
       expires_at = Column(DateTime)
       revoked = Column(Boolean, default=False)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

2. **Comprehensive Cookie Clearing**:
   ```python
   def clear_auth_cookies(response: Response):
       cookies_to_clear = [
           "access_token",
           "refresh_token",
           "session_id",
           "csrf_token"
       ]
       
       for cookie in cookies_to_clear:
           response.delete_cookie(
               key=cookie,
               path="/",
               domain=None,
               secure=True,
               httponly=True
           )
   ```

3. **Audit Log Entry**:
   ```python
   def log_logout(user_id: int, request: Request, db: Session):
       audit_entry = {
           "user_id": user_id,
           "action": "user_logout",
           "ip_address": request.client.host,
           "user_agent": request.headers.get("user-agent"),
           "timestamp": datetime.utcnow(),
           "details": {
               "logout_type": "manual",  # vs timeout, forced
               "session_duration": calculate_session_duration(user_id)
           }
       }
       # Save to database
   ```

4. **Client-Side Cache Busting**:
   ```javascript
   // Force reload without cache
   function forceReload() {
       // Append timestamp to prevent caching
       const timestamp = new Date().getTime();
       window.location.href = `/login?_=${timestamp}&message=You have been logged out`;
   }
   ```

### Testing Standards:
- Test files: `tests/test_api/test_auth_logout.py`
- Mock token storage
- Test with expired tokens
- Verify all cleanup actions
- Test concurrent logouts

## 📊 Tasks / Subtasks

- [ ] **Update Auth API** (AC: 2, 3, 9)
  - [ ] Add POST /logout endpoint
  - [ ] Implement token revocation
  - [ ] Clear server session
  - [ ] Handle errors gracefully

- [ ] **Create Web Routes** (AC: 5, 6)
  - [ ] Add logout POST route
  - [ ] Add logout GET route
  - [ ] Implement proper redirects
  - [ ] Add success message

- [ ] **Update UI Components** (AC: 1)
  - [ ] Add logout to user menu
  - [ ] Create logout button styling
  - [ ] Add logout icon
  - [ ] Make mobile-friendly

- [ ] **Implement Cookie Clearing** (AC: 4)
  - [ ] Clear auth cookies
  - [ ] Set proper cookie options
  - [ ] Clear all domains/paths
  - [ ] Test in all browsers

- [ ] **Add Security Headers** (AC: 8)
  - [ ] Prevent page caching
  - [ ] Add no-store headers
  - [ ] Set expires headers
  - [ ] Test back button

- [ ] **Create Audit Logging** (AC: 10)
  - [ ] Log logout events
  - [ ] Include timestamp
  - [ ] Track logout method
  - [ ] Store IP address

- [ ] **Build Confirmation Page** (AC: 1)
  - [ ] Create logout confirmation
  - [ ] Add cancel option
  - [ ] Style with design system
  - [ ] Handle form submission

- [ ] **Implement Client Cleanup** (AC: 7, 8)
  - [ ] Clear local storage
  - [ ] Clear session storage
  - [ ] Clear caches
  - [ ] Prevent back navigation

- [ ] **Handle Edge Cases** (AC: 9)
  - [ ] Expired token logout
  - [ ] Already logged out
  - [ ] Network errors
  - [ ] Multiple tabs

- [ ] **Add Comprehensive Tests** (DoD)
  - [ ] Test logout flow
  - [ ] Verify token invalidation
  - [ ] Test protected access
  - [ ] Check audit logs

- [ ] **Security Validation** (DoD)
  - [ ] Test token reuse
  - [ ] Verify session cleared
  - [ ] Check cache headers
  - [ ] Penetration testing

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