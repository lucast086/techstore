# STORY-031: Customer Profile

## 📋 Story Details
- **Epic**: EPIC-002 (Customer Management)
- **Priority**: HIGH
- **Estimate**: 1.5 days
- **Status**: TODO

## 🎯 User Story
**As** María or Carlos,  
**I want** to view and edit customer profiles,  
**So that** I can keep customer information up to date and see their complete history with our business

## ✅ Acceptance Criteria
1. [ ] Profile page shows all customer information clearly
2. [ ] Edit button visible for users with permission
3. [ ] Transaction history tab shows all sales and payments
4. [ ] Repair history tab shows all repair orders
5. [ ] Current balance prominently displayed with color coding
6. [ ] Contact section with WhatsApp quick action
7. [ ] Notes section for internal comments
8. [ ] Activity timeline shows recent interactions
9. [ ] Edit form pre-fills with current data
10. [ ] Success message after successful update
11. [ ] Soft delete option (deactivate) with confirmation
12. [ ] Cannot delete customer with non-zero balance

## 🔧 Technical Details

### Files to Create/Update:
```
src/app/
├── web/
│   └── customers.py         # Add profile routes
├── templates/
│   └── customers/
│       ├── profile.html     # Customer profile page
│       ├── edit.html        # Edit form (reuse form.html)
│       └── partials/
│           ├── contact_info.html
│           ├── transaction_history.html
│           ├── repair_history.html
│           └── activity_timeline.html
└── static/
    └── js/
        └── customer-profile.js  # Profile interactions
```

### Implementation Requirements:

1. **Profile Routes** (Update `app/web/customers.py`):
```python
@router.get("/{customer_id}", response_class=HTMLResponse)
async def customer_profile(
    customer_id: int,
    request: Request,
    tab: str = Query("overview", regex="^(overview|transactions|repairs|activity)$"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Customer profile page"""
    customer = customer_crud.get(db, customer_id)
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Calculate current balance (TODO: implement actual calculation)
    balance = Decimal("0.00")
    
    # Get recent transactions (TODO: implement when transaction model exists)
    transactions = []
    
    # Get repair history (TODO: implement when repair model exists)
    repairs = []
    
    # Get activity timeline
    activities = get_customer_activities(db, customer_id, limit=10)
    
    return templates.TemplateResponse("customers/profile.html", {
        "request": request,
        "customer": customer,
        "balance": balance,
        "transactions": transactions,
        "repairs": repairs,
        "activities": activities,
        "active_tab": tab,
        "current_user": current_user,
        "can_edit": has_permission(current_user, "customers.update"),
        "can_delete": has_permission(current_user, "customers.delete")
    })

@router.get("/{customer_id}/edit", response_class=HTMLResponse)
async def edit_customer_form(
    customer_id: int,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Show edit form"""
    if not has_permission(current_user, "customers.update"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    customer = customer_crud.get(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return templates.TemplateResponse("customers/form.html", {
        "request": request,
        "customer": customer,
        "current_user": current_user
    })

@router.post("/{customer_id}/edit")
async def update_customer(
    customer_id: int,
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
    """Update customer information"""
    if not has_permission(current_user, "customers.update"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        update_data = CustomerUpdate(
            name=name,
            phone=phone,
            phone_secondary=phone_secondary,
            email=email,
            address=address,
            notes=notes
        )
        
        customer = customer_crud.update(db, customer_id, update_data)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Log activity
        log_customer_activity(db, customer_id, "updated", current_user.id)
        
        request.session["flash_message"] = "Customer updated successfully!"
        
        return RedirectResponse(
            url=f"/customers/{customer_id}",
            status_code=303
        )
        
    except ValueError as e:
        # Return form with error
        customer = customer_crud.get(db, customer_id)
        return templates.TemplateResponse("customers/form.html", {
            "request": request,
            "customer": customer,
            "error": str(e),
            "current_user": current_user
        }, status_code=400)

@router.post("/{customer_id}/deactivate")
async def deactivate_customer(
    customer_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete (deactivate) customer"""
    if not has_permission(current_user, "customers.delete"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    customer = customer_crud.get(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check balance
    balance = calculate_customer_balance(db, customer_id)
    if balance != 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot deactivate customer with non-zero balance (${balance})"
        )
    
    success = customer_crud.soft_delete(db, customer_id)
    if success:
        log_customer_activity(db, customer_id, "deactivated", current_user.id)
        return {"success": True, "message": "Customer deactivated"}
    
    raise HTTPException(status_code=500, detail="Failed to deactivate customer")

def get_customer_activities(db: Session, customer_id: int, limit: int = 10):
    """Get recent activities for customer"""
    # TODO: Implement when we have sales, payments, repairs
    # For now, return mock data structure
    return [
        {
            "type": "registration",
            "description": "Customer registered",
            "timestamp": customer.created_at,
            "user": customer.created_by.full_name if customer.created_by else "System"
        }
    ]

def log_customer_activity(db: Session, customer_id: int, action: str, user_id: int):
    """Log customer-related activities"""
    # TODO: Implement activity logging
    pass
```

