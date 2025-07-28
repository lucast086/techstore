# STORY-030: Customer Search

## 📋 Story Details
- **Epic**: EPIC-002 (Customer Management)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** María or Carlos,  
**I want** to search for customers by name or phone numbers,  
**So that** I can quickly find customer information during sales or service

## ✅ Acceptance Criteria
1. [ ] Search bar prominently displayed on customer list page
2. [ ] Real-time search as user types (300ms debounce)
3. [ ] Search matches partial name, primary phone, or secondary phone
4. [ ] Results show: name, both phones, calculated balance
5. [ ] Click on result navigates to customer profile
6. [ ] "No customers found" message when no matches
7. [ ] Search results update without page refresh (HTMX)
8. [ ] Show only active customers by default
9. [ ] Toggle to include inactive customers in results
10. [ ] Clear search button to reset results
11. [ ] Search persists in URL for bookmarking/sharing
12. [ ] Results show customer debt with visual indicator

## 🔧 Technical Details

### Files to Update/Create:
```
src/app/
├── api/v1/
│   └── customers.py         # Add search endpoint
├── web/
│   └── customers.py         # Update list route
├── templates/
│   └── customers/
│       ├── list.html        # Add search UI
│       └── partials/
│           ├── customer_list.html    # Results partial
│           └── customer_row.html     # Individual row
└── static/
    ├── js/
    │   └── customer-search.js    # Search interactions
    └── css/
        └── customers.css         # Search styling
```

### Implementation Requirements:

1. **Enhanced Search API** (Update `app/api/v1/customers.py`):
```python
from typing import List, Optional
from decimal import Decimal

@router.get("/", response_model=CustomerList)
async def list_customers(
    search: Optional[str] = Query(None),
    include_inactive: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List customers with search and pagination"""
    skip = (page - 1) * per_page
    
    # Base query
    query = db.query(Customer)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.name.ilike(search_term),
                Customer.phone.like(search_term),
                Customer.phone_secondary.like(search_term)
            )
        )
    
    # Active filter
    if not include_inactive:
        query = query.filter(Customer.is_active == True)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    customers = query.order_by(Customer.name).offset(skip).limit(per_page).all()
    
    # Calculate balances for each customer
    customer_responses = []
    for customer in customers:
        # TODO: Calculate actual balance from transactions
        # For now, return 0 or mock data
        balance = Decimal("0.00")
        transaction_count = 0
        
        customer_responses.append(
            CustomerResponse(
                **customer.to_dict(),
                created_by_name=customer.created_by.full_name if customer.created_by else None,
                balance=float(balance),
                transaction_count=transaction_count
            )
        )
    
    return CustomerList(
        customers=customer_responses,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/quick-search")
async def quick_search(
    q: str = Query(..., min_length=1),
    include_inactive: bool = Query(False),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quick search for autocomplete"""
    customers = customer_crud.search(
        db=db,
        query=q,
        include_inactive=include_inactive,
        limit=limit
    )
    
    # Return simplified data for quick display
    return {
        "results": [
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "phone_secondary": c.phone_secondary,
                "balance": 0.0,  # TODO: Calculate actual balance
                "is_active": c.is_active,
                "display": f"{c.name} - {c.phone}"
            }
            for c in customers
        ],
        "count": len(customers)
    }
```

