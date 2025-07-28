# STORY-029: Customer Registration

## 📋 Story Details
- **Epic**: EPIC-002 (Customer Management)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** María or Carlos,  
**I want** to register new customers with their information,  
**So that** I can track their purchases and provide personalized service

## ✅ Acceptance Criteria
1. [ ] Registration form accessible from customer list page
2. [ ] Required fields: name and primary phone (clearly marked)
3. [ ] Optional fields: secondary phone, email, address, notes
4. [ ] Real-time duplicate phone check while typing
5. [ ] Form validation with clear error messages
6. [ ] Success notification after registration
7. [ ] Redirect to customer profile after creation
8. [ ] Cancel button returns to customer list
9. [ ] Tab order logical for quick data entry
10. [ ] Phone fields accept any format (flexible input)

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── api/v1/
│   └── customers.py         # Customer API endpoints
├── web/
│   └── customers.py         # Customer web routes
├── templates/
│   └── customers/
│       ├── list.html        # Customer list page
│       ├── form.html        # Registration/Edit form
│       └── partials/
│           ├── customer_card.html
│           └── phone_check.html
└── static/
    └── js/
        └── customer-form.js # Form interactions
```

### Implementation Requirements:

1. **Customer API Endpoints** (`app/api/v1/customers.py`):
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.crud.customer import customer_crud
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new customer"""
    try:
        db_customer = customer_crud.create(
            db=db,
            customer=customer,
            created_by_id=current_user.id
        )
        
        # Return with calculated fields
        return CustomerResponse(
            **db_customer.to_dict(),
            created_by_name=current_user.full_name,
            balance=0.0,  # New customer has zero balance
            transaction_count=0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/check-phone")
async def check_phone_availability(
    phone: str = Query(..., min_length=1),
    exclude_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Check if phone number is already in use"""
    existing = customer_crud.get_by_phone(db, phone)
    
    if existing and (not exclude_id or existing.id != exclude_id):
        return {
            "available": False,
            "message": f"Phone already registered to {existing.name}",
            "customer": {
                "id": existing.id,
                "name": existing.name
            }
        }
    
    return {"available": True}

@router.get("/search")
async def search_customers(
    q: str = Query(..., min_length=1),
    include_inactive: bool = Query(False),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quick search for duplicate check"""
    customers = customer_crud.search(
        db=db,
        query=q,
        include_inactive=include_inactive,
        limit=limit
    )
    
    return {
        "results": [
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "phone_secondary": c.phone_secondary,
                "is_active": c.is_active
            }
            for c in customers
        ]
    }
```

2. **Customer Web Routes** (`app/web/customers.py`):
```python
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.templates import templates
from app.middleware.auth import get_current_user
from app.schemas.customer import CustomerCreate
from app.crud.customer import customer_crud

router = APIRouter(prefix="/customers", tags=["customers-web"])

@router.get("/", response_class=HTMLResponse)
async def customer_list(
    request: Request,
    page: int = 1,
    search: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Customer list page"""
    per_page = 20
    skip = (page - 1) * per_page
    
    if search:
        customers = customer_crud.search(db, search, skip=skip, limit=per_page)
        total = len(customers)  # For now, simple count
    else:
        # Get paginated active customers
        customers = db.query(Customer).filter(
            Customer.is_active == True
        ).offset(skip).limit(per_page).all()
        total = customer_crud.count_active(db)
    
    total_pages = (total + per_page - 1) // per_page
    
    return templates.TemplateResponse("customers/list.html", {
        "request": request,
        "customers": customers,
        "page": page,
        "total_pages": total_pages,
        "search": search or "",
        "current_user": current_user
    })

@router.get("/new", response_class=HTMLResponse)
async def new_customer_form(
    request: Request,
    current_user = Depends(get_current_user)
):
    """Show customer registration form"""
    return templates.TemplateResponse("customers/form.html", {
        "request": request,
        "customer": None,  # New customer
        "current_user": current_user
    })

@router.post("/new")
async def create_customer_submit(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    phone_secondary: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process customer registration form"""
    try:
        # Create customer data
        customer_data = CustomerCreate(
            name=name,
            phone=phone,
            phone_secondary=phone_secondary,
            email=email,
            address=address,
            notes=notes
        )
        
        # Create customer
        customer = customer_crud.create(
            db=db,
            customer=customer_data,
            created_by_id=current_user.id
        )
        
        # Set success message
        request.session["flash_message"] = f"Customer {customer.name} registered successfully!"
        
        # Redirect to customer profile
        return RedirectResponse(
            url=f"/customers/{customer.id}",
            status_code=303
        )
        
    except ValueError as e:
        # Return form with error
        return templates.TemplateResponse("customers/form.html", {
            "request": request,
            "customer": None,
            "error": str(e),
            "form_data": {
                "name": name,
                "phone": phone,
                "phone_secondary": phone_secondary,
                "email": email,
                "address": address,
                "notes": notes
            },
            "current_user": current_user
        }, status_code=400)
```