2. **Customer Profile Template** (`templates/customers/profile.html`):
```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <!-- Header -->
    <div class="profile-header">
        <div class="profile-title">
            <a href="/customers" class="back-link">
                <svg><!-- arrow-left --></svg>
                Customers
            </a>
            <h1>{{ customer.name }}</h1>
            {% if not customer.is_active %}
            <span class="badge badge-inactive">Inactive</span>
            {% endif %}
        </div>
        
        <div class="profile-actions">
            {% if can_edit %}
            <a href="/customers/{{ customer.id }}/edit" class="btn-secondary">
                <svg><!-- pencil icon --></svg>
                Edit
            </a>
            {% endif %}
            
            {% if can_delete and customer.is_active %}
            <button class="btn-danger" 
                    onclick="confirmDeactivate({{ customer.id }})">
                <svg><!-- trash icon --></svg>
                Deactivate
            </button>
            {% endif %}
        </div>
    </div>
    
    <!-- Balance Card -->
    <div class="balance-card {{ 'negative' if balance < 0 else 'positive' if balance > 0 else 'neutral' }}">
        <div class="balance-label">Current Balance</div>
        <div class="balance-amount">
            {% if balance < 0 %}
                <span class="balance-indicator">Customer Owes</span>
                ${{ "{:,.2f}".format(abs(balance)) }}
            {% elif balance > 0 %}
                <span class="balance-indicator">Customer Has Credit</span>
                ${{ "{:,.2f}".format(balance) }}
            {% else %}
                $0.00
            {% endif %}
        </div>
        {% if balance < 0 %}
        <div class="balance-actions">
            <button class="btn-primary btn-small">Record Payment</button>
            <a href="https://wa.me/{{ customer.phone }}?text=Hello {{ customer.name }}, your current balance is ${{ abs(balance) }}" 
               class="btn-secondary btn-small"
               target="_blank">
                <svg><!-- whatsapp icon --></svg>
                Send Reminder
            </a>
        </div>
        {% endif %}
    </div>
    
    <!-- Profile Content -->
    <div class="profile-content">
        <div class="profile-sidebar">
            <!-- Contact Information -->
            <div class="info-card">
                <h3>Contact Information</h3>
                {% include "customers/partials/contact_info.html" %}
            </div>
            
            <!-- Notes -->
            <div class="info-card">
                <h3>Notes</h3>
                {% if customer.notes %}
                <p class="notes-content">{{ customer.notes }}</p>
                {% else %}
                <p class="text-muted">No notes added</p>
                {% endif %}
            </div>
            
            <!-- Metadata -->
            <div class="info-card">
                <h3>Customer Details</h3>
                <dl class="detail-list">
                    <dt>Customer Since</dt>
                    <dd>{{ customer.created_at.strftime('%B %d, %Y') }}</dd>
                    
                    <dt>Registered By</dt>
                    <dd>{{ customer.created_by.full_name if customer.created_by else 'System' }}</dd>
                    
                    <dt>Last Updated</dt>
                    <dd>{{ customer.updated_at.strftime('%B %d, %Y at %I:%M %p') }}</dd>
                </dl>
            </div>
        </div>
        
        <div class="profile-main">
            <!-- Tabs -->
            <div class="tabs">
                <a href="?tab=overview" 
                   class="tab {{ 'active' if active_tab == 'overview' else '' }}">
                    Overview
                </a>
                <a href="?tab=transactions" 
                   class="tab {{ 'active' if active_tab == 'transactions' else '' }}">
                    Transactions
                    {% if transactions %}
                    <span class="tab-count">{{ transactions|length }}</span>
                    {% endif %}
                </a>
                <a href="?tab=repairs" 
                   class="tab {{ 'active' if active_tab == 'repairs' else '' }}">
                    Repairs
                    {% if repairs %}
                    <span class="tab-count">{{ repairs|length }}</span>
                    {% endif %}
                </a>
                <a href="?tab=activity" 
                   class="tab {{ 'active' if active_tab == 'activity' else '' }}">
                    Activity
                </a>
            </div>
            
            <!-- Tab Content -->
            <div class="tab-content">
                {% if active_tab == 'overview' %}
                <div class="overview-tab">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">${{ "{:,.2f}".format(0) }}</div>
                            <div class="stat-label">Total Purchases</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">0</div>
                            <div class="stat-label">Total Repairs</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{ "{:,.2f}".format(0) }}</div>
                            <div class="stat-label">Average Purchase</div>
                        </div>
                    </div>
                    
                    <!-- Recent Activity -->
                    <h3>Recent Activity</h3>
                    {% include "customers/partials/activity_timeline.html" %}
                </div>
                
                {% elif active_tab == 'transactions' %}
                    {% include "customers/partials/transaction_history.html" %}
                
                {% elif active_tab == 'repairs' %}
                    {% include "customers/partials/repair_history.html" %}
                
                {% elif active_tab == 'activity' %}
                    <h3>All Activity</h3>
                    {% include "customers/partials/activity_timeline.html" %}
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Deactivate Confirmation Modal -->
<div id="deactivate-modal" class="modal hidden">
    <div class="modal-content">
        <h3>Deactivate Customer</h3>
        <p>Are you sure you want to deactivate {{ customer.name }}?</p>
        <p class="text-warning">This will hide the customer from searches and prevent new transactions.</p>
        
        <div class="modal-actions">
            <button onclick="closeModal()" class="btn-secondary">Cancel</button>
            <button onclick="deactivateCustomer({{ customer.id }})" class="btn-danger">
                Deactivate Customer
            </button>
        </div>
    </div>
</div>

<script src="/static/js/customer-profile.js"></script>
{% endblock %}
```

