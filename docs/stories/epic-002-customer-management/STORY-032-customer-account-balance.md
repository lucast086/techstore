# STORY-032: Customer Account Balance

## 📋 Story Details
- **Epic**: EPIC-002 (Customer Management)
- **Priority**: HIGH
- **Estimate**: 1 day
- **Status**: TODO

## 🎯 User Story
**As** María,  
**I want** to view customer account balances and transaction history,  
**So that** I can track credit sales and customer payments

## ✅ Acceptance Criteria
1. [ ] Balance always calculated from transactions (not stored)
2. [ ] Balance shows on customer list and profile
3. [ ] Positive balance = customer has credit
4. [ ] Negative balance = customer owes money
5. [ ] Transaction history shows sales and payments
6. [ ] Cannot delete customer with non-zero balance
7. [ ] Visual indicators for customers with debt
8. [ ] Basic account statement export as PDF
9. [ ] WhatsApp button to send balance reminder
10. [ ] Balance calculation is accurate and fast

## 🔧 Technical Details

### Files to Create/Update:
```
src/app/
├── services/
│   └── balance_service.py   # Balance calculation logic
├── web/
│   └── customers.py         # Add statement route
├── templates/
│   └── customers/
│       └── statement.html   # Account statement template
└── utils/
    └── pdf_generator.py     # PDF generation utility
```

### Implementation Requirements:

1. **Balance Service** (`app/services/balance_service.py`):
```python
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

class BalanceService:
    """Service for calculating customer balances from transactions"""
    
    def calculate_balance(self, db: Session, customer_id: int) -> Decimal:
        """
        Calculate current balance from all transactions
        MVP: Simple calculation from sales (debt) and payments (credit)
        """
        # TODO: When Sale model exists
        # sales_total = db.query(func.sum(Sale.total)).filter(
        #     Sale.customer_id == customer_id,
        #     Sale.payment_method == "credit"
        # ).scalar() or Decimal("0")
        
        # TODO: When Payment model exists
        # payments_total = db.query(func.sum(Payment.amount)).filter(
        #     Payment.customer_id == customer_id
        # ).scalar() or Decimal("0")
        
        # MVP: Return 0 for now
        return Decimal("0.00")
    
    def get_balance_summary(self, db: Session, customer_id: int) -> Dict:
        """Get balance with summary information"""
        balance = self.calculate_balance(db, customer_id)
        
        return {
            "current_balance": float(balance),
            "has_debt": balance < 0,
            "has_credit": balance > 0,
            "status": "debt" if balance < 0 else "credit" if balance > 0 else "clear",
            "formatted": self.format_balance(balance)
        }
    
    def format_balance(self, balance: Decimal) -> str:
        """Format balance for display"""
        if balance < 0:
            return f"Owes ${abs(balance):,.2f}"
        elif balance > 0:
            return f"Credit ${balance:,.2f}"
        else:
            return "$0.00"
    
    def get_transaction_history(self, db: Session, customer_id: int, 
                              limit: Optional[int] = None) -> List[Dict]:
        """
        Get transaction history with running balance
        MVP: Return empty list until transaction models exist
        """
        # TODO: Implement when Sale and Payment models exist
        # transactions = []
        # 
        # # Get all sales
        # sales = db.query(Sale).filter(
        #     Sale.customer_id == customer_id
        # ).all()
        # 
        # for sale in sales:
        #     transactions.append({
        #         "date": sale.created_at,
        #         "type": "sale",
        #         "description": f"Sale #{sale.id}",
        #         "amount": -sale.total,  # Negative for debt
        #         "reference": f"sale_{sale.id}"
        #     })
        # 
        # # Get all payments
        # payments = db.query(Payment).filter(
        #     Payment.customer_id == customer_id
        # ).all()
        # 
        # for payment in payments:
        #     transactions.append({
        #         "date": payment.created_at,
        #         "type": "payment",
        #         "description": payment.description,
        #         "amount": payment.amount,  # Positive for credit
        #         "reference": f"payment_{payment.id}"
        #     })
        # 
        # # Sort by date and calculate running balance
        # transactions.sort(key=lambda x: x['date'])
        # 
        # running_balance = Decimal("0")
        # for transaction in transactions:
        #     running_balance += transaction['amount']
        #     transaction['running_balance'] = float(running_balance)
        # 
        # if limit:
        #     transactions = transactions[-limit:]
        # 
        # return transactions
        
        return []  # MVP: Empty for now
    
    def can_delete_customer(self, db: Session, customer_id: int) -> tuple[bool, str]:
        """Check if customer can be deleted based on balance"""
        balance = self.calculate_balance(db, customer_id)
        
        if balance != 0:
            return False, f"Customer has non-zero balance: {self.format_balance(balance)}"
        
        return True, "Customer can be deleted"
    
    def get_customers_with_debt(self, db: Session, limit: Optional[int] = None) -> List[Dict]:
        """
        Get list of customers with outstanding debt
        MVP: Return empty list for now
        """
        # TODO: Implement when we can calculate balances
        return []

balance_service = BalanceService()
```