2. **Updated Customer List Template** (`templates/customers/list.html`):
```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <div class="page-header">
        <h1>Customers</h1>
        <a href="/customers/new" class="btn-primary">
            <svg><!-- user-plus icon --></svg>
            Register New Customer
        </a>
    </div>
    
    <!-- Search Section -->
    <div class="search-section">
        <div class="search-container">
            <div class="search-input-wrapper">
                <svg class="search-icon"><!-- magnifying-glass icon --></svg>
                <input type="search" 
                       id="customer-search"
                       name="search"
                       placeholder="Search by name or phone number..."
                       value="{{ search }}"
                       class="search-input"
                       autocomplete="off"
                       hx-get="/customers"
                       hx-trigger="keyup changed delay:300ms, search"
                       hx-target="#customer-results"
                       hx-push-url="true"
                       hx-indicator="#search-spinner">
                
                {% if search %}
                <button type="button" 
                        class="clear-search"
                        onclick="clearSearch()">
                    <svg><!-- x icon --></svg>
                </button>
                {% endif %}
                
                <div id="search-spinner" class="htmx-indicator">
                    <div class="spinner-small"></div>
                </div>
            </div>
            
            <div class="search-options">
                <label class="checkbox-label">
                    <input type="checkbox" 
                           id="include-inactive"
                           name="include_inactive"
                           hx-get="/customers"
                           hx-trigger="change"
                           hx-target="#customer-results"
                           hx-include="#customer-search">
                    <span>Include inactive customers</span>
                </label>
            </div>
        </div>
        
        <!-- Quick search results dropdown -->
        <div id="quick-search-results" class="quick-results hidden"></div>
    </div>
    
    <!-- Results Section -->
    <div id="customer-results">
        {% include "customers/partials/customer_list.html" %}
    </div>
</div>

<script src="/static/js/customer-search.js"></script>
{% endblock %}
```

3. **Customer List Partial** (`templates/customers/partials/customer_list.html`):
```html
<div class="customer-list">
    {% if search %}
    <div class="search-summary">
        <span>Found {{ total }} customer{{ 's' if total != 1 else '' }} for "{{ search }}"</span>
    </div>
    {% endif %}
    
    {% if customers %}
    <div class="table-responsive">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Phone Numbers</th>
                    <th>Balance</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for customer in customers %}
                {% include "customers/partials/customer_row.html" %}
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <!-- Pagination -->
    {% if total_pages > 1 %}
    <div class="pagination">
        {% if page > 1 %}
        <a href="?page={{ page - 1 }}&search={{ search }}" 
           hx-get="/customers?page={{ page - 1 }}&search={{ search }}"
           hx-target="#customer-results"
           class="page-link">Previous</a>
        {% endif %}
        
        <span class="page-info">Page {{ page }} of {{ total_pages }}</span>
        
        {% if page < total_pages %}
        <a href="?page={{ page + 1 }}&search={{ search }}"
           hx-get="/customers?page={{ page + 1 }}&search={{ search }}"
           hx-target="#customer-results"
           class="page-link">Next</a>
        {% endif %}
    </div>
    {% endif %}
    
    {% else %}
    <div class="empty-state">
        <svg class="empty-icon"><!-- users icon --></svg>
        {% if search %}
        <h3>No customers found</h3>
        <p>No customers match your search "{{ search }}"</p>
        <button onclick="clearSearch()" class="btn-secondary">Clear Search</button>
        {% else %}
        <h3>No customers yet</h3>
        <p>Start by registering your first customer</p>
        <a href="/customers/new" class="btn-primary">Register Customer</a>
        {% endif %}
    </div>
    {% endif %}
</div>
```

4. **Customer Row Partial** (`templates/customers/partials/customer_row.html`):
```html
<tr class="customer-row {{ 'inactive' if not customer.is_active else '' }}"
    onclick="window.location.href='/customers/{{ customer.id }}'">
    <td>
        <div class="customer-name">
            {{ customer.name }}
            {% if not customer.is_active %}
            <span class="badge badge-inactive">Inactive</span>
            {% endif %}
        </div>
    </td>
    <td>
        <div class="phone-numbers">
            <span class="phone-primary">{{ customer.phone }}</span>
            {% if customer.phone_secondary %}
            <span class="phone-secondary">/ {{ customer.phone_secondary }}</span>
            {% endif %}
        </div>
    </td>
    <td>
        <div class="balance {{ 'negative' if customer.balance < 0 else 'positive' if customer.balance > 0 else 'zero' }}">
            {% if customer.balance < 0 %}
                <span class="debt-indicator">Owes</span>
                ${{ "{:,.2f}".format(abs(customer.balance)) }}
            {% elif customer.balance > 0 %}
                <span class="credit-indicator">Credit</span>
                ${{ "{:,.2f}".format(customer.balance) }}
            {% else %}
                $0.00
            {% endif %}
        </div>
    </td>
    <td>
        <span class="status-indicator {{ 'active' if customer.is_active else 'inactive' }}"></span>
    </td>
    <td class="actions" onclick="event.stopPropagation()">
        <div class="action-buttons">
            <a href="/customers/{{ customer.id }}" class="btn-icon" title="View">
                <svg><!-- eye icon --></svg>
            </a>
            <a href="/customers/{{ customer.id }}/edit" class="btn-icon" title="Edit">
                <svg><!-- pencil icon --></svg>
            </a>
            {% if customer.balance < 0 %}
            <a href="https://wa.me/{{ customer.phone }}?text=Hello {{ customer.name }}, your current balance is ${{ abs(customer.balance) }}" 
               class="btn-icon" 
               title="Send WhatsApp reminder"
               target="_blank">
                <svg><!-- whatsapp icon --></svg>
            </a>
            {% endif %}
        </div>
    </td>
</tr>
```