3. **Contact Info Partial** (`templates/customers/partials/contact_info.html`):
```html
<div class="contact-info">
    <div class="contact-item">
        <label>Primary Phone</label>
        <div class="contact-value">
            <span>{{ customer.phone }}</span>
            <a href="https://wa.me/{{ customer.phone }}" 
               class="contact-action"
               target="_blank"
               title="Open WhatsApp">
                <svg><!-- whatsapp icon --></svg>
            </a>
        </div>
    </div>
    
    {% if customer.phone_secondary %}
    <div class="contact-item">
        <label>Secondary Phone</label>
        <div class="contact-value">
            <span>{{ customer.phone_secondary }}</span>
            <a href="https://wa.me/{{ customer.phone_secondary }}" 
               class="contact-action"
               target="_blank"
               title="Open WhatsApp">
                <svg><!-- whatsapp icon --></svg>
            </a>
        </div>
    </div>
    {% endif %}
    
    {% if customer.email %}
    <div class="contact-item">
        <label>Email</label>
        <div class="contact-value">
            <span>{{ customer.email }}</span>
            <a href="mailto:{{ customer.email }}" 
               class="contact-action"
               title="Send Email">
                <svg><!-- mail icon --></svg>
            </a>
        </div>
    </div>
    {% endif %}
    
    {% if customer.address %}
    <div class="contact-item">
        <label>Address</label>
        <div class="contact-value">
            <address>{{ customer.address }}</address>
        </div>
    </div>
    {% endif %}
    
    <div class="quick-actions">
        <a href="/sales/new?customer_id={{ customer.id }}" class="quick-action">
            <svg><!-- shopping-cart icon --></svg>
            New Sale
        </a>
        <a href="/repairs/new?customer_id={{ customer.id }}" class="quick-action">
            <svg><!-- wrench icon --></svg>
            New Repair
        </a>
    </div>
</div>
```

4. **Transaction History Partial** (`templates/customers/partials/transaction_history.html`):
```html
<div class="transaction-history">
    {% if transactions %}
    <div class="table-responsive">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Balance</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for transaction in transactions %}
                <tr>
                    <td>{{ transaction.date.strftime('%m/%d/%Y') }}</td>
                    <td>
                        <span class="transaction-type {{ transaction.type }}">
                            {{ transaction.type|title }}
                        </span>
                    </td>
                    <td>{{ transaction.description }}</td>
                    <td class="{{ 'debit' if transaction.amount < 0 else 'credit' }}">
                        ${{ "{:,.2f}".format(abs(transaction.amount)) }}
                    </td>
                    <td>${{ "{:,.2f}".format(transaction.running_balance) }}</td>
                    <td>
                        <a href="{{ transaction.link }}" class="btn-icon">
                            <svg><!-- eye icon --></svg>
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="empty-state">
        <svg class="empty-icon"><!-- receipt icon --></svg>
        <h4>No transactions yet</h4>
        <p>Transactions will appear here once the customer makes purchases or payments</p>
        <a href="/sales/new?customer_id={{ customer.id }}" class="btn-primary">
            Create First Sale
        </a>
    </div>
    {% endif %}
</div>
```

