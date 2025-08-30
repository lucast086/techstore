"""API endpoints for warranty management."""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.base import ResponseSchema
from app.schemas.warranty import (
    WarrantyCheckRequest,
    WarrantyCheckResponse,
    WarrantyClaimCreate,
    WarrantyClaimResponse,
    WarrantyClaimUpdate,
    WarrantyCreate,
    WarrantyListResponse,
    WarrantyResponse,
    WarrantySearchParams,
    WarrantyStatistics,
    WarrantyVoid,
)
from app.services.warranty_service import warranty_service

router = APIRouter(prefix="/warranties", tags=["warranties"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=ResponseSchema[WarrantyResponse])
def create_warranty(
    *,
    db: Session = Depends(get_db),
    warranty_in: WarrantyCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create warranty for a delivered repair."""
    logger.info(
        f"User {current_user.id} creating warranty for repair {warranty_in.repair_id}"
    )

    try:
        warranty = warranty_service.create_warranty_for_repair(
            db,
            repair_id=warranty_in.repair_id,
            warranty_data=warranty_in,
        )

        return ResponseSchema(
            success=True,
            data=warranty,
            message="Garantía creada exitosamente",
        )
    except ValueError as e:
        logger.error(f"Error creating warranty: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error creating warranty: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la garantía",
        ) from e


@router.get("/check", response_model=ResponseSchema[WarrantyCheckResponse])
def check_warranty(
    *,
    db: Session = Depends(get_db),
    warranty_number: Optional[str] = Query(None),
    repair_number: Optional[str] = Query(None),
    customer_phone: Optional[str] = Query(None),
) -> Any:
    """Check warranty validity by various criteria."""
    logger.info(
        f"Checking warranty - warranty: {warranty_number}, repair: {repair_number}, phone: {customer_phone}"
    )

    if not any([warranty_number, repair_number, customer_phone]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Al menos un parámetro de búsqueda es requerido",
        )

    try:
        request = WarrantyCheckRequest(
            warranty_number=warranty_number,
            repair_number=repair_number,
            customer_phone=customer_phone,
        )

        result = warranty_service.check_warranty(db, request=request)

        return ResponseSchema(
            success=True,
            data=result,
            message=result.message,
        )
    except Exception as e:
        logger.error(f"Error checking warranty: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar la garantía",
        ) from e


@router.get("/", response_model=ResponseSchema[list[WarrantyListResponse]])
def search_warranties(
    *,
    db: Session = Depends(get_db),
    params: WarrantySearchParams = Depends(),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Search warranties with filters."""
    logger.info(f"User {current_user.id} searching warranties with params: {params}")

    try:
        warranties, total = warranty_service.search_warranties(db, params=params)

        return ResponseSchema(
            success=True,
            data=warranties,
            message=f"Se han encontrado {total} garantías",
            meta={
                "total": total,
                "page": params.page,
                "page_size": params.page_size,
            },
        )
    except Exception as e:
        logger.error(f"Error searching warranties: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al buscar las garantías",
        ) from e


@router.get("/statistics", response_model=ResponseSchema[WarrantyStatistics])
def get_warranty_statistics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get warranty statistics."""
    logger.info(f"User {current_user.id} getting warranty statistics")

    try:
        stats = warranty_service.get_warranty_statistics(db)

        return ResponseSchema(
            success=True,
            data=stats,
            message="Estadísticas de garantías recuperadas exitosamente",
        )
    except Exception as e:
        logger.error(f"Error getting warranty statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las estadísticas de garantías",
        ) from e


@router.get("/{warranty_id}", response_model=ResponseSchema[WarrantyResponse])
def get_warranty(
    *,
    db: Session = Depends(get_db),
    warranty_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get warranty details."""
    logger.info(f"User {current_user.id} getting warranty {warranty_id}")

    try:
        warranty = warranty_service.get_warranty_details(db, warranty_id=warranty_id)

        return ResponseSchema(
            success=True,
            data=warranty,
            message="Detalles de garantía recuperados exitosamente",
        )
    except ValueError as e:
        logger.error(f"Warranty not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error getting warranty: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la garantía",
        ) from e


@router.put("/{warranty_id}/void", response_model=ResponseSchema[WarrantyResponse])
def void_warranty(
    *,
    db: Session = Depends(get_db),
    warranty_id: int,
    void_data: WarrantyVoid,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Void a warranty."""
    logger.info(f"User {current_user.id} voiding warranty {warranty_id}")

    # Set the current user as the one voiding
    void_data.voided_by = current_user.id

    try:
        warranty = warranty_service.void_warranty(
            db,
            warranty_id=warranty_id,
            void_data=void_data,
        )

        return ResponseSchema(
            success=True,
            data=warranty,
            message="Garantía anulada exitosamente",
        )
    except ValueError as e:
        logger.error(f"Error voiding warranty: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error voiding warranty: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al anular la garantía",
        ) from e


@router.post("/claims", response_model=ResponseSchema[WarrantyClaimResponse])
def create_warranty_claim(
    *,
    db: Session = Depends(get_db),
    claim_in: WarrantyClaimCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a warranty claim."""
    logger.info(f"User {current_user.id} creating warranty claim")

    try:
        claim = warranty_service.create_warranty_claim(
            db,
            claim_data=claim_in,
            current_user_id=current_user.id,
        )

        return ResponseSchema(
            success=True,
            data=claim,
            message="Warranty claim created successfully",
        )
    except ValueError as e:
        logger.error(f"Error creating warranty claim: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error creating warranty claim: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create warranty claim",
        ) from e


@router.put("/claims/{claim_id}", response_model=ResponseSchema[WarrantyClaimResponse])
def update_warranty_claim(
    *,
    db: Session = Depends(get_db),
    claim_id: int,
    claim_update: WarrantyClaimUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update a warranty claim."""
    logger.info(f"User {current_user.id} updating warranty claim {claim_id}")

    # Set the current user as approver if approving
    if claim_update.approved is not None:
        claim_update.approved_by = current_user.id

    try:
        claim = warranty_service.update_warranty_claim(
            db,
            claim_id=claim_id,
            claim_update=claim_update,
        )

        return ResponseSchema(
            success=True,
            data=claim,
            message="Warranty claim updated successfully",
        )
    except ValueError as e:
        logger.error(f"Error updating warranty claim: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error updating warranty claim: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update warranty claim",
        ) from e


@router.post("/update-expired", response_model=ResponseSchema[dict])
def update_expired_warranties(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update status of expired warranties (admin only)."""
    logger.info(f"User {current_user.id} updating expired warranties")

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    try:
        count = warranty_service.update_expired_warranties(db)

        return ResponseSchema(
            success=True,
            data={"updated": count},
            message=f"Updated {count} expired warranties",
        )
    except Exception as e:
        logger.error(f"Error updating expired warranties: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update expired warranties",
        ) from e