5. **Search JavaScript** (`static/js/customer-search.js`):
```javascript
class CustomerSearch {
    constructor() {
        this.searchInput = document.getElementById('customer-search');
        this.quickResults = document.getElementById('quick-search-results');
        this.includeInactive = document.getElementById('include-inactive');
        
        this.init();
    }
    
    init() {
        if (this.searchInput) {
            // Quick search for autocomplete
            this.searchInput.addEventListener('input', 
                this.debounce(this.performQuickSearch.bind(this), 200)
            );
            
            // Hide quick results on blur
            this.searchInput.addEventListener('blur', () => {
                setTimeout(() => this.hideQuickResults(), 200);
            });
            
            // Show quick results on focus if has value
            this.searchInput.addEventListener('focus', () => {
                if (this.searchInput.value.trim()) {
                    this.performQuickSearch();
                }
            });
        }
        
        // Handle keyboard navigation in quick results
        document.addEventListener('keydown', this.handleKeyboard.bind(this));
    }
    
    async performQuickSearch() {
        const query = this.searchInput.value.trim();
        
        if (query.length < 2) {
            this.hideQuickResults();
            return;
        }
        
        try {
            const includeInactive = this.includeInactive?.checked || false;
            const response = await fetch(
                `/api/v1/customers/quick-search?q=${encodeURIComponent(query)}&include_inactive=${includeInactive}`
            );
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                this.showQuickResults(data.results);
            } else {
                this.showNoResults();
            }
        } catch (error) {
            console.error('Quick search error:', error);
            this.hideQuickResults();
        }
    }
    
    showQuickResults(results) {
        const html = results.map((customer, index) => `
            <div class="quick-result-item ${!customer.is_active ? 'inactive' : ''}" 
                 data-index="${index}"
                 data-customer-id="${customer.id}"
                 onclick="window.location.href='/customers/${customer.id}'">
                <div class="result-info">
                    <div class="result-name">
                        ${customer.name}
                        ${!customer.is_active ? '<span class="badge-small">Inactive</span>' : ''}
                    </div>
                    <div class="result-phones">
                        ${customer.phone}
                        ${customer.phone_secondary ? ` / ${customer.phone_secondary}` : ''}
                    </div>
                </div>
                ${customer.balance !== 0 ? `
                <div class="result-balance ${customer.balance < 0 ? 'negative' : 'positive'}">
                    ${customer.balance < 0 ? 'Owes' : 'Credit'} 
                    $${Math.abs(customer.balance).toFixed(2)}
                </div>
                ` : ''}
            </div>
        `).join('');
        
        this.quickResults.innerHTML = html;
        this.quickResults.classList.remove('hidden');
    }
    
    showNoResults() {
        this.quickResults.innerHTML = `
            <div class="quick-result-empty">
                No customers found
            </div>
        `;
        this.quickResults.classList.remove('hidden');
    }
    
    hideQuickResults() {
        this.quickResults.classList.add('hidden');
    }
    
    handleKeyboard(event) {
        if (!this.quickResults.classList.contains('hidden')) {
            const items = this.quickResults.querySelectorAll('.quick-result-item');
            const current = this.quickResults.querySelector('.quick-result-item.selected');
            let index = current ? parseInt(current.dataset.index) : -1;
            
            switch(event.key) {
                case 'ArrowDown':
                    event.preventDefault();
                    index = Math.min(index + 1, items.length - 1);
                    this.selectQuickResult(index);
                    break;
                    
                case 'ArrowUp':
                    event.preventDefault();
                    index = Math.max(index - 1, -1);
                    this.selectQuickResult(index);
                    break;
                    
                case 'Enter':
                    if (current) {
                        event.preventDefault();
                        window.location.href = `/customers/${current.dataset.customerId}`;
                    }
                    break;
                    
                case 'Escape':
                    this.hideQuickResults();
                    this.searchInput.blur();
                    break;
            }
        }
    }
    
    selectQuickResult(index) {
        const items = this.quickResults.querySelectorAll('.quick-result-item');
        items.forEach(item => item.classList.remove('selected'));
        
        if (index >= 0 && index < items.length) {
            items[index].classList.add('selected');
        }
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

// Global function for clear button
function clearSearch() {
    const searchInput = document.getElementById('customer-search');
    searchInput.value = '';
    searchInput.dispatchEvent(new Event('keyup', { bubbles: true }));
    searchInput.focus();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new CustomerSearch();
});

// Reinitialize after HTMX swaps
document.body.addEventListener('htmx:afterSwap', (event) => {
    if (event.detail.target.id === 'customer-results') {
        new CustomerSearch();
    }
});
```

