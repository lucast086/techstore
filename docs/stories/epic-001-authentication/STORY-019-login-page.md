# STORY-019: Login Page

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: CRITICAL
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** María (administrator) or Carlos (technician)  
**I want to** see a login form when entering the main page  
**So that** I can authenticate and securely access the system

## ✅ Acceptance Criteria
- [ ] Accessing root URL ("/") shows login form
- [ ] Form has email/username and password fields
- [ ] Fields have visual validation (required)
- [ ] "Sign In" button to submit form
- [ ] Responsive design works on mobile devices
- [ ] TechStore logo/name displayed on page
- [ ] If already authenticated, redirect to dashboard

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
- [ ] Login page displays at /login
- [ ] Form is visually appealing and centered
- [ ] All form fields are present and required
- [ ] Mobile responsive (test at 375px width)
- [ ] Root URL redirects to /login
- [ ] No console errors

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