3. **Customer Registration Form** (`templates/customers/form.html`):
```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <div class="page-header">
        <h1>{{ "Edit Customer" if customer else "Register New Customer" }}</h1>
        <a href="/customers" class="btn-secondary">
            <svg><!-- arrow-left icon --></svg>
            Back to List
        </a>
    </div>
    
    {% if error %}
    <div class="alert alert-error">
        <svg><!-- exclamation icon --></svg>
        {{ error }}
    </div>
    {% endif %}
    
    <form method="POST" 
          action="{{ '/customers/' + customer.id|string + '/edit' if customer else '/customers/new' }}"
          class="customer-form">
        
        <div class="form-section">
            <h2>Basic Information</h2>
            
            <div class="form-group">
                <label for="name" class="required">Customer Name</label>
                <input type="text" 
                       id="name" 
                       name="name" 
                       value="{{ (form_data.name if form_data else customer.name if customer else '') }}"
                       required
                       autofocus
                       class="form-control">
                <span class="form-hint">Full name of the customer</span>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="phone" class="required">Primary Phone</label>
                    <input type="tel" 
                           id="phone" 
                           name="phone" 
                           value="{{ (form_data.phone if form_data else customer.phone if customer else '') }}"
                           required
                           hx-get="/api/v1/customers/check-phone"
                           hx-trigger="keyup changed delay:500ms"
                           hx-target="#phone-check"
                           hx-params="*"
                           {% if customer %}hx-vals='{"exclude_id": {{ customer.id }}}'{% endif %}
                           class="form-control">
                    <div id="phone-check"></div>
                    <span class="form-hint">Main contact number</span>
                </div>
                
                <div class="form-group">
                    <label for="phone_secondary">Secondary Phone</label>
                    <input type="tel" 
                           id="phone_secondary" 
                           name="phone_secondary" 
                           value="{{ (form_data.phone_secondary if form_data else customer.phone_secondary if customer else '') }}"
                           placeholder="Optional"
                           class="form-control">
                    <span class="form-hint">Alternative contact</span>
                </div>
            </div>
            
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" 
                       id="email" 
                       name="email" 
                       value="{{ (form_data.email if form_data else customer.email if customer else '') }}"
                       placeholder="Optional"
                       class="form-control">
                <span class="form-hint">For electronic receipts</span>
            </div>
        </div>
        
        <div class="form-section">
            <h2>Additional Information</h2>
            
            <div class="form-group">
                <label for="address">Address</label>
                <textarea id="address" 
                          name="address" 
                          rows="3"
                          placeholder="Optional"
                          class="form-control">{{ (form_data.address if form_data else customer.address if customer else '') }}</textarea>
                <span class="form-hint">Physical address for deliveries</span>
            </div>
            
            <div class="form-group">
                <label for="notes">Notes</label>
                <textarea id="notes" 
                          name="notes" 
                          rows="3"
                          placeholder="Optional - Any special notes about this customer"
                          class="form-control">{{ (form_data.notes if form_data else customer.notes if customer else '') }}</textarea>
                <span class="form-hint">Internal notes (not visible to customer)</span>
            </div>
        </div>
        
        <div class="form-actions">
            <button type="submit" class="btn-primary">
                <svg><!-- save icon --></svg>
                {{ "Update Customer" if customer else "Register Customer" }}
            </button>
            <a href="/customers" class="btn-secondary">Cancel</a>
        </div>
    </form>
    
    <!-- Similar customers (for duplicate prevention) -->
    <div id="similar-customers" class="hidden">
        <h3>Similar Customers Found</h3>
        <div id="similar-list"></div>
    </div>
</div>

<script src="/static/js/customer-form.js"></script>
{% endblock %}
```

