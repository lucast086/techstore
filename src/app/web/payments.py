"""Payment web routes for HTMX interface."""

import logging
from decimal import Decimal
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.crud.customer import customer_crud
from app.crud.payment import payment_crud
from app.dependencies import get_db
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentMethodDetail
from app.services.balance_service import balance_service
from app.services.payment_service import payment_service
from app.services.receipt_service import receipt_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments-web"])
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/", response_class=HTMLResponse)
async def payments_list(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> HTMLResponse:
    """Render payments list page.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated user.
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        HTML response with payments list.
    """
    # Get recent payments
    payments = payment_crud.get_recent_payments(db, skip=skip, limit=limit)

    context = {
        "request": request,
        "current_user": current_user,
        "payments": payments,
        "page_title": "Payment History",
    }

    return templates.TemplateResponse("payments/list.html", context)


@router.get("/new", response_class=HTMLResponse)
async def payments_new(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Render new payment page to select a customer.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        HTML response with customer selection for new payment.
    """
    # Get customers with balances
    customers = customer_crud.get_customers_with_balance(db)

    context = {
        "request": request,
        "current_user": current_user,
        "customers": customers,
        "page_title": "New Payment",
    }

    return templates.TemplateResponse("payments/new.html", context)


@router.get("/pending", response_class=HTMLResponse)
async def payments_pending(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Render pending payments page.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        HTML response with customers having pending payments.
    """
    # Get customers with positive balances
    customers = customer_crud.get_customers_with_positive_balance(db)

    context = {
        "request": request,
        "current_user": current_user,
        "customers": customers,
        "page_title": "Pending Payments",
    }

    return templates.TemplateResponse("payments/pending.html", context)


@router.get("/record/{customer_id}", response_class=HTMLResponse)
async def payment_form(
    customer_id: int,
    request: Request,
    sale_id: int = Query(None),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Show payment recording form.

    Args:
        customer_id: ID of the customer.
        request: FastAPI request object.
        sale_id: Optional sale ID for sale-specific payment.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        HTML response with payment form.
    """
    customer = customer_crud.get(db, customer_id)
    if not customer:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Customer not found"},
            status_code=404,
        )

    # Get sale if provided
    sale = None
    if sale_id:
        from app.crud.sale import sale_crud

        sale = sale_crud.get(db, sale_id)
        if not sale or sale.customer_id != customer_id:
            sale = None

    # Get current balance
    balance_info = balance_service.get_balance_summary(db, customer_id)

    return templates.TemplateResponse(
        "payments/form.html",
        {
            "request": request,
            "customer": customer,
            "sale": sale,
            "balance_info": balance_info,
            "current_user": current_user,
        },
    )


@router.post("/record/{customer_id}")
async def record_payment(
    customer_id: int,
    request: Request,
    amount: Annotated[Decimal, Form(..., gt=0)],
    payment_method: Annotated[str, Form(...)],
    reference_number: Annotated[str | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Record a customer payment.

    Args:
        customer_id: ID of the customer.
        request: FastAPI request object.
        amount: Payment amount.
        payment_method: Payment method (cash, transfer, card).
        reference_number: Reference number for non-cash payments.
        notes: Optional notes.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        Redirect to receipt or error form.
    """
    try:
        # Check customer exists
        customer = customer_crud.get(db, customer_id)
        if not customer:
            raise HTTPException(404, "Customer not found")

        # Check amount doesn't exceed debt (MVP: skip this check for now since we don't have sales)
        # current_balance = balance_service.calculate_balance(db, customer_id)
        # if current_balance >= 0:
        #     raise ValueError("Customer has no outstanding debt")
        #
        # if amount > abs(current_balance):
        #     raise ValueError(f"Payment amount exceeds debt of ${abs(current_balance):.2f}")

        # Create payment
        payment_data = PaymentCreate(
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
        )

        payment = payment_crud.create(
            db=db,
            customer_id=customer_id,
            payment=payment_data,
            received_by_id=current_user.id,
        )

        logger.info(f"Payment recorded: {payment.receipt_number}")

        # Redirect to receipt view with print parameter
        return RedirectResponse(
            url=f"/payments/{payment.id}/receipt?print=true", status_code=303
        )

    except ValueError as e:
        logger.error(f"Error recording payment: {e}")

        # Get balance info again for form display
        balance_info = balance_service.get_balance_summary(db, customer_id)

        return templates.TemplateResponse(
            "payments/record_payment.html",
            {
                "request": request,
                "customer": customer,
                "balance_info": balance_info,
                "error": str(e),
                "form_data": {
                    "amount": amount,
                    "payment_method": payment_method,
                    "reference_number": reference_number,
                    "notes": notes,
                },
                "current_user": current_user,
            },
            status_code=400,
        )


@router.get("/{payment_id}/receipt")
async def view_receipt(
    payment_id: int,
    request: Request,
    format: str = Query("html", pattern="^(html|pdf)$"),
    print: bool = Query(False),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """View or download payment receipt.

    Args:
        payment_id: ID of the payment.
        request: FastAPI request object.
        format: Output format (html or pdf).
        print: Whether to auto-print.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        HTML receipt or PDF download.
    """
    payment = payment_crud.get(db, payment_id)
    if not payment:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Payment not found"},
            status_code=404,
        )

    # Calculate balances
    balance_before = balance_service.calculate_balance_before_payment(
        db, payment.customer_id, payment.id
    )
    balance_after = balance_before + payment.amount

    receipt_data = {
        "request": request,
        "payment": payment,
        "balance_before": float(balance_before),
        "balance_after": float(balance_after),
        "print_mode": print,
        "current_user": current_user,
    }

    if format == "pdf":
        # Generate PDF receipt
        pdf_bytes = receipt_service.generate_payment_receipt_pdf(receipt_data)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={payment.receipt_number}.pdf"
            },
        )

    # Use the template instead of the service for HTML
    return templates.TemplateResponse("payments/receipt.html", receipt_data)


@router.get("/{payment_id}/whatsapp")
async def whatsapp_receipt(
    payment_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Generate WhatsApp link with receipt info.

    Args:
        payment_id: ID of the payment.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        JSON with WhatsApp URL.
    """
    payment = payment_crud.get(db, payment_id)
    if not payment:
        return {"error": "Payment not found"}

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

    return {"url": whatsapp_url, "message": message}


@router.get("/customer/{customer_id}/history", response_class=HTMLResponse)
async def payment_history(
    customer_id: int,
    request: Request,
    include_voided: bool = Query(False),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """View customer payment history.

    Args:
        customer_id: ID of the customer.
        request: FastAPI request object.
        include_voided: Whether to include voided payments.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        HTML response with payment history.
    """
    customer = customer_crud.get(db, customer_id)
    if not customer:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Customer not found"},
            status_code=404,
        )

    # Get payment history
    payments = payment_crud.get_customer_payments(db, customer_id, include_voided)

    return templates.TemplateResponse(
        "payments/payment_list.html",
        {
            "request": request,
            "customer": customer,
            "payments": payments,
            "include_voided": include_voided,
            "current_user": current_user,
        },
    )


@router.post("/{payment_id}/void")
async def void_payment(
    payment_id: int,
    request: Request,
    void_reason: Annotated[str, Form(..., min_length=10)],
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Void a payment.

    Args:
        payment_id: ID of the payment to void.
        request: FastAPI request object.
        void_reason: Reason for voiding.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        Redirect back to payment history.
    """
    payment = payment_crud.get(db, payment_id)
    if not payment:
        return {"error": "Payment not found"}

    success = payment_crud.void_payment(db, payment_id, void_reason, current_user.id)

    if not success:
        return {"error": "Failed to void payment"}

    # Redirect back to customer payment history
    return RedirectResponse(
        url=f"/payments/customer/{payment.customer_id}/history?include_voided=true",
        status_code=303,
    )


@router.post("/process")
async def process_payment(
    request: Request,
    customer_id: Annotated[int, Form(...)],
    payment_type: Annotated[str, Form(...)],
    sale_id: Annotated[int | None, Form()] = None,
    allow_overpayment: Annotated[bool, Form()] = False,
    notes: Annotated[str | None, Form()] = None,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Process payment with support for mixed payment methods.

    Args:
        request: FastAPI request object.
        customer_id: ID of the customer.
        payment_type: Type of payment (single or mixed).
        sale_id: Optional sale ID.
        allow_overpayment: Whether to allow overpayment.
        notes: Optional notes.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        Redirect to receipt or error page.
    """
    try:
        # Get form data
        form_data = await request.form()

        if payment_type == "single":
            # Single payment method
            amount = Decimal(form_data.get("amount", "0"))
            payment_method = form_data.get("payment_method")
            reference_number = form_data.get("reference_number")

            payment_data = PaymentCreate(
                amount=amount,
                payment_method=payment_method,
                reference_number=reference_number,
                notes=notes,
            )

            payment = payment_service.process_payment(
                db=db,
                customer_id=customer_id,
                sale_id=sale_id,
                payment_data=payment_data,
                user_id=current_user.id,
                allow_overpayment=allow_overpayment,
            )
        else:
            # Mixed payment methods
            payment_methods = []

            for method in ["cash", "transfer", "card"]:
                if form_data.get(f"method_enabled_{method}"):
                    amount = Decimal(form_data.get(f"method_amount_{method}", "0"))
                    if amount > 0:
                        reference = form_data.get(f"method_reference_{method}")
                        payment_methods.append(
                            PaymentMethodDetail(
                                payment_method=method,
                                amount=amount,
                                reference_number=reference,
                            )
                        )

            if not payment_methods:
                raise ValueError("No payment methods selected")

            payment = payment_service.process_mixed_payment(
                db=db,
                customer_id=customer_id,
                sale_id=sale_id,
                payment_methods=payment_methods,
                notes=notes,
                user_id=current_user.id,
                allow_overpayment=allow_overpayment,
            )

        logger.info(f"Payment processed: {payment.receipt_number}")

        # Redirect to receipt with print option
        return RedirectResponse(
            url=f"/payments/{payment.id}/receipt?print=true", status_code=303
        )

    except ValueError as e:
        logger.error(f"Payment validation error: {e}")

        # Get customer and balance info for error display
        customer = customer_crud.get(db, customer_id)
        balance_info = balance_service.get_balance_summary(db, customer_id)

        # Get sale if provided
        sale = None
        if sale_id:
            from app.crud.sale import sale_crud

            sale = sale_crud.get(db, sale_id)

        return templates.TemplateResponse(
            "payments/form.html",
            {
                "request": request,
                "customer": customer,
                "sale": sale,
                "balance_info": balance_info,
                "error": str(e),
                "current_user": current_user,
            },
            status_code=400,
        )
