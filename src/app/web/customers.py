"""Customer web routes for HTMX interface."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.crud.customer import customer_crud
from app.dependencies import get_db
from app.models.user import User
from app.schemas.customer import CustomerCreate
from app.services.balance_service import balance_service
from app.services.customer import customer_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers-web"])
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/", response_class=HTMLResponse)
async def customer_list(
    request: Request,
    page: int = Query(1, ge=1),
    search: str | None = Query(None),
    success: str | None = Query(None),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Customer list page - HTMX endpoint.

    Args:
        request: FastAPI request object.
        page: Page number for pagination.
        search: Optional search query.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        HTML response with customer list.
    """
    logger.info(f"Accessing customer list via HTMX - page: {page}, search: {search}")

    per_page = 20

    if search:
        # Call service for search
        customers = customer_service.search_customers(
            db=db, query=search, include_inactive=False, limit=per_page
        )
        # Add balance info to each customer
        customers_with_balance = []
        for customer in customers:
            balance_info = balance_service.get_balance_summary(db, customer.id)
            customer_dict = (
                customer.to_dict() if hasattr(customer, "to_dict") else customer
            )
            customers_with_balance.append({**customer_dict, **balance_info})
        customers = customers_with_balance
        total = len(customers)  # For now, simple count
    else:
        # Get customers with balances using updated CRUD method
        skip = (page - 1) * per_page
        customers = customer_crud.list_with_balances(db, skip=skip, limit=per_page)
        total = customer_service.get_customer_count(db)

    total_pages = (total + per_page - 1) // per_page

    # Decode success message if present
    success_message = None
    if success == "registered":
        success_message = "Cliente registrado exitosamente!"

    return templates.TemplateResponse(
        "customers/list.html",
        {
            "request": request,
            "customers": customers,
            "page": page,
            "total_pages": total_pages,
            "search": search or "",
            "current_user": current_user,
            "success_message": success_message,
        },
    )


@router.get("/new", response_class=HTMLResponse)
async def new_customer_form(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Show customer registration form.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated user.

    Returns:
        HTML response with registration form.
    """
    return templates.TemplateResponse(
        "customers/form.html",
        {
            "request": request,
            "customer": None,  # New customer
            "current_user": current_user,
        },
    )


@router.post("/new")
async def create_customer_submit(
    request: Request,
    name: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    phone_secondary: Annotated[str | None, Form()] = None,
    email: Annotated[str | None, Form()] = None,
    address: Annotated[str | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Process customer registration form - HTMX endpoint.

    Args:
        request: FastAPI request object.
        name: Customer name.
        phone: Primary phone number.
        phone_secondary: Optional secondary phone.
        email: Optional email address.
        address: Optional physical address.
        notes: Optional notes.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        Redirect to customer profile on success, form with error on failure.
    """
    logger.info(f"Creating customer via HTMX form: {name}")

    try:
        # Create customer data
        customer_data = CustomerCreate(
            name=name,
            phone=phone,
            phone_secondary=phone_secondary,
            email=email,
            address=address,
            notes=notes,
        )

        # Call service directly
        customer = customer_service.create_customer(
            db=db, customer_data=customer_data, created_by_id=current_user.id
        )

        logger.info(f"Customer created successfully via HTMX: {customer.id}")

        # Redirect to customer list with success message
        # (redirecting to profile would give 404 since profile not implemented)
        return RedirectResponse(
            url="/customers?success=registered", status_code=status.HTTP_303_SEE_OTHER
        )

    except ValueError as e:
        logger.error(f"Error creating customer via HTMX: {e}")

        # Return form with error
        return templates.TemplateResponse(
            "customers/form.html",
            {
                "request": request,
                "customer": None,
                "error": str(e),
                "form_data": {
                    "name": name,
                    "phone": phone,
                    "phone_secondary": phone_secondary,
                    "email": email,
                    "address": address,
                    "notes": notes,
                },
                "current_user": current_user,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/{customer_id}/statement", response_class=HTMLResponse)
async def customer_statement(
    customer_id: int,
    request: Request,
    format: str = Query("html", pattern="^(html|pdf)$"),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """View or download customer account statement.

    Args:
        customer_id: ID of the customer.
        request: FastAPI request object.
        format: Output format (html or pdf).
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        HTML statement or PDF download.
    """
    customer = customer_crud.get(db, customer_id)
    if not customer:
        # Return 404 page
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Customer not found"},
            status_code=404,
        )

    # Get balance and transactions
    balance_info = balance_service.get_balance_summary(db, customer_id)
    transactions = balance_service.get_transaction_history(db, customer_id)

    if format == "pdf":
        # Generate PDF using simple HTML to PDF approach
        from app.utils.pdf_generator import generate_statement_pdf

        pdf_bytes = generate_statement_pdf(
            customer.to_dict(), balance_info, transactions
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=statement_{customer.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            },
        )

    # HTML view
    return templates.TemplateResponse(
        "customers/statement.html",
        {
            "request": request,
            "customer": customer,
            "balance_info": balance_info,
            "transactions": transactions,
            "current_user": current_user,
            "generated_at": datetime.now(),
        },
    )


@router.post("/{customer_id}/send-balance-reminder")
async def send_balance_reminder(
    customer_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Generate WhatsApp link for balance reminder.

    Args:
        customer_id: ID of the customer.
        request: FastAPI request object.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        JSON with WhatsApp URL.
    """
    customer = customer_crud.get(db, customer_id)
    if not customer:
        return {"error": "Cliente no encontrado"}

    balance_info = balance_service.get_balance_summary(db, customer_id)

    if not balance_info["has_debt"]:
        return {"error": "El cliente no tiene deuda pendiente"}

    # Generate WhatsApp message
    message = (
        f"Hola {customer.name},\n\n"
        f"Esta es una recordatorio sobre tu saldo de cuenta.\n"
        f"Saldo actual: ${abs(balance_info['current_balance']):,.2f}\n\n"
        f"Por favor, contáctenos para programar el pago.\n"
        f"Gracias!"
    )

    whatsapp_url = f"https://wa.me/{customer.phone}?text={quote(message)}"

    return {"whatsapp_url": whatsapp_url, "message": message}


@router.get("/{customer_id}", response_class=HTMLResponse)
async def customer_detail(
    customer_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
):
    """Customer detail/profile page.

    Args:
        customer_id: ID of the customer.
        request: FastAPI request object.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        HTML response with customer profile.
    """
    logger.info(f"Accessing customer detail via HTMX - customer_id: {customer_id}")

    # Get customer
    customer = customer_crud.get(db, customer_id)
    if not customer:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Cliente no encontrado"},
            status_code=404,
        )

    # Get balance info
    balance_info = balance_service.get_balance_summary(db, customer_id)

    # Get recent transactions (last 10)
    transactions = balance_service.get_transaction_history(db, customer_id, limit=10)

    return templates.TemplateResponse(
        "customers/detail.html",
        {
            "request": request,
            "customer": customer,
            "balance_info": balance_info,
            "recent_transactions": transactions,
            "current_user": current_user,
        },
    )
