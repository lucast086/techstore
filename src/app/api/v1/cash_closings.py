"""Cash closing management API endpoints."""

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.base import ResponseSchema
from app.schemas.cash_closing import (
    CashClosingCreate,
)
from app.services.cash_closing_service import cash_closing_service
from app.services.pdf_service import pdf_service

logger = logging.getLogger(__name__)
router = APIRouter()


def require_admin_or_manager(current_user: User = Depends(get_current_user)) -> User:
    """Require Admin or Manager role for cash closing operations."""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin and Manager roles can access cash closing operations",
        )
    return current_user


@router.post("/start", response_model=ResponseSchema)
async def start_daily_closing(
    closing_date: Optional[date] = Query(
        None, description="Date for closing (default: today)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> ResponseSchema:
    """Initialize daily closing process.

    - **closing_date**: Date for closing (optional, defaults to today)

    Returns daily summary and opening balance to populate closing form.
    """
    try:
        target_date = closing_date or date.today()

        daily_summary, opening_balance = cash_closing_service.start_daily_closing(
            db=db, closing_date=target_date, user_id=current_user.id
        )

        return ResponseSchema(
            success=True,
            message="Cierre diario inicializado exitosamente",
            data={
                "daily_summary": daily_summary,
                "opening_balance": opening_balance,
                "closing_date": target_date,
            },
        )
    except ValueError as e:
        logger.error(f"Error starting daily closing: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error starting daily closing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start daily closing",
        )


@router.get("/current", response_model=ResponseSchema)
async def get_current_closing_status(
    target_date: Optional[date] = Query(
        None, description="Date to check (default: today)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> ResponseSchema:
    """Get current closing status for today or specified date.

    - **target_date**: Date to check status for (optional, defaults to today)

    Returns closing status, daily summary, and whether closing can be created.
    """
    try:
        status_info = cash_closing_service.get_current_closing_status(
            db=db, target_date=target_date
        )

        return ResponseSchema(
            success=True,
            message="Estado de cierre recuperado exitosamente",
            data=status_info,
        )
    except Exception as e:
        logger.error(f"Error getting closing status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get closing status",
        )


@router.post("/", response_model=ResponseSchema)
async def create_closing(
    closing_in: CashClosingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> ResponseSchema:
    """Create new cash closing record.

    - **closing_date**: Date of the closing
    - **opening_balance**: Starting cash amount
    - **cash_count**: Actual cash counted at closing
    - **notes**: Optional closing notes
    """
    try:
        closing = cash_closing_service.create_closing(
            db=db, closing_data=closing_in, user_id=current_user.id
        )

        # Check if cash difference is within threshold
        is_valid, warning = cash_closing_service.validate_cash_difference(
            closing.cash_difference
        )

        return ResponseSchema(
            success=True,
            message="Cierre de caja creado exitosamente"
            + (f" - Warning: {warning}" if warning else ""),
            data={
                "closing": closing,
                "cash_difference_warning": warning if warning else None,
            },
        )
    except ValueError as e:
        logger.error(f"Error creating closing: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error creating closing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create closing",
        )


@router.put("/{closing_id}", response_model=ResponseSchema)
async def update_closing(
    closing_id: int,
    closing_update: CashClosingCreate,  # Use same schema for updates
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> ResponseSchema:
    """Update draft closing record.

    - **closing_id**: ID of closing to update
    - **closing_update**: Updated closing data

    Only draft closings (not finalized) can be updated.
    """
    try:
        # Get existing closing to verify it exists and is not finalized
        existing_closing = cash_closing_service.cash_closing.get(db, closing_id)
        if not existing_closing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Closing with ID {closing_id} not found",
            )

        if existing_closing.is_finalized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update finalized closing",
            )

        # Create new closing with updated data (delete old one first)
        cash_closing_service.cash_closing.remove(db, id=closing_id)
        updated_closing = cash_closing_service.create_closing(
            db=db, closing_data=closing_update, user_id=current_user.id
        )

        return ResponseSchema(
            success=True,
            message="Cierre de caja actualizado exitosamente",
            data={"closing": updated_closing},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating closing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update closing",
        )


@router.post("/{closing_id}/finalize", response_model=ResponseSchema)
async def finalize_closing(
    closing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> ResponseSchema:
    """Finalize closing record, making it immutable.

    - **closing_id**: ID of closing to finalize

    Once finalized, closing cannot be modified and prevents further sales for that date.
    """
    try:
        finalized_closing = cash_closing_service.finalize_closing(
            db=db, closing_id=closing_id, user_id=current_user.id
        )

        return ResponseSchema(
            success=True,
            message="Cierre de caja finalizado exitosamente",
            data={"closing": finalized_closing},
        )
    except ValueError as e:
        logger.error(f"Error finalizing closing: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error finalizing closing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to finalize closing",
        )


@router.get("/{closing_date}", response_model=ResponseSchema)
async def get_closing_by_date(
    closing_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> ResponseSchema:
    """Get closing record for specific date.

    - **closing_date**: Date to retrieve closing for (YYYY-MM-DD format)
    """
    try:
        closing = cash_closing_service.get_closing_by_date(
            db=db, closing_date=closing_date
        )

        if not closing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No closing found for date {closing_date}",
            )

        return ResponseSchema(
            success=True,
            message="Cierre recuperado exitosamente",
            data={"closing": closing},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting closing by date: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get closing",
        )


@router.get("/", response_model=ResponseSchema)
async def get_recent_closings(
    limit: int = Query(10, ge=1, le=100, description="Number of closings to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> ResponseSchema:
    """Get recent finalized closings.

    - **limit**: Maximum number of closings to return (1-100, default: 10)
    """
    try:
        closings = cash_closing_service.get_recent_closings(db=db, limit=limit)

        return ResponseSchema(
            success=True,
            message=f"Se han recuperado {len(closings)} cierres recientes",
            data={"closings": closings, "total": len(closings)},
        )
    except Exception as e:
        logger.error(f"Error getting recent closings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recent closings",
        )


@router.get("/check-sales", response_model=ResponseSchema)
async def check_can_process_sale(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Any authenticated user can check
) -> ResponseSchema:
    """Check if sales can be processed for current business day.

    Uses business day logic with midnight cutoff to determine which register should be used.

    Returns whether sales are allowed and reason if not.
    """
    try:
        from app.utils.timezone import get_cash_register_business_day

        can_process, reason = cash_closing_service.check_can_process_sale(db=db)
        business_day = get_cash_register_business_day()

        return ResponseSchema(
            success=True,
            message="Procesamiento de venta completado",
            data={
                "can_process_sale": can_process,
                "reason": reason if reason else "Sales can be processed for this date",
                "date": business_day,
            },
        )
    except Exception as e:
        logger.error(f"Error checking sale processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar el estado de procesamiento de venta",
        )


@router.get("/{closing_id}/pdf")
async def download_closing_pdf(
    closing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> Response:
    """Download PDF document for cash closing.

    - **closing_id**: ID of closing to generate PDF for

    Returns PDF file for download.
    """
    try:
        # Get closing with user relationship
        closing = cash_closing_service.cash_closing.get(db, closing_id)
        if not closing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Closing with ID {closing_id} not found",
            )

        # Generate PDF
        pdf_bytes = pdf_service.generate_cash_closing_pdf(closing)

        # Return PDF response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=cash_closing_{closing.closing_date}_{closing_id}.pdf"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF for closing {closing_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF",
        )