6. **Search Styles** (`static/css/customers.css`):
```css
/* Search Section */
.search-section {
    margin-bottom: var(--space-6);
    position: relative;
}

.search-container {
    background: var(--color-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    padding: var(--space-4);
}

.search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.search-icon {
    position: absolute;
    left: var(--space-3);
    width: 20px;
    height: 20px;
    color: var(--color-gray-400);
}

.search-input {
    width: 100%;
    padding-left: var(--space-10);
    padding-right: var(--space-10);
    font-size: var(--text-lg);
}

.clear-search {
    position: absolute;
    right: var(--space-3);
    padding: var(--space-1);
    color: var(--color-gray-500);
}

.clear-search:hover {
    color: var(--color-gray-700);
}

/* Quick Results */
.quick-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin-top: var(--space-2);
    background: var(--color-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    max-height: 400px;
    overflow-y: auto;
    z-index: 100;
}

.quick-result-item {
    padding: var(--space-3) var(--space-4);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--color-gray-100);
}

.quick-result-item:hover,
.quick-result-item.selected {
    background: var(--color-gray-50);
}

.quick-result-item.inactive {
    opacity: 0.6;
}

.result-name {
    font-weight: 500;
    color: var(--color-gray-900);
}

.result-phones {
    font-size: var(--text-sm);
    color: var(--color-gray-600);
}

.result-balance {
    font-weight: 500;
    font-size: var(--text-sm);
}

.result-balance.negative {
    color: var(--color-red-600);
}

.result-balance.positive {
    color: var(--color-green-600);
}

/* Customer List */
.customer-row {
    cursor: pointer;
    transition: background-color 0.15s;
}

.customer-row:hover {
    background-color: var(--color-gray-50);
}

.customer-row.inactive {
    opacity: 0.6;
}

.balance {
    font-weight: 500;
}

.balance.negative {
    color: var(--color-red-600);
}

.balance.positive {
    color: var(--color-green-600);
}

.debt-indicator,
.credit-indicator {
    font-size: var(--text-xs);
    text-transform: uppercase;
    margin-right: var(--space-1);
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: var(--space-12);
}

.empty-icon {
    width: 64px;
    height: 64px;
    color: var(--color-gray-300);
    margin-bottom: var(--space-4);
}
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Search results update in < 300ms
- [ ] Quick search dropdown works smoothly
- [ ] URL updates with search params
- [ ] Mobile-responsive search interface
- [ ] Keyboard navigation in quick results
- [ ] No duplicate queries fired
- [ ] Accessibility compliant

## 🧪 Testing Approach

### Manual Tests:
- Search by full name
- Search by partial name
- Search by phone numbers
- Toggle inactive customers
- Clear search
- Navigate with keyboard

### Performance Tests:
- Search response time
- Debounce effectiveness
- Large result sets
- Concurrent searches

### Integration Tests:
- Search API endpoint
- Pagination with search
- Quick search results
- URL parameter handling

### UI Tests:
- Mobile search experience
- Keyboard navigation
- Empty states
- Loading indicators

## 🔗 Dependencies
- **Depends on**: 
  - STORY-028 (Customer Model)
  - STORY-029 (Customer Registration)
- **Blocks**: 
  - STORY-031 (Customer Profile)
  - Sales/Repair features (need to find customers)

## 📌 Notes
- Balance calculation will be implemented with transactions
- Quick search improves UX for point-of-sale
- WhatsApp integration for debt reminders
- Consider fuzzy search in future
- Search history could be added

## 📝 Dev Notes

### Search Strategy:
1. **Two search modes**:
   - Quick search: Dropdown with instant results
   - Full search: Updates main list with pagination

2. **Performance optimizations**:
   - 300ms debounce for main search
   - 200ms debounce for quick search
   - Indexes on search fields
   - Limited quick search results

3. **User Experience**:
   - Search persists in URL
   - Clear visual feedback
   - Keyboard navigation
   - Mobile-optimized

### Balance Calculation (TODO):
```python
# Future implementation
def calculate_customer_balance(customer_id: int, db: Session) -> Decimal:
    # Sum all sales (negative)
    sales_total = db.query(func.sum(Sale.total)).filter(
        Sale.customer_id == customer_id,
        Sale.payment_method == "credit"
    ).scalar() or Decimal("0")
    
    # Sum all payments (positive)
    payments_total = db.query(func.sum(Payment.amount)).filter(
        Payment.customer_id == customer_id
    ).scalar() or Decimal("0")
    
    return payments_total - sales_total