2. **Update Customer CRUD** (Update `app/crud/customer.py`):
```python
# Add to CustomerCRUD class
def get_with_balance(self, db: Session, customer_id: int) -> Dict:
    """Get customer with calculated balance"""
    customer = self.get(db, customer_id)
    if not customer:
        return None
    
    from app.services.balance_service import balance_service
    balance_info = balance_service.get_balance_summary(db, customer_id)
    
    return {
        **customer.to_dict(),
        **balance_info
    }

def list_with_balances(self, db: Session, skip: int = 0, limit: int = 20) -> List[Dict]:
    """Get customers with their balances"""
    customers = db.query(Customer).filter(
        Customer.is_active == True
    ).offset(skip).limit(limit).all()
    
    from app.services.balance_service import balance_service
    result = []
    
    for customer in customers:
        balance_info = balance_service.get_balance_summary(db, customer.id)
        result.append({
            **customer.to_dict(),
            **balance_info
        })
    
    return result
```

3. **Statement Route** (Update `app/web/customers.py`):
```python
from app.services.balance_service import balance_service
from app.utils.pdf_generator import generate_statement_pdf

@router.get("/{customer_id}/statement", response_class=HTMLResponse)
async def customer_statement(
    customer_id: int,
    request: Request,
    format: str = Query("html", regex="^(html|pdf)$"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View or download customer account statement"""
    customer = customer_crud.get(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get balance and transactions
    balance_info = balance_service.get_balance_summary(db, customer_id)
    transactions = balance_service.get_transaction_history(db, customer_id)
    
    if format == "pdf":
        # Generate PDF
        pdf_bytes = generate_statement_pdf(customer, balance_info, transactions)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=statement_{customer.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    
    # HTML view
    return templates.TemplateResponse("customers/statement.html", {
        "request": request,
        "customer": customer,
        "balance_info": balance_info,
        "transactions": transactions,
        "current_user": current_user,
        "generated_at": datetime.now()
    })

@router.post("/{customer_id}/send-balance-reminder")
async def send_balance_reminder(
    customer_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate WhatsApp link for balance reminder"""
    customer = customer_crud.get(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    balance_info = balance_service.get_balance_summary(db, customer_id)
    
    if not balance_info['has_debt']:
        raise HTTPException(status_code=400, detail="Customer has no outstanding debt")
    
    # Generate WhatsApp message
    message = (
        f"Hello {customer.name},\n\n"
        f"This is a friendly reminder about your account balance.\n"
        f"Current balance: ${abs(balance_info['current_balance']):,.2f}\n\n"
        f"Please contact us to arrange payment.\n"
        f"Thank you!"
    )
    
    whatsapp_url = f"https://wa.me/{customer.phone}?text={quote(message)}"
    
    return {"whatsapp_url": whatsapp_url, "message": message}
```

