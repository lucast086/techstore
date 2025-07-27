# STORY-018: Clean Codebase

## 📋 Story Details
- **Epic**: EPIC-001 (Foundation & Authentication)
- **Priority**: CRITICAL - Must be done first
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As a** developer of the system  
**I want to** eliminate all example code and dummy data  
**So that** I have a clean base to implement real functionalities

## ✅ Acceptance Criteria
- [ ] Remove all search API endpoints from `/api/v1/search.py`
- [ ] Remove DEMO_PRODUCTS data from `SearchService`
- [ ] Remove SearchResponse and CategoryResponse schemas
- [ ] Remove HTMX search routes from `/web/search.py`
- [ ] Keep base structure: main.py, config.py, database.py, dependencies.py
- [ ] Keep base.html template as foundation for layouts
- [ ] FastAPI server starts without errors after cleanup
- [ ] No references to example functionality remain in code

## 🔧 Technical Details

### Files to Remove/Clean:
```
src/app/
├── api/v1/search.py          # Remove completely
├── web/search.py             # Remove completely
├── services/search_service.py # Remove completely
├── schemas/search.py         # Remove completely
└── templates/
    └── welcome.html          # Clean or replace with login
```

### Files to Keep:
```
src/app/
├── main.py                   # Keep, but remove search routes
├── config.py                 # Keep as is
├── database.py               # Keep as is
├── dependencies.py           # Keep as is
├── models/base.py            # Keep as is
└── templates/
    └── base.html             # Keep as foundation
```

### Code Changes Required:

1. **main.py** - Remove search route includes:
```python
# Remove these lines:
# app.include_router(search_router, prefix="/api/v1")
# app.include_router(web_router)
```

2. **Create new welcome route**:
```python
@app.get("/")
async def root():
    return RedirectResponse(url="/login", status_code=302)
```

## 📝 Definition of Done
- [ ] All example code removed
- [ ] Server runs without errors
- [ ] No import errors
- [ ] Git commit with clear message
- [ ] Base structure intact for next stories

## 🧪 Testing Approach
1. Manual testing: Server starts successfully
2. No 404 errors on root path
3. Redirects to /login (which will 404 until Story #19)

## 🔗 Dependencies
- **Blocks**: All other stories
- **Blocked by**: None

## 📌 Notes
- This is a cleanup task, no new features
- Preserve the application structure
- Keep configuration and base files intact
- This sets the foundation for authentication implementation