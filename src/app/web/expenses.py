"""Web routes for expense management."""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie, require_web_role
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.expense import (
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCreate,
    ExpenseFilter,
    ExpenseUpdate,
)
from app.services.expense_service import expense_service

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/app/templates")

# Dependency for admin-only routes
require_admin = require_web_role(["admin"])


@router.get("/expenses/categories", response_class=HTMLResponse)
async def expense_categories_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Render expense categories management page (Admin only)."""
    categories = expense_service.get_all_categories(db)

    return templates.TemplateResponse(
        "expenses/categories.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": categories,
        },
    )


@router.get("/expenses/categories/new", response_class=HTMLResponse)
async def new_category_form(
    request: Request,
    current_user: User = Depends(require_admin),
):
    """Render new category form (HTMX partial)."""
    return templates.TemplateResponse(
        "expenses/_category_form.html",
        {
            "request": request,
            "current_user": current_user,
            "category": None,
            "mode": "create",
        },
    )


@router.get("/expenses/categories/{category_id}/edit", response_class=HTMLResponse)
async def edit_category_form(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Render edit category form (HTMX partial)."""
    from app.crud.expense_category import expense_category

    category = expense_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return templates.TemplateResponse(
        "expenses/_category_form.html",
        {
            "request": request,
            "current_user": current_user,
            "category": category,
            "mode": "edit",
        },
    )