4. **Statement Template** (`templates/customers/statement.html`):
```html
{% extends "base.html" %}

{% block content %}
<div class="container statement-container">
    <div class="statement-header">
        <div class="statement-title">
            <h1>Account Statement</h1>
            <div class="statement-actions">
                <a href="/customers/{{ customer.id }}" class="btn-secondary">
                    Back to Profile
                </a>
                <a href="?format=pdf" class="btn-primary">
                    <svg><!-- download icon --></svg>
                    Download PDF
                </a>
            </div>
        </div>
        
        <div class="statement-info">
            <div class="customer-info">
                <h2>{{ customer.name }}</h2>
                <p>{{ customer.phone }}</p>
                {% if customer.phone_secondary %}
                <p>{{ customer.phone_secondary }}</p>
                {% endif %}
                {% if customer.address %}
                <p>{{ customer.address }}</p>
                {% endif %}
            </div>
            
            <div class="statement-meta">
                <p><strong>Statement Date:</strong> {{ generated_at.strftime('%B %d, %Y') }}</p>
                <p><strong>Customer Since:</strong> {{ customer.created_at.strftime('%B %d, %Y') }}</p>
            </div>
        </div>
    </div>
    
    <div class="balance-summary">
        <h3>Current Balance</h3>
        <div class="balance-display {{ balance_info.status }}">
            {% if balance_info.has_debt %}
                <span class="label">Amount Due</span>
                <span class="amount">${{ "{:,.2f}".format(abs(balance_info.current_balance)) }}</span>
            {% elif balance_info.has_credit %}
                <span class="label">Credit Balance</span>
                <span class="amount">${{ "{:,.2f}".format(balance_info.current_balance) }}</span>
            {% else %}
                <span class="label">Balance</span>
                <span class="amount">$0.00</span>
            {% endif %}
        </div>
    </div>
    
    <div class="transaction-section">
        <h3>Transaction History</h3>
        {% if transactions %}
        <table class="statement-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Debit</th>
                    <th>Credit</th>
                    <th>Balance</th>
                </tr>
            </thead>
            <tbody>
                {% for transaction in transactions %}
                <tr>
                    <td>{{ transaction.date.strftime('%m/%d/%Y') }}</td>
                    <td>{{ transaction.description }}</td>
                    <td>
                        {% if transaction.amount < 0 %}
                        ${{ "{:,.2f}".format(abs(transaction.amount)) }}
                        {% endif %}
                    </td>
                    <td>
                        {% if transaction.amount > 0 %}
                        ${{ "{:,.2f}".format(transaction.amount) }}
                        {% endif %}
                    </td>
                    <td>${{ "{:,.2f}".format(abs(transaction.running_balance)) }}</td>
                </tr>
                {% endfor %}
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="4"><strong>Current Balance</strong></td>
                    <td><strong>${{ "{:,.2f}".format(abs(balance_info.current_balance)) }}</strong></td>
                </tr>
            </tfoot>
        </table>
        {% else %}
        <div class="empty-transactions">
            <p>No transactions recorded yet.</p>
        </div>
        {% endif %}
    </div>
    
    <div class="statement-footer">
        <p class="disclaimer">
            This statement is generated automatically and reflects all transactions up to the statement date.
            For questions about your account, please contact us.
        </p>
    </div>
</div>
{% endblock %}
```

