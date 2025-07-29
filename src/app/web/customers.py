"""Customer web routes for HTMX interface."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.dependencies import get_db
from app.models.user import User
from app.schemas.customer import CustomerCreate
from app.services.customer import customer_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers-web"])
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/", response_class=HTMLResponse)
async def customer_list(
    request: Request,
    page: int = Query(1, ge=1),
    search: str | None = Query(None),
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
        total = len(customers)  # For now, simple count
    else:
        # For pagination without search, we still need to get customers directly
        # TODO: Add pagination support to service layer
        skip = (page - 1) * per_page
        from app.models.customer import Customer

        customers = (
            db.query(Customer)
            .filter(Customer.is_active.is_(True))
            .offset(skip)
            .limit(per_page)
            .all()
        )
        total = customer_service.get_customer_count(db)

    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        "customers/list.html",
        {
            "request": request,
            "customers": customers,
            "page": page,
            "total_pages": total_pages,
            "search": search or "",
            "current_user": current_user,
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

        # Set success message
        request.session[
            "flash_message"
        ] = f"Customer {customer.name} registered successfully!"

        # Redirect to customer profile
        return RedirectResponse(
            url=f"/customers/{customer.id}", status_code=status.HTTP_303_SEE_OTHER
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
