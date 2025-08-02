"""Cash closing management web routes for HTMX interface."""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.crud.cash_closing import cash_closing
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.cash_closing import CashClosingCreate
from app.services.cash_closing_service import cash_closing_service

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/app/templates")


def require_admin_or_manager(
    current_user: User = Depends(get_current_user_from_cookie)
) -> User:
    """Require Admin or Manager role for cash closing operations."""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only Admin and Manager roles can access cash closing operations",
        )
    return current_user


@router.get("/", response_class=HTMLResponse)
async def cash_closing_list(
    request: Request,
    page: int = Query(1, ge=1),
    message: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """Render cash closing list page."""
    try:
        # Get recent closings for display
        closings = cash_closing_service.get_recent_closings(db=db, limit=20)

        # Get current status for today
        today_status = cash_closing_service.get_current_closing_status(db=db)

        # Prepare alert message if needed
        alert_message = None
        alert_type = None
        if message == "open_required":
            alert_message = "You must open the cash register before processing sales."
            alert_type = "warning"

        return templates.TemplateResponse(
            "cash_closings/list.html",
            {
                "request": request,
                "current_user": current_user,
                "closings": closings,
                "today_status": today_status,
                "alert_message": alert_message,
                "alert_type": alert_type,
                "page_title": "Cash Closings",
            },
        )
    except Exception as e:
        logger.error(f"Error in cash closing list: {e}")
        raise HTTPException(status_code=500, detail="Failed to load cash closings")


@router.get("/open", response_class=HTMLResponse)
async def cash_opening_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """Render cash opening form."""
    try:
        # Check if already open for today
        today = date.today()
        if cash_closing.is_cash_register_open(db, target_date=today):
            # Redirect to list if already open
            return RedirectResponse(url="/cash-closings", status_code=302)

        # Get last closing for opening balance
        last_closing = cash_closing.get_last_closing(db)
        suggested_balance = last_closing.cash_count if last_closing else Decimal("0.00")

        return templates.TemplateResponse(
            "cash_closings/open.html",
            {
                "request": request,
                "current_user": current_user,
                "opening_date": today,
                "suggested_balance": suggested_balance,
                "page_title": "Open Cash Register",
            },
        )
    except Exception as e:
        logger.error(f"Error in cash opening form: {e}")
        raise HTTPException(status_code=500, detail="Failed to load opening form")


@router.post("/open", response_class=HTMLResponse)
async def open_cash_register(
    request: Request,
    opening_balance: Decimal = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """Open cash register for the day."""
    try:
        today = date.today()

        # Open the cash register
        opening = cash_closing_service.open_cash_register(
            db=db,
            opening_date=today,
            opening_balance=opening_balance,
            user_id=current_user.id,
        )

        # Update notes if provided
        if notes:
            db_opening = cash_closing.get(db, opening.id)
            db_opening.notes = f"Opening notes: {notes}"
            db.commit()

        # Redirect to list with success message
        return templates.TemplateResponse(
            "cash_closings/opened.html",
            {
                "request": request,
                "current_user": current_user,
                "opening": opening,
            },
        )
    except ValueError as e:
        logger.error(f"ValueError opening cash register: {e}")
        error_message = str(e) if str(e) else "Failed to open cash register"
        return templates.TemplateResponse(
            "cash_closings/open.html",
            {
                "request": request,
                "current_user": current_user,
                "error": error_message,
                "opening_date": date.today(),
                "opening_balance": opening_balance,
                "notes": notes,
                "suggested_balance": opening_balance,
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error opening cash register: {e}", exc_info=True)
        return templates.TemplateResponse(
            "cash_closings/open.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"System error: {str(e)}",
                "opening_date": date.today(),
                "opening_balance": opening_balance,
                "notes": notes,
                "suggested_balance": opening_balance,
            },
        )


@router.get("/new", response_class=HTMLResponse)
async def cash_closing_form(
    request: Request,
    closing_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """Render cash closing form page."""
    try:
        # Use today's date if none provided
        target_date = date.fromisoformat(closing_date) if closing_date else date.today()

        # Get current status and daily summary
        status_info = cash_closing_service.get_current_closing_status(
            db=db, target_date=target_date
        )

        # If closing already exists AND is finalized, redirect to view it
        if (
            status_info["has_closing"]
            and status_info["closing"]
            and status_info["closing"].is_finalized
        ):
            return RedirectResponse(
                url=f"/cash-closings/{target_date}",
                status_code=302,
            )

        return templates.TemplateResponse(
            "cash_closings/form.html",
            {
                "request": request,
                "current_user": current_user,
                "status_info": status_info,
                "closing_date": target_date,
                "page_title": f"Cash Closing - {target_date}",
            },
        )
    except ValueError as e:
        logger.error(f"Error in cash closing form: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in cash closing form: {e}")
        raise HTTPException(status_code=500, detail="Failed to load closing form")


@router.post("/", response_class=HTMLResponse)
async def create_cash_closing(
    request: Request,
    closing_date: str = Form(...),
    opening_balance: Decimal = Form(...),
    cash_count: Decimal = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """Create new cash closing."""
    # Parse date first to ensure we have a valid date object
    try:
        target_date = date.fromisoformat(closing_date)
    except ValueError:
        # If date parsing fails, return to form with error
        return templates.TemplateResponse(
            "cash_closings/form.html",
            {
                "request": request,
                "current_user": current_user,
                "error": "Invalid date format. Please use YYYY-MM-DD format.",
                "closing_date": date.today(),  # Default to today
                "opening_balance": opening_balance,
                "cash_count": cash_count,
                "notes": notes,
                "status_info": cash_closing_service.get_current_closing_status(db=db),
            },
        )

    try:
        # Create closing data
        closing_data = CashClosingCreate(
            closing_date=target_date,
            opening_balance=opening_balance,
            cash_count=cash_count,
            notes=notes,
        )

        # Create the closing
        closing = cash_closing_service.create_closing(
            db=db, closing_data=closing_data, user_id=current_user.id
        )

        # Check for cash difference warnings
        is_valid, warning = cash_closing_service.validate_cash_difference(
            closing.cash_difference
        )

        # Return success response with closing details
        return templates.TemplateResponse(
            "cash_closings/closing_created.html",
            {
                "request": request,
                "current_user": current_user,
                "closing": closing,
                "warning": warning if warning else None,
                "is_valid": is_valid,
            },
        )
    except ValueError as e:
        logger.error(f"Error creating closing: {e}")
        # Return error response
        return templates.TemplateResponse(
            "cash_closings/form.html",
            {
                "request": request,
                "current_user": current_user,
                "error": str(e),
                "closing_date": target_date,  # Use the parsed date object
                "opening_balance": opening_balance,
                "cash_count": cash_count,
                "notes": notes,
                "status_info": cash_closing_service.get_current_closing_status(
                    db=db, target_date=target_date
                ),
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error creating closing: {e}")
        raise HTTPException(status_code=500, detail="Failed to create closing")


@router.get("/{closing_date}", response_class=HTMLResponse)
async def view_cash_closing(
    request: Request,
    closing_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """View specific cash closing."""
    try:
        # Parse date
        target_date = date.fromisoformat(closing_date)

        # Get closing
        closing = cash_closing_service.get_closing_by_date(
            db=db, closing_date=target_date
        )

        if not closing:
            raise HTTPException(
                status_code=404, detail=f"No closing found for {target_date}"
            )

        return templates.TemplateResponse(
            "cash_closings/detail.html",
            {
                "request": request,
                "current_user": current_user,
                "closing": closing,
                "page_title": f"Cash Closing - {target_date}",
            },
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing closing: {e}")
        raise HTTPException(status_code=500, detail="Failed to load closing")


@router.post("/{closing_id}/finalize", response_class=HTMLResponse)
async def finalize_cash_closing(
    request: Request,
    closing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """Finalize cash closing."""
    try:
        # Finalize the closing
        finalized_closing = cash_closing_service.finalize_closing(
            db=db, closing_id=closing_id, user_id=current_user.id
        )

        # Return success response
        return templates.TemplateResponse(
            "cash_closings/finalized.html",
            {
                "request": request,
                "current_user": current_user,
                "closing": finalized_closing,
            },
        )
    except ValueError as e:
        logger.error(f"Error finalizing closing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error finalizing closing: {e}")
        raise HTTPException(status_code=500, detail="Failed to finalize closing")


# HTMX endpoints for dynamic updates
@router.get("/htmx/daily-summary", response_class=HTMLResponse)
async def get_daily_summary_htmx(
    request: Request,
    target_date: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """Get daily summary for HTMX update."""
    try:
        # Parse date
        parsed_date = date.fromisoformat(target_date)

        # Get daily summary
        daily_summary = cash_closing_service.calculate_daily_totals(
            db=db, target_date=parsed_date
        )

        # Get opening balance
        last_closing = cash_closing.get_last_closing(db)
        opening_balance = last_closing.cash_count if last_closing else Decimal("0.00")

        return templates.TemplateResponse(
            "cash_closings/_daily_summary.html",
            {
                "request": request,
                "daily_summary": daily_summary,
                "opening_balance": opening_balance,
                "target_date": parsed_date,
            },
        )
    except ValueError:
        return HTMLResponse("<div class='text-red-500'>Invalid date format</div>")
    except Exception as e:
        logger.error(f"Error getting daily summary: {e}")
        return HTMLResponse("<div class='text-red-500'>Error loading summary</div>")


@router.get("/htmx/cash-calculation", response_class=HTMLResponse)
async def calculate_cash_difference_htmx(
    request: Request,
    opening_balance: Decimal = Query(...),
    sales_total: Decimal = Query(...),
    expenses_total: Decimal = Query(0),
    cash_count: Decimal = Query(...),
    current_user: User = Depends(require_admin_or_manager),
):
    """Calculate cash difference for HTMX update."""
    try:
        # Calculate expected cash and difference
        expected_cash = opening_balance + sales_total - expenses_total
        cash_difference = cash_count - expected_cash

        # Validate difference
        is_valid, warning = cash_closing_service.validate_cash_difference(
            cash_difference
        )

        return templates.TemplateResponse(
            "cash_closings/_cash_calculation.html",
            {
                "request": request,
                "expected_cash": expected_cash,
                "cash_difference": cash_difference,
                "is_valid": is_valid,
                "warning": warning,
            },
        )
    except Exception as e:
        logger.error(f"Error calculating cash difference: {e}")
        return HTMLResponse("<div class='text-red-500'>Calculation error</div>")
