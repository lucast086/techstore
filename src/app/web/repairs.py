"""Repair management web routes for HTMX interface."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.repair import (
    RepairCreate,
    RepairDiagnosis,
    RepairSearchParams,
    RepairStatus,
    RepairStatusUpdate,
)
from app.services.repair_service import repair_service

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/", response_class=HTMLResponse)
async def repair_list(
    request: Request,
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render repair list page."""
    # Convert status string to enum if provided
    status_filter = None
    if status:
        try:
            status_filter = RepairStatus(status)
        except ValueError:
            status_filter = None

    params = RepairSearchParams(
        q=q,
        status=status_filter,
        page=page,
        page_size=20,
    )

    repairs, total = repair_service.search_repairs(db=db, params=params)

    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "Repairs",
        "repairs": repairs,
        "total": total,
        "page": page,
        "page_size": 20,
        "total_pages": (total + 19) // 20,
        "search_query": q,
        "status_filter": status,
        "repair_statuses": [s.value for s in RepairStatus],
    }

    return templates.TemplateResponse("repairs/list.html", context)


@router.get("/new", response_class=HTMLResponse)
async def new_repair_form(
    request: Request,
    customer_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render new repair form."""
    from app.models.customer import Customer
    from app.models.user import User as TechUser

    # Get all customers for dropdown
    customers = (
        db.query(Customer)
        .filter(Customer.is_active.is_(True))
        .order_by(Customer.name)
        .all()
    )

    # Get all technicians (users)
    technicians = db.query(TechUser).filter(TechUser.is_active.is_(True)).all()

    # Preselect customer if ID provided
    selected_customer = None
    if customer_id:
        selected_customer = (
            db.query(Customer).filter(Customer.id == customer_id).first()
        )

    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "New Repair",
        "customers": customers,
        "technicians": technicians,
        "selected_customer": selected_customer,
    }

    return templates.TemplateResponse("repairs/new.html", context)


@router.post("/", response_class=HTMLResponse)
async def create_repair(
    request: Request,
    customer_id: int = Form(...),
    device_type: str = Form(...),
    device_brand: str = Form(...),
    device_model: Optional[str] = Form(None),
    serial_number: Optional[str] = Form(None),
    problem_description: str = Form(...),
    device_condition: Optional[str] = Form(None),
    accessories_received: Optional[str] = Form(None),
    estimated_completion: Optional[str] = Form(None),
    warranty_days: int = Form(30),
    is_express: bool = Form(False),
    assigned_technician: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Create new repair order."""
    try:
        # Parse estimated completion date if provided
        estimated_date = None
        if estimated_completion:
            try:
                estimated_date = datetime.strptime(
                    estimated_completion, "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        repair_data = RepairCreate(
            customer_id=customer_id,
            device_type=device_type,
            device_brand=device_brand,
            device_model=device_model,
            serial_number=serial_number,
            problem_description=problem_description,
            device_condition=device_condition,
            accessories_received=accessories_received,
            estimated_completion=estimated_date,
            warranty_days=warranty_days,
            is_express=is_express,
            assigned_technician=assigned_technician,
        )

        repair = repair_service.create_repair(
            db=db, repair_data=repair_data, user_id=current_user.id
        )

        # Redirect to repair detail page
        return RedirectResponse(url=f"/repairs/{repair.id}", status_code=302)

    except ValueError as e:
        # Return error in HTMX format
        return HTMLResponse(
            content=f'<div class="bg-red-50 text-red-700 p-4 rounded">{str(e)}</div>',
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error creating repair: {e}")
        return HTMLResponse(
            content='<div class="bg-red-50 text-red-700 p-4 rounded">Error creating repair</div>',
            status_code=500,
        )


@router.get("/{repair_id}", response_class=HTMLResponse)
async def repair_detail(
    request: Request,
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render repair detail page."""
    repair = repair_service.get_repair(db=db, repair_id=repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    # Get all technicians for assignment
    from app.models.user import User as TechUser

    technicians = db.query(TechUser).filter(TechUser.is_active.is_(True)).all()

    context = {
        "request": request,
        "current_user": current_user,
        "page_title": f"Repair {repair.repair_number}",
        "repair": repair,
        "technicians": technicians,
        "repair_statuses": [s.value for s in RepairStatus],
    }

    return templates.TemplateResponse("repairs/detail.html", context)


@router.post("/{repair_id}/status", response_class=HTMLResponse)
async def update_repair_status_htmx(
    request: Request,
    repair_id: int,
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Update repair status (HTMX endpoint)."""
    try:
        status_enum = RepairStatus(status)
        status_update = RepairStatusUpdate(status=status_enum, notes=notes)

        repair = repair_service.update_status(
            db=db,
            repair_id=repair_id,
            status_update=status_update,
            user_id=current_user.id,
        )

        if not repair:
            return HTMLResponse(
                content='<div class="bg-red-50 text-red-700 p-4 rounded">Repair not found</div>',
                status_code=404,
            )

        # Return updated status badge
        status_colors = {
            "received": "bg-gray-100 text-gray-800",
            "diagnosing": "bg-blue-100 text-blue-800",
            "approved": "bg-green-100 text-green-800",
            "repairing": "bg-yellow-100 text-yellow-800",
            "testing": "bg-purple-100 text-purple-800",
            "ready": "bg-green-100 text-green-800",
            "delivered": "bg-gray-100 text-gray-800",
            "cancelled": "bg-red-100 text-red-800",
        }

        color_class = status_colors.get(
            repair.status.value, "bg-gray-100 text-gray-800"
        )

        return HTMLResponse(
            content=f"""
            <div class="flex items-center space-x-2">
                <span class="px-3 py-1 text-sm font-medium rounded-full {color_class}">
                    {repair.status.value.title()}
                </span>
                <span class="text-sm text-green-600">Updated!</span>
            </div>
            """
        )

    except ValueError as e:
        return HTMLResponse(
            content=f'<div class="bg-red-50 text-red-700 p-4 rounded">{str(e)}</div>',
            status_code=400,
        )


@router.get("/{repair_id}/diagnosis", response_class=HTMLResponse)
async def diagnosis_form(
    request: Request,
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render diagnosis form."""
    repair = repair_service.get_repair(db=db, repair_id=repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    context = {
        "request": request,
        "current_user": current_user,
        "repair": repair,
    }

    return templates.TemplateResponse("repairs/partials/diagnosis_form.html", context)


@router.post("/{repair_id}/diagnosis", response_class=HTMLResponse)
async def add_diagnosis_htmx(
    request: Request,
    repair_id: int,
    diagnosis_notes: str = Form(...),
    labor_cost: Decimal = Form(...),
    parts_cost: Decimal = Form(Decimal("0")),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Add diagnosis to repair (HTMX endpoint)."""
    try:
        estimated_cost = labor_cost + parts_cost

        diagnosis = RepairDiagnosis(
            diagnosis_notes=diagnosis_notes,
            estimated_cost=estimated_cost,
            labor_cost=labor_cost,
            parts_cost=parts_cost,
        )

        repair = repair_service.add_diagnosis(
            db=db, repair_id=repair_id, diagnosis=diagnosis, user_id=current_user.id
        )

        if not repair:
            return HTMLResponse(
                content='<div class="bg-red-50 text-red-700 p-4 rounded">Repair not found</div>',
                status_code=404,
            )

        # Return success message and updated diagnosis section
        return HTMLResponse(
            content=f"""
            <div class="bg-green-50 text-green-700 p-4 rounded mb-4">
                Diagnosis added successfully
            </div>
            <div class="prose max-w-none">
                <p class="font-semibold">Diagnosis:</p>
                <p>{repair.diagnosis_notes}</p>
                <p class="mt-2">
                    <span class="font-semibold">Estimated Cost:</span>
                    ${repair.estimated_cost}
                    (Labor: ${repair.labor_cost}, Parts: ${repair.parts_cost})
                </p>
            </div>
            """
        )

    except ValueError as e:
        return HTMLResponse(
            content=f'<div class="bg-red-50 text-red-700 p-4 rounded">{str(e)}</div>',
            status_code=400,
        )


@router.get("/{repair_id}/receipt", response_class=HTMLResponse)
async def repair_receipt(
    request: Request,
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render repair receipt."""
    repair = repair_service.get_repair(db=db, repair_id=repair_id)
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    # Get company info (mock for now)
    company = {
        "name": "TechStore",
        "address": "123 Main St, City, State 12345",
        "phone": "(555) 123-4567",
        "email": "info@techstore.com",
        "tax_id": "12-3456789",
    }

    context = {
        "request": request,
        "current_user": current_user,
        "page_title": f"Receipt - {repair.repair_number}",
        "repair": repair,
        "company": company,
    }

    return templates.TemplateResponse("repairs/receipt.html", context)
