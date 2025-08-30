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
