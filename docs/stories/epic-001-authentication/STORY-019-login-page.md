# STORY-019: Login Page

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: CRITICAL
- **Estimate**: 1 day
- **Status**: IN PROGRESS 🔄

## 🎯 User Story
**As** María (administrator) or Carlos (technician)  
**I want to** see a login form when entering the main page  
**So that** I can authenticate and securely access the system

## ✅ Acceptance Criteria
- [x] Accessing root URL ("/") shows login form
- [x] Form has email/username and password fields
- [x] Fields have visual validation (required)
- [x] "Sign In" button to submit form
- [x] Responsive design works on mobile devices
- [x] TechStore logo/name displayed on page
- [ ] If already authenticated, redirect to dashboard (pending auth implementation)

## 🔧 Technical Details

### New Files:
```
src/app/
├── web/
│   └── auth.py              # Auth routes
└── templates/
    └── auth/
        └── login.html       # Login page template
```

### Implementation:

1. **Create auth router** (`web/auth.py`):
```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )
```

2. **Login template** (`templates/auth/login.html`):
```html
{% extends "base.html" %}
{% block title %}Login - TechStore{% endblock %}
{% block content %}
<div class="min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full space-y-8">
        <div>
            <h1 class="text-center text-3xl font-bold">TechStore</h1>
            <h2 class="text-center text-xl">Business Management System</h2>
        </div>
        <form class="mt-8 space-y-6" 
              hx-post="/api/v1/auth/login" 
              hx-target="#error-message">
            <div>
                <label for="email" class="block text-sm font-medium">
                    Email
                </label>
                <input id="email" 
                       name="email" 
                       type="email" 
                       required 
                       class="mt-1 block w-full rounded-md border-gray-300">
            </div>
            <div>
                <label for="password" class="block text-sm font-medium">
                    Password
                </label>
                <input id="password" 
                       name="password" 
                       type="password" 
                       required 
                       class="mt-1 block w-full rounded-md border-gray-300">
            </div>
            <div id="error-message"></div>
            <button type="submit" 
                    class="w-full py-2 px-4 bg-blue-600 text-white rounded-md">
                Sign In
            </button>
        </form>
    </div>
</div>
{% endblock %}
```

3. **Update main.py**:
```python
from app.web import auth

# Add auth routes
app.include_router(auth.router, tags=["auth"])

# Root redirect
@app.get("/")
async def root():
    return RedirectResponse(url="/login")
```

## 📝 Definition of Done
- [x] Login page displays at /login
- [x] Form is visually appealing and centered
- [x] All form fields are present and required
- [x] Mobile responsive (test at 375px width)
- [x] Root URL redirects to /login
- [x] No console errors

## 🧪 Testing Approach
1. Navigate to http://localhost:8000/ → redirects to /login
2. Check form displays correctly
3. Verify required field validation
4. Test responsive design
5. Form submission (will fail until Story #20)

## 🔗 Dependencies
- **Depends on**: STORY-018 (Clean codebase)
- **Blocks**: STORY-020 (Authentication system)

## 📌 Notes
- Use Tailwind CSS classes from base.html
- Form uses HTMX for future AJAX submission
- Keep design clean and professional
- This is UI only, no backend logic yet

## 📝 Dev Agent Record

### Agent Model Used
- Claude Opus 4 (claude-opus-4-20250514)

### Completion Notes
- Login page successfully implemented with all UI requirements
- HTMX integration prepared for backend authentication
- Responsive design tested and working
- Professional UI with TechStore branding

### Files Created
- src/app/web/auth.py - Auth router with login route
- src/app/templates/auth/login.html - Complete login form template

### Files Modified
- src/app/main.py - Added auth router and root redirect

### Implementation Details
- Email field with HTML5 validation and proper autocomplete
- Password field with security attributes
- Loading indicator for form submission
- Error message container for validation feedback
- Tailwind CSS for responsive, professional styling
- HTMX attributes for future AJAX form submission

### Pending Work
- Authentication redirect functionality blocked by STORY-020
- Cannot verify "If already authenticated, redirect to dashboard" until auth system is implemented