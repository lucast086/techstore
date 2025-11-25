"""Repair management API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.base import ResponseSchema
from app.schemas.repair import (
    RepairComplete,
    RepairCreate,
    RepairDeliver,
    RepairDiagnosis,
    RepairPartCreate,
    RepairPhotoCreate,
    RepairSearchParams,
    RepairStatus,
    RepairStatusUpdate,
    RepairUpdate,
)
from app.schemas.repair_deposit import (
    DepositCreate,
    DepositRefund,
)
from app.services.repair_deposit_service import repair_deposit_service
from app.services.repair_service import repair_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ResponseSchema)
async def create_repair(
    repair_in: RepairCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Create new repair order.

    - **customer_id**: Customer ID (required)
    - **device_type**: Type of device (phone, laptop, etc)
    - **device_brand**: Device manufacturer
    - **device_model**: Device model (optional)
    - **problem_description**: Description of the issue
    - **is_express**: Whether this is an express repair
    """
    try:
        repair = repair_service.create_repair(
            db=db, repair_data=repair_in, user_id=current_user.id
        )
        return ResponseSchema(
            success=True,
            message="Orden de reparación creada exitosamente",
            data=repair.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error creating repair: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la orden de reparación",
        ) from e


@router.get("/", response_model=ResponseSchema)
async def search_repairs(
    q: Optional[str] = Query(None, description="Search query"),
    status: Optional[RepairStatus] = Query(None, description="Filter by status"),
    technician_id: Optional[int] = Query(None, description="Filter by technician"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    device_brand: Optional[str] = Query(None, description="Filter by device brand"),
    is_express: Optional[bool] = Query(None, description="Filter express repairs"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Search and list repairs with filters."""
    params = RepairSearchParams(
        q=q,
        status=status,
        technician_id=technician_id,
        device_type=device_type,
        device_brand=device_brand,
        is_express=is_express,
        page=page,
        page_size=page_size,
    )

    repairs, total = repair_service.search_repairs(db=db, params=params)

    return ResponseSchema(
        success=True,
        data={
            "repairs": [repair.model_dump() for repair in repairs],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    )


@router.get("/statistics", response_model=ResponseSchema)
async def get_repair_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Get repair statistics dashboard data."""
    stats = repair_service.get_statistics(db=db)
    return ResponseSchema(
        success=True,
        data=stats.model_dump(),
    )


@router.get("/{repair_id}", response_model=ResponseSchema)
async def get_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Get repair details by ID."""
    repair = repair_service.get_repair(db=db, repair_id=repair_id)
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found",
        )

    return ResponseSchema(
        success=True,
        data=repair.model_dump(),
    )


@router.patch("/{repair_id}", response_model=ResponseSchema)
async def update_repair(
    repair_id: int,
    repair_update: RepairUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Update repair details."""
    repair = repair_service.update_repair(
        db=db, repair_id=repair_id, repair_data=repair_update
    )
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found",
        )

    return ResponseSchema(
        success=True,
        message="Reparación actualizada exitosamente",
        data=repair.model_dump(),
    )


@router.post("/{repair_id}/diagnosis", response_model=ResponseSchema)
async def add_diagnosis(
    repair_id: int,
    diagnosis: RepairDiagnosis,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Add diagnosis to repair.

    - **diagnosis_notes**: Technician's diagnosis
    - **estimated_cost**: Total estimated cost
    - **labor_cost**: Labor component
    - **parts_cost**: Parts component
    - **parts**: Optional list of parts needed
    """
    try:
        repair = repair_service.add_diagnosis(
            db=db, repair_id=repair_id, diagnosis=diagnosis, user_id=current_user.id
        )
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repair not found",
            )

        return ResponseSchema(
            success=True,
            message="Diagnóstico agregado exitosamente",
            data=repair.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/{repair_id}/status", response_model=ResponseSchema)
async def update_repair_status(
    repair_id: int,
    status_update: RepairStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Update repair status.

    Valid transitions:
    - received -> diagnosing, cancelled
    - diagnosing -> approved, cancelled, ready (express)
    - approved -> repairing, cancelled
    - repairing -> testing, ready, cancelled
    - testing -> ready, repairing, cancelled
    - ready -> delivered, repairing
    """
    try:
        repair = repair_service.update_status(
            db=db,
            repair_id=repair_id,
            status_update=status_update,
            user_id=current_user.id,
        )
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repair not found",
            )

        return ResponseSchema(
            success=True,
            message=f"Estado de reparación actualizado a {status_update.status}",
            data=repair.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/{repair_id}/complete", response_model=ResponseSchema)
async def complete_repair(
    repair_id: int,
    completion: RepairComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Mark repair as completed.

    - **final_cost**: Final repair cost
    - **repair_notes**: Notes about the repair work
    - **warranty_days**: Warranty period in days
    """
    try:
        repair = repair_service.complete_repair(
            db=db, repair_id=repair_id, completion=completion, user_id=current_user.id
        )
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repair not found",
            )

        return ResponseSchema(
            success=True,
            message="Reparación completada exitosamente",
            data=repair.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/{repair_id}/deliver", response_model=ResponseSchema)
async def deliver_repair(
    repair_id: int,
    delivery: RepairDeliver,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Mark repair as delivered.

    - **delivered_by**: User ID delivering the device
    - **customer_signature**: Optional signature data
    - **delivery_notes**: Optional delivery notes
    """
    try:
        # Override delivered_by with current user
        delivery.delivered_by = current_user.id

        repair = repair_service.deliver_repair(
            db=db, repair_id=repair_id, delivery=delivery
        )
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repair not found",
            )

        return ResponseSchema(
            success=True,
            message="Reparación entregada exitosamente",
            data=repair.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/{repair_id}/parts", response_model=ResponseSchema)
async def add_repair_part(
    repair_id: int,
    part: RepairPartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Add part to repair."""
    part_added = repair_service.add_part(db=db, repair_id=repair_id, part_data=part)
    if not part_added:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found",
        )

    return ResponseSchema(
        success=True,
        message="Parte agregada exitosamente",
        data={"part_id": part_added.id},
    )


@router.delete("/parts/{part_id}", response_model=ResponseSchema)
async def remove_repair_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Remove part from repair."""
    removed = repair_service.remove_part(db=db, part_id=part_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Part not found",
        )

    return ResponseSchema(
        success=True,
        message="Parte removida exitosamente",
    )


@router.post("/{repair_id}/photos", response_model=ResponseSchema)
async def add_repair_photo(
    repair_id: int,
    photo: RepairPhotoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Add photo to repair.

    Note: This endpoint expects a photo URL. In production,
    implement file upload to cloud storage first.
    """
    photo_added = repair_service.add_photo(
        db=db, repair_id=repair_id, photo_data=photo, user_id=current_user.id
    )
    if not photo_added:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair not found",
        )

    return ResponseSchema(
        success=True,
        message="Foto agregada exitosamente",
        data={"photo_id": photo_added.id},
    )


# ============= Deposit Management Endpoints =============


@router.post("/{repair_id}/deposits", response_model=ResponseSchema)
async def record_deposit(
    repair_id: int,
    deposit_in: DepositCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Record a new deposit for a repair.

    - **amount**: Deposit amount (required, must be positive)
    - **payment_method**: Payment method (cash, card, transfer, etc.)
    - **notes**: Optional notes about the deposit
    """
    try:
        # Override repair_id from URL
        deposit_in.repair_id = repair_id

        deposit = repair_deposit_service.record_deposit(
            db=db, deposit_data=deposit_in, received_by_id=current_user.id
        )

        return ResponseSchema(
            success=True,
            message=f"Deposit recorded successfully. Receipt: {deposit.receipt_number}",
            data=deposit.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error recording deposit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error recording deposit",
        ) from e


@router.get("/{repair_id}/deposits", response_model=ResponseSchema)
async def get_repair_deposits(
    repair_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Get all deposits for a repair with summary."""
    summary = repair_deposit_service.get_repair_deposits(db=db, repair_id=repair_id)

    return ResponseSchema(
        success=True,
        message=f"Found {summary.deposit_count} deposits",
        data=summary.model_dump(),
    )


@router.get("/deposits/{deposit_id}", response_model=ResponseSchema)
async def get_deposit(
    deposit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Get deposit details by ID."""
    deposit = repair_deposit_service.get_deposit(db=db, deposit_id=deposit_id)
    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found",
        )

    return ResponseSchema(
        success=True,
        message="Deposit retrieved successfully",
        data=deposit.model_dump(),
    )


@router.post("/deposits/{deposit_id}/refund", response_model=ResponseSchema)
async def refund_deposit(
    deposit_id: int,
    refund_data: DepositRefund,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Refund a deposit.

    - **refund_amount**: Amount to refund (optional, defaults to full amount)
    - **refund_reason**: Reason for refund (required)
    """
    try:
        deposit = repair_deposit_service.refund_deposit(
            db=db,
            deposit_id=deposit_id,
            refund_data=refund_data,
            refunded_by_id=current_user.id,
        )

        return ResponseSchema(
            success=True,
            message=f"Deposit {deposit.receipt_number} refunded successfully",
            data=deposit.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error refunding deposit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing refund",
        ) from e


@router.post("/deposits/{deposit_id}/void", response_model=ResponseSchema)
async def void_deposit(
    deposit_id: int,
    reason: str = Query(..., description="Reason for voiding"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Void a deposit.

    Only active deposits can be voided.
    """
    try:
        deposit = repair_deposit_service.void_deposit(
            db=db,
            deposit_id=deposit_id,
            reason=reason,
            voided_by_id=current_user.id,
        )

        return ResponseSchema(
            success=True,
            message=f"Deposit {deposit.receipt_number} voided successfully",
            data=deposit.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error voiding deposit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error voiding deposit",
        ) from e


@router.post("/{repair_id}/deposits/apply-to-sale", response_model=ResponseSchema)
async def apply_deposits_to_sale(
    repair_id: int,
    sale_id: int = Query(..., description="Sale ID to apply deposits to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Apply all active deposits of a repair to a sale.

    This is typically done when converting a repair to a sale.
    """
    try:
        deposits = repair_deposit_service.apply_deposits_to_sale(
            db=db, repair_id=repair_id, sale_id=sale_id
        )

        return ResponseSchema(
            success=True,
            message=f"Applied {len(deposits)} deposits to sale {sale_id}",
            data={"deposits": [d.model_dump() for d in deposits]},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error applying deposits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error applying deposits to sale",
        ) from e