```

## 📊 Tasks / Subtasks

- [ ] **Update API Endpoints** (AC: 3, 4, 8, 9)
  - [ ] Enhance list endpoint with search
  - [ ] Add quick-search endpoint
  - [ ] Include balance calculation
  - [ ] Add inactive filter

- [ ] **Create Search UI** (AC: 1, 2, 10)
  - [ ] Add search input to list page
  - [ ] Style search container
  - [ ] Add clear button
  - [ ] Include inactive toggle

- [ ] **Implement Quick Search** (AC: 2, 5)
  - [ ] Create dropdown component
  - [ ] Add keyboard navigation
  - [ ] Handle result selection
  - [ ] Style quick results

- [ ] **Update Customer List** (AC: 4, 6, 12)
  - [ ] Show balance in list
  - [ ] Add debt indicators
  - [ ] Update row styling
  - [ ] Add WhatsApp action

- [ ] **Add HTMX Integration** (AC: 7, 11)
  - [ ] Configure search triggers
  - [ ] Update URL on search
  - [ ] Handle loading states
  - [ ] Preserve search on navigation

- [ ] **Handle Empty States** (AC: 6)
  - [ ] No results message
  - [ ] Clear search option
  - [ ] Helpful suggestions
  - [ ] Register CTA

- [ ] **Optimize Performance** (DoD)
  - [ ] Add debouncing
  - [ ] Prevent duplicate requests
  - [ ] Cache recent searches
  - [ ] Monitor query time

- [ ] **Mobile Optimization** (DoD)
  - [ ] Responsive search bar
  - [ ] Touch-friendly results
  - [ ] Simplified mobile view
  - [ ] Test on devices

- [ ] **Add Tests** (DoD)
  - [ ] Search API tests
  - [ ] UI interaction tests
  - [ ] Performance benchmarks
  - [ ] Edge case handling

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