4. **Phone Check Partial** (`templates/customers/partials/phone_check.html`):
```html
{% if not available %}
<div class="field-error">
    <svg><!-- exclamation icon --></svg>
    {{ message }}
    {% if customer %}
    <a href="/customers/{{ customer.id }}" class="link-primary">View Customer</a>
    {% endif %}
</div>
{% else %}
<div class="field-success">
    <svg><!-- check icon --></svg>
    Phone number available
</div>
{% endif %}
```

5. **Form JavaScript** (`static/js/customer-form.js`):
```javascript
// Customer form enhancements
class CustomerForm {
    constructor() {
        this.form = document.querySelector('.customer-form');
        this.nameInput = document.getElementById('name');
        this.phoneInput = document.getElementById('phone');
        this.similarDiv = document.getElementById('similar-customers');
        
        this.init();
    }
    
    init() {
        // Auto-search for similar customers while typing name
        if (this.nameInput) {
            this.nameInput.addEventListener('input', 
                this.debounce(this.searchSimilar.bind(this), 500)
            );
        }
        
        // Format phone numbers as they type
        const phoneInputs = document.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach(input => {
            input.addEventListener('input', this.formatPhone.bind(this));
        });
        
        // Form validation
        this.form.addEventListener('submit', this.validateForm.bind(this));
    }
    
    async searchSimilar(event) {
        const query = event.target.value.trim();
        
        if (query.length < 3) {
            this.similarDiv.classList.add('hidden');
            return;
        }
        
        try {
            const response = await fetch(`/api/v1/customers/search?q=${encodeURIComponent(query)}&limit=5`);
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                this.showSimilarCustomers(data.results);
            } else {
                this.similarDiv.classList.add('hidden');
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }
    
    showSimilarCustomers(customers) {
        const listDiv = document.getElementById('similar-list');
        
        listDiv.innerHTML = customers.map(customer => `
            <div class="similar-customer-card">
                <div class="customer-info">
                    <strong>${customer.name}</strong>
                    <span class="text-muted">${customer.phone}</span>
                    ${customer.phone_secondary ? `<span class="text-muted">/ ${customer.phone_secondary}</span>` : ''}
                </div>
                <a href="/customers/${customer.id}" class="btn-small">View</a>
            </div>
        `).join('');
        
        this.similarDiv.classList.remove('hidden');
    }
    
    formatPhone(event) {
        // Basic phone formatting (can be enhanced)
        let value = event.target.value.replace(/\D/g, '');
        
        // Don't format if user is typing international format
        if (event.target.value.startsWith('+')) {
            return;
        }
        
        // Simple formatting for 10-digit numbers
        if (value.length === 10) {
            value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
            event.target.value = value;
        }
    }
    
    validateForm(event) {
        // Clear previous errors
        document.querySelectorAll('.field-error').forEach(el => el.remove());
        
        let valid = true;
        
        // Validate name
        if (!this.nameInput.value.trim()) {
            this.showFieldError(this.nameInput, 'Name is required');
            valid = false;
        }
        
        // Validate phone
        const phone = this.phoneInput.value.replace(/\D/g, '');
        if (phone.length < 7) {
            this.showFieldError(this.phoneInput, 'Please enter a valid phone number');
            valid = false;
        }
        
        // Validate email if provided
        const emailInput = document.getElementById('email');
        if (emailInput.value && !this.isValidEmail(emailInput.value)) {
            this.showFieldError(emailInput, 'Please enter a valid email address');
            valid = false;
        }
        
        if (!valid) {
            event.preventDefault();
        }
    }
    
    showFieldError(field, message) {
        const error = document.createElement('div');
        error.className = 'field-error';
        error.textContent = message;
        field.parentElement.appendChild(error);
        field.focus();
    }
    
    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new CustomerForm();
});
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Form validates all inputs correctly
- [ ] Duplicate phone check works in real-time
- [ ] Success message displays after registration
- [ ] Form is mobile-responsive
- [ ] Tab order optimized for data entry
- [ ] No console errors
- [ ] Accessibility: proper labels and ARIA

## 🧪 Testing Approach

### Manual Tests:
- Register customer with all fields
- Register with only required fields
- Try duplicate phone number
- Cancel and verify redirect
- Test on mobile device

### Integration Tests:
- Form submission with valid data
- Form submission with invalid data
- Duplicate phone prevention
- Similar customer search
- Session flash messages

### UI Tests:
- Field validation messages
- Phone formatting
- Auto-search behavior
- Success notifications

## 🔗 Dependencies
- **Depends on**: 
  - STORY-028 (Customer Model)
  - STORY-027 (Database Setup)
  - Design System
- **Blocks**: 
  - STORY-030 (Customer Search)
  - STORY-031 (Customer Profile)

## 📌 Notes
- Phone format is flexible (no strict validation)
- Similar customer search helps prevent duplicates
- Form optimized for quick data entry
- All fields except name and phone are optional
- Future: Add photo upload capability

## 📝 Dev Notes

### Key Features:

1. **Duplicate Prevention**:
   - Real-time phone check
   - Similar customer search by name
   - Clear indication of existing customers

2. **User Experience**:
   - Logical tab order
   - Clear required field indicators
   - Inline validation messages
   - Success feedback

3. **Form Design**:
   - Grouped into logical sections
   - Help text for each field
   - Mobile-friendly layout
   - Clear action buttons

### API Integration:
- `POST /api/v1/customers/` - Create customer
- `GET /api/v1/customers/check-phone` - Check phone availability
- `GET /api/v1/customers/search` - Search similar customers

### Session Messages:
```python
# Set success message
request.session["flash_message"] = "Customer registered successfully!"