5. **Profile JavaScript** (`static/js/customer-profile.js`):
```javascript
// Customer profile interactions
function confirmDeactivate(customerId) {
    document.getElementById('deactivate-modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('deactivate-modal').classList.add('hidden');
}

async function deactivateCustomer(customerId) {
    try {
        const response = await fetch(`/customers/${customerId}/deactivate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show success message
            showNotification('Customer deactivated successfully', 'success');
            
            // Redirect to customer list
            setTimeout(() => {
                window.location.href = '/customers';
            }, 1500);
        } else {
            showNotification(data.detail || 'Failed to deactivate customer', 'error');
            closeModal();
        }
    } catch (error) {
        console.error('Deactivation error:', error);
        showNotification('An error occurred', 'error');
        closeModal();
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Tab persistence
document.addEventListener('DOMContentLoaded', () => {
    // Preserve tab selection on page reload
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            // Let the link work but store the tab
            const url = new URL(tab.href);
            const tabName = url.searchParams.get('tab');
            if (tabName) {
                localStorage.setItem('customerProfileTab', tabName);
            }
        });
    });
});

// Initialize tooltips
tippy('[title]', {
    placement: 'top',
    animation: 'fade',
});
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Profile loads in < 500ms
- [ ] All tabs functional
- [ ] Edit form works correctly
- [ ] Deactivation with balance check
- [ ] WhatsApp integration working
- [ ] Mobile responsive design
- [ ] No console errors

## 🧪 Testing Approach

### Manual Tests:
- View customer with all fields
- View customer with minimal fields
- Edit customer information
- Try to deactivate with balance
- Navigate all tabs
- Test WhatsApp links

### Integration Tests:
- Profile data loading
- Edit form submission
- Deactivation process
- Permission checks
- Activity logging

### UI Tests:
- Tab navigation
- Modal interactions
- Form validation
- Responsive layout
- Quick actions

## 🔗 Dependencies
- **Depends on**: 
  - STORY-028 (Customer Model)
  - STORY-029 (Customer Registration)
  - STORY-030 (Customer Search)
- **Blocks**: 
  - Sales features (need customer profile)
  - Repair features (need customer profile)

## 📌 Notes
- Transaction/repair history will be implemented with those features
- Balance calculation placeholder for now
- Activity timeline will grow with more features
- Consider adding customer photo in future
- Export customer data feature for GDPR

## 📝 Dev Notes

### Profile Layout:
1. **Header**: Name, status, actions
2. **Balance Card**: Prominent balance display
3. **Sidebar**: Contact info, notes, metadata
4. **Main Area**: Tabbed content

### Tab Structure:
- **Overview**: Summary stats and recent activity
- **Transactions**: Full transaction history
- **Repairs**: Repair order history
- **Activity**: Complete activity timeline

### Future Integrations:
```python
# When transaction model exists
def calculate_customer_balance(db: Session, customer_id: int) -> Decimal:
    # Implementation here
    pass

# When activity logging exists
def get_customer_activities(db: Session, customer_id: int):
    # Implementation here
    pass
```

### Permission Checks:
- View: Any authenticated user
- Edit: customers.update permission
- Delete: customers.delete permission

## 📊 Tasks / Subtasks

- [ ] **Create Profile Route** (AC: 1, 5, 8)
  - [ ] Implement profile view
  - [ ] Calculate balance
  - [ ] Get activity data
  - [ ] Handle tabs

- [ ] **Build Profile Template** (AC: 1, 2, 5, 6, 7)
  - [ ] Create layout structure
  - [ ] Add balance card
  - [ ] Design contact section
  - [ ] Include notes area

- [ ] **Implement Edit Flow** (AC: 2, 9, 10)
  - [ ] Add edit route
  - [ ] Reuse form template
  - [ ] Handle updates
  - [ ] Show success message

- [ ] **Create Tab System** (AC: 3, 4, 8)
  - [ ] Build tab navigation
  - [ ] Create tab content areas
  - [ ] Handle tab switching
  - [ ] Preserve tab state

- [ ] **Add Deactivation** (AC: 11, 12)
  - [ ] Create deactivate endpoint
  - [ ] Check balance before delete
  - [ ] Add confirmation modal
  - [ ] Log deactivation

- [ ] **Build Partials** (AC: 3, 4, 6)
  - [ ] Contact info partial
  - [ ] Transaction history
  - [ ] Repair history
  - [ ] Activity timeline

- [ ] **Add WhatsApp Actions** (AC: 6)
  - [ ] Phone number links
  - [ ] Balance reminder button
  - [ ] Quick message templates
  - [ ] Test on mobile

- [ ] **Style Profile Page** (DoD)
  - [ ] Apply design system
  - [ ] Mobile responsive
  - [ ] Loading states
  - [ ] Empty states

- [ ] **Add Tests** (DoD)
  - [ ] Profile view tests
  - [ ] Edit functionality
  - [ ] Permission tests
  - [ ] Balance validation

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