5. **Simple PDF Generator** (`app/utils/pdf_generator.py`):
```python
from io import BytesIO
from datetime import datetime
from typing import Dict, List

def generate_statement_pdf(customer: Dict, balance_info: Dict, transactions: List[Dict]) -> bytes:
    """
    Generate a simple PDF statement
    MVP: Basic implementation, can enhance later
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph("ACCOUNT STATEMENT", styles['Title']))
    story.append(Spacer(1, 0.5*inch))
    
    # Customer Info
    story.append(Paragraph(f"<b>Customer:</b> {customer['name']}", styles['Normal']))
    story.append(Paragraph(f"<b>Phone:</b> {customer['phone']}", styles['Normal']))
    if customer.get('address'):
        story.append(Paragraph(f"<b>Address:</b> {customer['address']}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Statement Date
    story.append(Paragraph(f"<b>Statement Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Current Balance
    balance_style = ParagraphStyle(
        'Balance',
        parent=styles['Heading2'],
        textColor=colors.red if balance_info['has_debt'] else colors.green if balance_info['has_credit'] else colors.black
    )
    story.append(Paragraph(f"Current Balance: {balance_info['formatted']}", balance_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Transactions Table
    if transactions:
        story.append(Paragraph("Transaction History", styles['Heading2']))
        
        # Table data
        data = [['Date', 'Description', 'Debit', 'Credit', 'Balance']]
        
        for trans in transactions:
            date = trans['date'].strftime('%m/%d/%Y')
            desc = trans['description']
            debit = f"${abs(trans['amount']):,.2f}" if trans['amount'] < 0 else ""
            credit = f"${trans['amount']:,.2f}" if trans['amount'] > 0 else ""
            balance = f"${abs(trans['running_balance']):,.2f}"
            
            data.append([date, desc, debit, credit, balance])
        
        # Create table
        table = Table(data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table)
    else:
        story.append(Paragraph("No transactions recorded.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Balance calculation service created
- [ ] Statement generation works
- [ ] PDF export functional
- [ ] WhatsApp integration tested
- [ ] Performance acceptable (< 200ms)
- [ ] Deletion prevention works
- [ ] Visual indicators clear

## 🧪 Testing Approach

### Unit Tests:
- Balance calculation logic
- Transaction history sorting
- Deletion validation
- PDF generation

### Integration Tests:
- Statement view
- PDF download
- WhatsApp URL generation
- Balance in customer list

### Manual Tests:
- View statement with no transactions
- Export PDF
- Send WhatsApp reminder
- Try delete with balance

## 🔗 Dependencies
- **Depends on**: 
  - STORY-028 (Customer Model)
  - STORY-031 (Customer Profile)
- **Blocks**: 
  - Sales features (need balance tracking)
  - Payment features (need balance tracking)

## 📌 Notes
- MVP: Balance calculation returns 0 until transaction models exist
- PDF is basic, can enhance with company branding later
- WhatsApp message is simple template
- Future: Email statements, scheduled reminders
- Future: Aging reports, payment terms

## 📝 Dev Notes

### MVP Approach:
1. **Infrastructure Ready**: Service and UI ready for when transactions exist
2. **Placeholder Data**: Returns 0 balance and empty transactions for now
3. **Easy Integration**: Just update balance_service when models ready

### Future Integration:
```python
# When Sale model exists, update calculate_balance:
sales_total = db.query(func.sum(Sale.total)).filter(
    Sale.customer_id == customer_id,
    Sale.payment_method == "credit"
).scalar() or Decimal("0")

# When Payment model exists:
payments_total = db.query(func.sum(Payment.amount)).filter(
    Payment.customer_id == customer_id
).scalar() or Decimal("0")

return payments_total - sales_total
```

### Performance Considerations:
- Index on customer_id in transaction tables
- Consider caching balance for large customers
- Pagination for transaction history

## 📊 Tasks / Subtasks

- [ ] **Create Balance Service** (AC: 1, 2, 10)
  - [ ] Calculate balance method
  - [ ] Get balance summary
  - [ ] Format balance display
  - [ ] Transaction history method

- [ ] **Update Customer CRUD** (AC: 2, 6)
  - [ ] Add balance to list
  - [ ] Add deletion check
  - [ ] Get with balance method
  - [ ] List with balances

- [ ] **Create Statement Route** (AC: 5, 8)
  - [ ] HTML statement view
  - [ ] PDF generation
  - [ ] Add to customer routes
  - [ ] Handle format parameter

- [ ] **Build Statement Template** (AC: 3, 4, 5, 7)
  - [ ] Statement layout
  - [ ] Balance display
  - [ ] Transaction table
  - [ ] PDF download link

- [ ] **Implement PDF Generation** (AC: 8)
  - [ ] Basic PDF layout
  - [ ] Customer info section
  - [ ] Transaction table
  - [ ] Return as bytes

- [ ] **Add WhatsApp Feature** (AC: 9)
  - [ ] Balance reminder endpoint
  - [ ] Message template
  - [ ] URL generation
  - [ ] Add to UI

- [ ] **Update UI Components** (AC: 2, 7)
  - [ ] Balance in customer list
  - [ ] Debt indicators
  - [ ] Statement link
  - [ ] WhatsApp button

- [ ] **Add Tests** (DoD)
  - [ ] Service unit tests
  - [ ] Route tests
  - [ ] PDF generation test
  - [ ] Balance calculation test

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