# Display in template
{% if request.session.get('flash_message') %}
<div class="alert alert-success">
    {{ request.session.pop('flash_message') }}
</div>
{% endif %}
```

## 📊 Tasks / Subtasks

- [ ] **Create API Endpoints** (AC: 4, 5)
  - [ ] Create customer endpoint
  - [ ] Phone availability check
  - [ ] Search endpoint
  - [ ] Add validation

- [ ] **Build Web Routes** (AC: 1, 7, 8)
  - [ ] Customer list route
  - [ ] Registration form route
  - [ ] Form submission handler
  - [ ] Success redirect

- [ ] **Design Registration Form** (AC: 2, 3, 9)
  - [ ] Create form template
  - [ ] Mark required fields
  - [ ] Add help text
  - [ ] Optimize tab order

- [ ] **Implement Phone Check** (AC: 4)
  - [ ] HTMX integration
  - [ ] Check endpoint
  - [ ] Display results
  - [ ] Handle errors

- [ ] **Add Form Validation** (AC: 5, 10)
  - [ ] Client-side validation
  - [ ] Server-side validation
  - [ ] Error messages
  - [ ] Field formatting

- [ ] **Create Success Flow** (AC: 6, 7)
  - [ ] Flash message system
  - [ ] Success notification
  - [ ] Redirect to profile
  - [ ] Clear form data

- [ ] **Build Similar Search** (AC: 4)
  - [ ] Auto-search on name
  - [ ] Display similar customers
  - [ ] Link to existing profiles
  - [ ] Hide when not relevant

- [ ] **Style Components** (DoD)
  - [ ] Apply design system
  - [ ] Mobile responsive
  - [ ] Loading states
  - [ ] Error states

- [ ] **Add Tests** (DoD)
  - [ ] API endpoint tests
  - [ ] Form submission tests
  - [ ] Validation tests
  - [ ] UI interaction tests

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