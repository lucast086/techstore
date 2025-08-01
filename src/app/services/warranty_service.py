"""Service layer for warranty management."""

import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.crud import repair_crud
from app.crud import warranty as warranty_crud
from app.models.warranty import Warranty, WarrantyClaim
from app.schemas.repair import RepairStatus
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

logger = logging.getLogger(__name__)


class WarrantyService:
    """Service for managing warranties."""

    def create_warranty_for_repair(
        self,
        db: Session,
        *,
        repair_id: int,
        warranty_data: Optional[WarrantyCreate] = None,
    ) -> WarrantyResponse:
        """Create warranty for a delivered repair."""
        logger.info(f"Creating warranty for repair {repair_id}")

        # Check if repair exists and is delivered
        repair = repair_crud.get_repair(db, repair_id=repair_id)
        if not repair:
            logger.error(f"Repair {repair_id} not found")
            raise ValueError("Repair not found")

        if repair.status != RepairStatus.DELIVERED.value:
            logger.error(f"Repair {repair_id} is not delivered")
            raise ValueError("Warranty can only be created for delivered repairs")

        # Check if warranty already exists
        existing = warranty_crud.warranty.get_by_repair_id(db, repair_id=repair_id)
        if existing:
            logger.error(f"Warranty already exists for repair {repair_id}")
            raise ValueError("Warranty already exists for this repair")

        # Create warranty with defaults if not provided
        if not warranty_data:
            warranty_data = WarrantyCreate(repair_id=repair_id)

        warranty = warranty_crud.warranty.create_warranty(
            db,
            repair_id=repair_id,
            warranty_create=warranty_data,
        )

        logger.info(
            f"Created warranty {warranty.warranty_number} for repair {repair_id}"
        )
        return self._build_warranty_response(warranty)

    def void_warranty(
        self,
        db: Session,
        *,
        warranty_id: int,
        void_data: WarrantyVoid,
    ) -> WarrantyResponse:
        """Void a warranty."""
        logger.info(f"Voiding warranty {warranty_id}")

        warranty = warranty_crud.warranty.void_warranty(
            db,
            warranty_id=warranty_id,
            void_data=void_data,
        )

        if not warranty:
            logger.error(f"Warranty {warranty_id} not found")
            raise ValueError("Warranty not found")

        logger.info(f"Voided warranty {warranty.warranty_number}")
        return self._build_warranty_response(warranty)

    def check_warranty(
        self,
        db: Session,
        *,
        request: WarrantyCheckRequest,
    ) -> WarrantyCheckResponse:
        """Check warranty validity."""
        logger.info(f"Checking warranty with params: {request}")

        warranties = warranty_crud.warranty.check_warranty(
            db,
            warranty_number=request.warranty_number,
            repair_number=request.repair_number,
            customer_phone=request.customer_phone,
        )

        if not warranties:
            return WarrantyCheckResponse(
                found=False,
                warranties=[],
                message="No warranty found with the provided information",
            )

        warranty_responses = [self._build_warranty_response(w) for w in warranties]

        return WarrantyCheckResponse(
            found=True,
            warranties=warranty_responses,
            message=f"Found {len(warranties)} warranty(ies)",
        )

    def search_warranties(
        self,
        db: Session,
        *,
        params: WarrantySearchParams,
    ) -> tuple[list[WarrantyListResponse], int]:
        """Search warranties with filters."""
        logger.info(f"Searching warranties with params: {params}")

        warranties, total = warranty_crud.warranty.search_warranties(
            db,
            params=params,
        )

        responses = [
            WarrantyListResponse(
                id=w.id,
                warranty_number=w.warranty_number,
                repair_number=w.repair.repair_number,
                customer_name=w.repair.customer.name,
                device_type=w.repair.device_type,
                status=w.status,
                start_date=w.start_date,
                parts_expiry_date=w.parts_expiry_date,
                labor_expiry_date=w.labor_expiry_date,
                is_valid=w.is_valid(),
            )
            for w in warranties
        ]

        return responses, total

    def get_warranty_details(
        self,
        db: Session,
        *,
        warranty_id: int,
    ) -> WarrantyResponse:
        """Get warranty details."""
        logger.info(f"Getting warranty details for {warranty_id}")

        warranty = warranty_crud.warranty.get(db, id=warranty_id)
        if not warranty:
            logger.error(f"Warranty {warranty_id} not found")
            raise ValueError("Warranty not found")

        return self._build_warranty_response(warranty)

    def create_warranty_claim(
        self,
        db: Session,
        *,
        claim_data: WarrantyClaimCreate,
        current_user_id: int,
    ) -> WarrantyClaimResponse:
        """Create a warranty claim."""
        logger.info(f"Creating warranty claim for warranty {claim_data.warranty_id}")

        # Validate warranty
        warranty = warranty_crud.warranty.get(db, id=claim_data.warranty_id)
        if not warranty:
            logger.error(f"Warranty {claim_data.warranty_id} not found")
            raise ValueError("Warranty not found")

        # Check warranty validity
        if not warranty.is_valid():
            logger.error(f"Warranty {warranty.warranty_number} is not valid")
            raise ValueError("Warranty has expired")

        # Check coverage
        if claim_data.parts_covered and not warranty.is_parts_valid():
            logger.error(f"Parts warranty has expired for {warranty.warranty_number}")
            raise ValueError("Parts warranty has expired")

        if claim_data.labor_covered and not warranty.is_labor_valid():
            logger.error(f"Labor warranty has expired for {warranty.warranty_number}")
            raise ValueError("Labor warranty has expired")

        # Create new repair for warranty claim
        repair_create = {
            "customer_id": warranty.repair.customer_id,
            "device_type": warranty.repair.device_type,
            "device_brand": warranty.repair.device_brand,
            "device_model": warranty.repair.device_model,
            "serial_number": warranty.repair.serial_number,
            "problem_description": f"WARRANTY CLAIM: {claim_data.issue_description}",
            "device_condition": f"Warranty claim for repair {warranty.repair.repair_number}",
            "received_by": current_user_id,
            "is_express": False,
        }

        from app.schemas.repair import RepairCreate

        repair_create_obj = RepairCreate(**repair_create)
        new_repair = repair_crud.create_repair(
            db, repair_in=repair_create_obj, received_by_id=current_user_id
        )

        # Create claim
        claim_data.approved_by = current_user_id
        claim = warranty_crud.warranty_claim.create_claim(
            db,
            claim_create=claim_data,
            repair_id=new_repair.id,
        )

        logger.info(f"Created warranty claim {claim.claim_number}")
        return self._build_claim_response(claim)

    def update_warranty_claim(
        self,
        db: Session,
        *,
        claim_id: int,
        claim_update: WarrantyClaimUpdate,
    ) -> WarrantyClaimResponse:
        """Update a warranty claim."""
        logger.info(f"Updating warranty claim {claim_id}")

        claim = warranty_crud.warranty_claim.update_claim(
            db,
            claim_id=claim_id,
            claim_update=claim_update,
        )

        if not claim:
            logger.error(f"Warranty claim {claim_id} not found")
            raise ValueError("Warranty claim not found")

        logger.info(f"Updated warranty claim {claim.claim_number}")
        return self._build_claim_response(claim)

    def get_warranty_statistics(
        self,
        db: Session,
    ) -> WarrantyStatistics:
        """Get warranty statistics."""
        logger.info("Getting warranty statistics")

        stats = warranty_crud.warranty.get_statistics(db)

        return WarrantyStatistics(**stats)

    def update_expired_warranties(
        self,
        db: Session,
    ) -> int:
        """Update status of expired warranties."""
        logger.info("Updating expired warranties")

        count = warranty_crud.warranty.update_expired_warranties(db)

        logger.info(f"Updated {count} expired warranties")
        return count

    def _build_warranty_response(self, warranty: Warranty) -> WarrantyResponse:
        """Build warranty response with computed fields."""
        today = date.today()

        return WarrantyResponse(
            id=warranty.id,
            repair_id=warranty.repair_id,
            warranty_number=warranty.warranty_number,
            coverage_type=warranty.coverage_type,
            parts_warranty_days=warranty.parts_warranty_days,
            labor_warranty_days=warranty.labor_warranty_days,
            status=warranty.status,
            start_date=warranty.start_date,
            parts_expiry_date=warranty.parts_expiry_date,
            labor_expiry_date=warranty.labor_expiry_date,
            void_reason=warranty.void_reason,
            voided_at=warranty.voided_at,
            voided_by=warranty.voided_by,
            terms=warranty.terms,
            exclusions=warranty.exclusions,
            created_at=warranty.created_at,
            updated_at=warranty.updated_at,
            repair_number=warranty.repair.repair_number,
            customer_name=warranty.repair.customer.name,
            device_type=warranty.repair.device_type,
            device_brand=warranty.repair.device_brand,
            device_model=warranty.repair.device_model,
            is_parts_valid=warranty.is_parts_valid(),
            is_labor_valid=warranty.is_labor_valid(),
            is_valid=warranty.is_valid(),
            days_remaining_parts=max(0, (warranty.parts_expiry_date - today).days),
            days_remaining_labor=max(0, (warranty.labor_expiry_date - today).days),
            voided_by_name=warranty.voided_by_user.full_name
            if warranty.voided_by_user
            else None,
        )

    def _build_claim_response(self, claim: WarrantyClaim) -> WarrantyClaimResponse:
        """Build warranty claim response."""
        return WarrantyClaimResponse(
            id=claim.id,
            warranty_id=claim.warranty_id,
            repair_id=claim.repair_id,
            claim_number=claim.claim_number,
            claim_date=claim.claim_date,
            issue_description=claim.issue_description,
            resolution_notes=claim.resolution_notes,
            parts_covered=claim.parts_covered,
            labor_covered=claim.labor_covered,
            approved=claim.approved,
            approved_by=claim.approved_by,
            approved_at=claim.approved_at,
            created_at=claim.created_at,
            updated_at=claim.updated_at,
            warranty_number=claim.warranty.warranty_number,
            repair_number=claim.repair.repair_number,
            customer_name=claim.repair.customer.name,
            approved_by_name=claim.approved_by_user.full_name
            if claim.approved_by_user
            else None,
        )


# Create service instance
warranty_service = WarrantyService()