@router.post("/expenses/categories", response_class=HTMLResponse)
async def create_category(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create new expense category (HTMX endpoint)."""
    try:
        category_in = ExpenseCategoryCreate(
            name=name,
            description=description,
        )
        category = expense_service.manage_category(db, category_create=category_in)

        # Return the new row for the table
        return templates.TemplateResponse(
            "expenses/_category_row.html",
            {
                "request": request,
                "current_user": current_user,
                "category": category,
            },
        )
    except ValueError as e:
        # Return error message
        return HTMLResponse(
            content=f'<div class="text-red-600 text-sm mt-2">{str(e)}</div>',
            status_code=400,
        )


@router.put("/expenses/categories/{category_id}", response_class=HTMLResponse)
async def update_category(
    request: Request,
    category_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update expense category (HTMX endpoint)."""
    try:
        # Convert form checkbox to boolean
        if is_active is not None:
            is_active = is_active == "on" or is_active is True

        category_in = ExpenseCategoryUpdate(
            name=name if name else None,
            description=description if description else None,
            is_active=is_active,
        )

        category = expense_service.manage_category(
            db, category_id=category_id, category_update=category_in
        )

        # Return the updated row
        return templates.TemplateResponse(
            "expenses/_category_row.html",
            {
                "request": request,
                "current_user": current_user,
                "category": category,
            },
        )
    except ValueError as e:
        # Return error message
        return HTMLResponse(
            content=f'<div class="text-red-600 text-sm mt-2">{str(e)}</div>',
            status_code=400,
        )


@router.delete("/expenses/categories/{category_id}", response_class=HTMLResponse)
async def deactivate_category(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deactivate expense category (HTMX endpoint)."""
    try:
        category = expense_service.deactivate_category(db, category_id=category_id)

        # Return the updated row showing deactivated status
        return templates.TemplateResponse(
            "expenses/_category_row.html",
            {
                "request": request,
                "current_user": current_user,
                "category": category,
            },
        )
    except ValueError as e:
        # Return error message
        return HTMLResponse(
            content=f'<div class="text-red-600 text-sm mt-2">{str(e)}</div>',
            status_code=400,
        )


# Expense Registration Routes
@router.get("/expenses", response_class=HTMLResponse)
async def expenses_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
):
    """Render expense list page with filters."""
    # Parse filter parameters
    filters = ExpenseFilter()
    if date_from:
        try:
            filters.date_from = date.fromisoformat(date_from)
        except ValueError:
            pass
    if date_to:
        try:
            filters.date_to = date.fromisoformat(date_to)
        except ValueError:
            pass
    if category_id:
        filters.category_id = category_id
    if payment_method:
        filters.payment_method = payment_method

    # Get expenses with filters
    expenses = expense_service.get_expenses_with_filters(db, filters=filters, limit=100)

    # Get categories for filter dropdown
    categories = expense_service.get_categories_for_dropdown(db)

    # Calculate totals
    total_amount = sum(exp.amount for exp in expenses)

    return templates.TemplateResponse(
        "expenses/expense_list.html",
        {
            "request": request,
            "current_user": current_user,
            "expenses": expenses,
            "categories": categories,
            "filters": {
                "date_from": date_from,
                "date_to": date_to,
                "category_id": category_id,
                "payment_method": payment_method,
            },
            "total_amount": total_amount,
        },
    )


@router.get("/expenses/new", response_class=HTMLResponse)
async def new_expense_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render new expense form."""
    categories = expense_service.get_categories_for_dropdown(db)

    return templates.TemplateResponse(
        "expenses/expense_form.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": categories,
            "expense": None,
        },
    )


@router.post("/expenses", response_class=HTMLResponse)
async def create_expense(
    request: Request,
    category_id: int = Form(...),
    amount: Decimal = Form(...),
    description: str = Form(...),
    expense_date: str = Form(...),
    payment_method: str = Form(...),
    receipt_number: Optional[str] = Form(None),
    supplier_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Create new expense."""
    try:
        # Convert date string to date object
        expense_date_obj = date.fromisoformat(expense_date)

        expense_in = ExpenseCreate(
            category_id=category_id,
            amount=amount,
            description=description,
            expense_date=expense_date_obj,
            payment_method=payment_method,
            receipt_number=receipt_number,
            supplier_name=supplier_name,
        )

        expense_service.register_expense(
            db, expense_in=expense_in, current_user=current_user
        )

        # Redirect to expense list with success message
        return HTMLResponse(
            content='<script>window.location.href="/expenses?success=Expense created successfully"</script>',
            status_code=200,
        )
    except ValueError as e:
        logger.error(f"Error creating expense: {e}")
        # Re-render form with error
        categories = expense_service.get_categories_for_dropdown(db)
        return templates.TemplateResponse(
            "expenses/expense_form.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": categories,
                "expense": None,
                "error": str(e),
            },
            status_code=400,
        )


@router.get("/expenses/{expense_id}/edit", response_class=HTMLResponse)
async def edit_expense_form(
    request: Request,
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render edit expense form."""
    from app.crud.expense import expense as expense_crud

    expense = expense_crud.get(db, id=expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # Check if expense is editable
    if not expense_crud.check_expense_editable(expense, current_user.id):
        return HTMLResponse(
            content='<div class="text-red-600">This expense can only be edited on the same day by the creator.</div>',
            status_code=403,
        )

    categories = expense_service.get_categories_for_dropdown(db)

    return templates.TemplateResponse(
        "expenses/expense_form.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": categories,
            "expense": expense,
        },
    )


@router.put("/expenses/{expense_id}", response_class=HTMLResponse)
async def update_expense(
    request: Request,
    expense_id: int,
    amount: Optional[Decimal] = Form(None),
    description: Optional[str] = Form(None),
    payment_method: Optional[str] = Form(None),
    receipt_number: Optional[str] = Form(None),
    supplier_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Update expense."""
    try:
        expense_in = ExpenseUpdate(
            amount=amount,
            description=description,
            payment_method=payment_method,
            receipt_number=receipt_number,
            supplier_name=supplier_name,
        )

        expense_service.update_expense(
            db, expense_id=expense_id, expense_in=expense_in, current_user=current_user
        )

        # Return success message
        return HTMLResponse(
            content='<script>window.location.href="/expenses?success=Expense updated successfully"</script>',
            status_code=200,
        )
    except ValueError as e:
        return HTMLResponse(
            content=f'<div class="text-red-600 text-sm mt-2">{str(e)}</div>',
            status_code=400,
        )


@router.get("/expenses/filter", response_class=HTMLResponse)
async def filter_expenses(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
):
    """Filter expenses (HTMX endpoint)."""
    # Parse filter parameters
    filters = ExpenseFilter()
    if date_from:
        try:
            filters.date_from = date.fromisoformat(date_from)
        except ValueError:
            pass
    if date_to:
        try:
            filters.date_to = date.fromisoformat(date_to)
        except ValueError:
            pass
    if category_id:
        filters.category_id = category_id
    if payment_method:
        filters.payment_method = payment_method

    # Get filtered expenses
    expenses = expense_service.get_expenses_with_filters(db, filters=filters, limit=100)

    # Calculate totals
    total_amount = sum(exp.amount for exp in expenses)

    return templates.TemplateResponse(
        "expenses/_expense_table.html",
        {
            "request": request,
            "current_user": current_user,
            "expenses": expenses,
            "total_amount": total_amount,
        },
    )


@router.post("/expenses/{expense_id}/receipt", response_class=HTMLResponse)
async def upload_receipt(
    request: Request,
    expense_id: int,
    receipt: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Upload receipt for expense."""
    import uuid
    from pathlib import Path

    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
        if receipt.content_type not in allowed_types:
            raise ValueError("Invalid file type. Only images and PDFs are allowed.")

        # Generate unique filename
        file_extension = Path(receipt.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Create upload directory if it doesn't exist
        upload_dir = Path("static/uploads/receipts")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = upload_dir / unique_filename
        with open(file_path, "wb") as f:
            content = await receipt.read()
            f.write(content)

        # Update expense with file path
        expense_service.handle_receipt_upload(
            db,
            expense_id=expense_id,
            file_path=str(file_path),
            current_user=current_user,
        )

        return HTMLResponse(
            content='<div class="text-green-600">Receipt uploaded successfully</div>',
            status_code=200,
        )
    except ValueError as e:
        return HTMLResponse(
            content=f'<div class="text-red-600">{str(e)}</div>',
            status_code=400,
        )
