"""Web routes for expense management."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import require_web_role
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.expense import ExpenseCategoryCreate, ExpenseCategoryUpdate
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
