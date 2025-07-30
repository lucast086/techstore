# STORY-033: Payment Recording

## 📋 Story Details
- **Epic**: EPIC-002 (Customer Management)
- **Priority**: CRITICAL
- **Estimate**: 1 day
- **Status**: DONE

## 🎯 User Story
**As** María or Carlos,
**I want** to record customer payments against their account balance,
**So that** I can track when customers pay their debts and maintain accurate account balances

## ✅ Acceptance Criteria
1. [ ] Payment form accessible from customer profile when balance is negative
2. [ ] Required fields: amount, payment method
3. [ ] Optional fields: reference number, notes
4. [ ] Payment amount cannot exceed customer debt
5. [ ] Payment methods: cash, bank transfer, card
6. [ ] Generate unique receipt number automatically
7. [ ] Show balance before and after payment
8. [ ] Print receipt immediately after recording
9. [ ] Receipt shows "PAID IN FULL" when balance reaches zero
10. [ ] Payment history visible in customer profile
11. [ ] Cannot delete payments (only void with reason)
12. [ ] WhatsApp option to send receipt to customer

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── models/
│   └── payment.py           # Payment model
├── schemas/
│   └── payment.py           # Payment schemas
├── crud/
│   └── payment.py           # Payment CRUD operations
├── web/
│   └── payments.py          # Payment routes
├── templates/
│   ├── payments/
│   │   ├── record_payment.html
│   │   └── payment_list.html
│   └── reports/
│       └── payment_receipt.html
└── services/
    └── receipt_service.py   # Receipt generation
```

### Implementation Requirements:

1. **Payment Model** (`app/models/payment.py`):
```python
from sqlalchemy import Column, Integer, String, Decimal, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models import BaseModel

class Payment(BaseModel):
    __tablename__ = "payments"

    # Payment details
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Decimal(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, transfer, card
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Receipt info
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)

    # Audit
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    voided = Column(Boolean, default=False)
    void_reason = Column(Text, nullable=True)
    voided_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    voided_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", backref="payments")
    received_by = relationship("User", foreign_keys=[received_by_id])
    voided_by = relationship("User", foreign_keys=[voided_by_id])

    def __repr__(self):
        return f"<Payment {self.receipt_number} - ${self.amount}>"
```

2. **Payment Schemas** (`app/schemas/payment.py`):
```python
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    payment_method: str = Field(..., regex="^(cash|transfer|card)$")
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

    @validator('reference_number')
    def validate_reference(cls, v, values):
        method = values.get('payment_method')
        if method in ['transfer', 'card'] and not v:
            raise ValueError('Reference number required for transfer/card payments')
        return v

class PaymentResponse(BaseModel):
    id: int
    receipt_number: str
    customer_id: int
    customer_name: str
    amount: float
    payment_method: str
    reference_number: Optional[str]
    notes: Optional[str]
    received_by: str
    created_at: datetime
    voided: bool

    class Config:
        orm_mode = True

class PaymentVoid(BaseModel):
    void_reason: str = Field(..., min_length=10)
```

3. **Payment CRUD** (`app/crud/payment.py`):
```python
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate

