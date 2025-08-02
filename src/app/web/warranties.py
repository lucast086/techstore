"""Web routes for warranty management (HTMX)."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.warranty import (
    WarrantyCheckRequest,
    WarrantyClaimCreate,
    WarrantySearchParams,
    WarrantyVoid,
)
from app.services.warranty_service import warranty_service

router = APIRouter(prefix="/warranties", tags=["warranties"])
templates = Jinja2Templates(directory="src/app/templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def warranty_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    q: Optional[str] = None,
) -> HTMLResponse:
    """Display warranty list page."""
    logger.info(f"User {current_user.id} viewing warranty list")

    params = WarrantySearchParams(page=page, q=q)
    warranties, total = warranty_service.search_warranties(db, params=params)

    # Calculate pagination
    total_pages = (total + params.page_size - 1) // params.page_size

    return templates.TemplateResponse(
        "warranties/list.html",
        {
            "request": request,
            "warranties": warranties,
            "current_page": page,
            "total_pages": total_pages,
            "total": total,
            "search_query": q or "",
            "user": current_user,
        },
    )


@router.get("/lookup", response_class=HTMLResponse)
async def warranty_lookup_form(
    request: Request,
    current_user: User = Depends(get_current_active_user),
) -> HTMLResponse:
    """Display warranty lookup form."""
    logger.info(f"User {current_user.id} viewing warranty lookup form")

    return templates.TemplateResponse(
        "warranties/lookup.html",
        {
            "request": request,
            "user": current_user,
        },
    )


@router.post("/check", response_class=HTMLResponse)
async def check_warranty(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    warranty_number: Optional[str] = Form(None),
    repair_number: Optional[str] = Form(None),
    customer_phone: Optional[str] = Form(None),
) -> HTMLResponse:
    """Check warranty and return results."""
    logger.info(f"User {current_user.id} checking warranty")

    try:
        check_request = WarrantyCheckRequest(
            warranty_number=warranty_number,
            repair_number=repair_number,
            customer_phone=customer_phone,
        )

        result = warranty_service.check_warranty(db, request=check_request)

        return templates.TemplateResponse(
            "warranties/partials/check_results.html",
            {
                "request": request,
                "result": result,
                "user": current_user,
            },
        )
    except ValueError as e:
        logger.error(f"Error checking warranty: {e}")
        return templates.TemplateResponse(
            "warranties/partials/error.html",
            {
                "request": request,
                "error": str(e),
            },
        )


@router.get("/{warranty_id}", response_class=HTMLResponse)
async def warranty_detail(
    request: Request,
    warranty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> HTMLResponse:
    """Display warranty details."""
    logger.info(f"User {current_user.id} viewing warranty {warranty_id}")

    try:
        warranty = warranty_service.get_warranty_details(db, warranty_id=warranty_id)

        return templates.TemplateResponse(
            "warranties/detail.html",
            {
                "request": request,
                "warranty": warranty,
                "user": current_user,
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warranty not found",
        ) from e


@router.get("/{warranty_id}/void-form", response_class=HTMLResponse)
async def void_warranty_form(
    request: Request,
    warranty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> HTMLResponse:
    """Display void warranty form."""
    logger.info(f"User {current_user.id} viewing void form for warranty {warranty_id}")

    try:
        warranty = warranty_service.get_warranty_details(db, warranty_id=warranty_id)

        return templates.TemplateResponse(
            "warranties/partials/void_form.html",
            {
                "request": request,
                "warranty": warranty,
                "user": current_user,
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warranty not found",
        ) from e


@router.post("/{warranty_id}/void", response_class=HTMLResponse)
async def void_warranty(
    request: Request,
    warranty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    void_reason: str = Form(...),
) -> HTMLResponse:
    """Void a warranty."""
    logger.info(f"User {current_user.id} voiding warranty {warranty_id}")

    try:
        void_data = WarrantyVoid(
            void_reason=void_reason,
            voided_by=current_user.id,
        )

        warranty = warranty_service.void_warranty(
            db,
            warranty_id=warranty_id,
            void_data=void_data,
        )

        return templates.TemplateResponse(
            "warranties/partials/warranty_status.html",
            {
                "request": request,
                "warranty": warranty,
                "user": current_user,
                "message": "Warranty voided successfully",
            },
        )
    except ValueError as e:
        logger.error(f"Error voiding warranty: {e}")
        return templates.TemplateResponse(
            "warranties/partials/error.html",
            {
                "request": request,
                "error": str(e),
            },
        )


@router.get("/{warranty_id}/claim-form", response_class=HTMLResponse)
async def warranty_claim_form(
    request: Request,
    warranty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> HTMLResponse:
    """Display warranty claim form."""
    logger.info(f"User {current_user.id} viewing claim form for warranty {warranty_id}")

    try:
        warranty = warranty_service.get_warranty_details(db, warranty_id=warranty_id)

        return templates.TemplateResponse(
            "warranties/claim.html",
            {
                "request": request,
                "warranty": warranty,
                "user": current_user,
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warranty not found",
        ) from e


@router.post("/{warranty_id}/claim", response_class=HTMLResponse)
async def create_warranty_claim(
    request: Request,
    warranty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    issue_description: str = Form(...),
    parts_covered: bool = Form(False),
    labor_covered: bool = Form(False),
) -> HTMLResponse:
    """Create a warranty claim."""
    logger.info(f"User {current_user.id} creating claim for warranty {warranty_id}")

    try:
        claim_data = WarrantyClaimCreate(
            warranty_id=warranty_id,
            issue_description=issue_description,
            parts_covered=parts_covered,
            labor_covered=labor_covered,
        )

        claim = warranty_service.create_warranty_claim(
            db,
            claim_data=claim_data,
            current_user_id=current_user.id,
        )

        return templates.TemplateResponse(
            "warranties/partials/claim_success.html",
            {
                "request": request,
                "claim": claim,
                "user": current_user,
            },
        )
    except ValueError as e:
        logger.error(f"Error creating warranty claim: {e}")
        return templates.TemplateResponse(
            "warranties/partials/error.html",
            {
                "request": request,
                "error": str(e),
            },
        )


@router.get("/terms", response_class=HTMLResponse)
async def warranty_terms(
    request: Request,
    current_user: User = Depends(get_current_active_user),
) -> HTMLResponse:
    """Display warranty terms and conditions."""
    logger.info(f"User {current_user.id} viewing warranty terms")

    return templates.TemplateResponse(
        "warranties/terms.html",
        {
            "request": request,
            "user": current_user,
        },
    )


@router.get("/statistics", response_class=HTMLResponse)
async def warranty_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> HTMLResponse:
    """Display warranty statistics."""
    logger.info(f"User {current_user.id} viewing warranty statistics")

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    stats = warranty_service.get_warranty_statistics(db)

    return templates.TemplateResponse(
        "warranties/statistics.html",
        {
            "request": request,
            "stats": stats,
            "user": current_user,
        },
    )