class PaymentCRUD:
    def create(self, db: Session, customer_id: int,
               payment: PaymentCreate, received_by_id: int) -> Payment:
        """Record new payment"""
        # Generate receipt number
        receipt_number = self.generate_receipt_number(db)

        db_payment = Payment(
            customer_id=customer_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            notes=payment.notes,
            receipt_number=receipt_number,
            received_by_id=received_by_id
        )

        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)

        return db_payment

    def generate_receipt_number(self, db: Session) -> str:
        """Generate unique receipt number: REC-YYYYMMDD-XXXX"""
        today = datetime.now()
        prefix = f"REC-{today.strftime('%Y%m%d')}"

        # Get count of receipts today
        count = db.query(func.count(Payment.id)).filter(
            Payment.receipt_number.like(f"{prefix}%")
        ).scalar() or 0

        return f"{prefix}-{str(count + 1).zfill(4)}"

    def get_by_receipt(self, db: Session, receipt_number: str) -> Optional[Payment]:
        """Get payment by receipt number"""
        return db.query(Payment).filter(
            Payment.receipt_number == receipt_number
        ).first()

    def get_customer_payments(self, db: Session, customer_id: int,
                            include_voided: bool = False) -> List[Payment]:
        """Get all payments for a customer"""
        query = db.query(Payment).filter(Payment.customer_id == customer_id)

        if not include_voided:
            query = query.filter(Payment.voided == False)

        return query.order_by(Payment.created_at.desc()).all()

    def void_payment(self, db: Session, payment_id: int,
                    void_reason: str, voided_by_id: int) -> bool:
        """Void a payment (cannot delete)"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment or payment.voided:
            return False

        payment.voided = True
        payment.void_reason = void_reason
        payment.voided_by_id = voided_by_id
        payment.voided_at = datetime.now()

        db.commit()
        return True

payment_crud = PaymentCRUD()
```

4. **Payment Routes** (`app/web/payments.py`):
```python
from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from decimal import Decimal
from typing import Optional
from urllib.parse import quote

from app.dependencies import get_current_user, get_db
from app.crud.payment import payment_crud
from app.crud.customer import customer_crud
from app.services.balance_service import balance_service
from app.services.receipt_service import ReceiptService

router = APIRouter(prefix="/payments", tags=["payments-web"])

@router.get("/record/{customer_id}", response_class=HTMLResponse)
async def payment_form(
    customer_id: int,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Show payment recording form"""
    customer = customer_crud.get(db, customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")

    # Get current balance
    balance_info = balance_service.get_balance_summary(db, customer_id)

    return templates.TemplateResponse("payments/record_payment.html", {
        "request": request,
        "customer": customer,
        "balance_info": balance_info,
        "current_user": current_user
    })

@router.post("/record/{customer_id}")
async def record_payment(
    customer_id: int,
    request: Request,
    amount: Decimal = Form(..., gt=0),
    payment_method: str = Form(...),
    reference_number: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a customer payment"""
    try:
        # Check customer exists
        customer = customer_crud.get(db, customer_id)
        if not customer:
            raise HTTPException(404, "Customer not found")

        # Check amount doesn't exceed debt
        current_balance = balance_service.calculate_balance(db, customer_id)
        if current_balance >= 0:
            raise ValueError("Customer has no outstanding debt")

        if amount > abs(current_balance):
            raise ValueError(f"Payment amount exceeds debt of ${abs(current_balance):.2f}")

        # Create payment
        payment_data = PaymentCreate(
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes
        )

        payment = payment_crud.create(
            db=db,
            customer_id=customer_id,
            payment=payment_data,
            received_by_id=current_user.id
        )

        # Set success message
        request.session["flash_message"] = f"Payment recorded: {payment.receipt_number}"

        # Redirect to receipt view
        return RedirectResponse(
            url=f"/payments/{payment.id}/receipt?print=true",
            status_code=303
        )

    except ValueError as e:
        return templates.TemplateResponse("payments/record_payment.html", {
            "request": request,
            "customer": customer,
            "balance_info": balance_service.get_balance_summary(db, customer_id),
            "error": str(e),
            "form_data": {
                "amount": amount,
                "payment_method": payment_method,
                "reference_number": reference_number,
                "notes": notes
            },
            "current_user": current_user
        }, status_code=400)

@router.get("/{payment_id}/receipt")
async def view_receipt(
    payment_id: int,
    request: Request,
    format: str = Query("html", regex="^(html|pdf)$"),
    print: bool = Query(False),
    db: Session = Depends(get_db)
):
    """View or download payment receipt"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(404, "Payment not found")

    # Calculate balances
    balance_before = balance_service.calculate_balance_before_payment(
        db, payment.customer_id, payment.id
    )
    balance_after = balance_before + payment.amount

    receipt_data = {
        "payment": payment,
        "balance_before": balance_before,
        "balance_after": balance_after,
        "print_mode": print
    }

    if format == "pdf":
        receipt_service = ReceiptService()
        pdf_bytes = receipt_service.generate_payment_receipt(receipt_data)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={payment.receipt_number}.pdf"
            }
        )

    return templates.TemplateResponse("reports/payment_receipt.html", {
        "request": request,
        **receipt_data
    })

@router.get("/{payment_id}/whatsapp")
async def whatsapp_receipt(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Generate WhatsApp link with receipt info"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(404, "Payment not found")

    # Calculate new balance
    new_balance = balance_service.calculate_balance(db, payment.customer_id)

    message = (
        f"*Payment Receipt - {payment.receipt_number}*\n\n"
        f"Amount Received: ${payment.amount:.2f}\n"
        f"Payment Method: {payment.payment_method.title()}\n"
        f"Date: {payment.created_at.strftime('%B %d, %Y')}\n\n"
    )

    if new_balance == 0:
        message += "✅ *ACCOUNT PAID IN FULL*\n\n"
    elif new_balance < 0:
        message += f"Remaining Balance: ${abs(new_balance):.2f}\n\n"
    else:
        message += f"Account Credit: ${new_balance:.2f}\n\n"

    message += "Thank you for your payment!"

    whatsapp_url = f"https://wa.me/{payment.customer.phone}?text={quote(message)}"

    return {"url": whatsapp_url}
```

5. **Receipt Service** (`app/services/receipt_service.py`):
```python
from typing import Dict
from datetime import datetime
from jinja2 import Template

class ReceiptService:
    """Service for generating receipts"""

    def __init__(self):
        self.company_info = {
            "name": "TechStore",
            "address": "123 Main St, City",
            "phone": "(555) 123-4567",
            "email": "info@techstore.com"
        }

    def generate_payment_receipt(self, data: Dict) -> bytes:
        """Generate payment receipt PDF"""
        # Load template
        with open('templates/reports/payment_receipt.html', 'r') as f:
            template = Template(f.read())

        # Add company info
        data['company'] = self.company_info
        data['generated_at'] = datetime.now()

        # Render HTML
        html_content = template.render(**data)

        # Convert to PDF
        from weasyprint import HTML
        pdf = HTML(string=html_content).write_pdf()

        return pdf
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Receipt generates correctly
- [ ] Balance updates properly
- [ ] Cannot exceed debt amount
- [ ] Print function works
- [ ] WhatsApp sharing works
- [ ] Void function tested
- [ ] Mobile responsive

## 🧪 Testing Approach

### Manual Tests:
- Record cash payment
- Record transfer with reference
- Try to overpay debt
- Print receipt
- Void payment with reason
- View payment history

### Integration Tests:
- Payment creation flow
- Balance calculation after payment
- Receipt generation
- Void functionality
- Payment listing

### Edge Cases:
- Exact payment (zero balance)
- Customer with no debt
- Concurrent payments
- Void already voided

## 🔗 Dependencies
- **Depends on**:
  - STORY-028 (Customer Model)
  - STORY-032 (Account Balance)
  - STORY-027 (Database Setup)
- **Blocks**:
  - Complete account management
  - Sales on credit

## 📌 Notes
- Payments cannot be deleted, only voided
- Receipt numbers are sequential per day
- Consider email receipts in future
- SMS notifications could be added
- Integration with POS systems later

## 📝 Dev Notes

### Receipt Number Format:
- Format: `REC-YYYYMMDD-XXXX`
- Example: `REC-20240127-0001`
- Resets daily
- Sequential per day

### Balance Calculation:
```python
# Before payment
balance_before = sum(sales_on_credit) - sum(previous_payments)

# After payment
balance_after = balance_before + payment_amount
```

### Validation Rules:
1. Amount must be positive
2. Cannot exceed current debt
3. Reference required for non-cash
4. Cannot void twice

### MVP Simplifications:
- No partial payments tracking
- No payment plans
- No automated reminders
- Basic receipt format

## 📊 Tasks / Subtasks

- [ ] **Create Payment Model** (AC: 6, 11)
  - [ ] Define payment table
  - [ ] Add relationships
  - [ ] Create migration
  - [ ] Add indexes

- [ ] **Build Payment Form** (AC: 1, 2, 3, 5)
  - [ ] Create form template
  - [ ] Add validation
  - [ ] Show current balance
  - [ ] Payment method selection

- [ ] **Implement Recording Logic** (AC: 4, 6, 7)
  - [ ] Validate amount
  - [ ] Generate receipt number
  - [ ] Save payment
  - [ ] Update balance

- [ ] **Create Receipt Template** (AC: 7, 8, 9)
  - [ ] Design receipt layout
  - [ ] Show balances
  - [ ] Add company info
  - [ ] Handle paid in full

- [ ] **Add Print Function** (AC: 8)
  - [ ] Print-friendly CSS
  - [ ] Auto-print option
  - [ ] PDF generation
  - [ ] Print dialog

- [ ] **Build Payment History** (AC: 10)
  - [ ] List payments in profile
  - [ ] Show receipt numbers
  - [ ] Link to receipts
  - [ ] Filter voided

- [ ] **Implement Void Function** (AC: 11)
  - [ ] Void endpoint
  - [ ] Require reason
  - [ ] Update balance
  - [ ] Audit trail

- [ ] **Add WhatsApp Share** (AC: 12)
  - [ ] Generate message
  - [ ] Create link
  - [ ] Include receipt info
  - [ ] Test on mobile

- [ ] **Create Tests** (DoD)
  - [ ] Payment flow tests
  - [ ] Validation tests
  - [ ] Receipt generation
  - [ ] Balance updates

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
