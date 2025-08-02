"""Repair service for managing device repairs."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.repair import repair_crud
from app.models.repair import Repair, RepairPart, RepairPhoto
from app.schemas.repair import (
    RepairComplete,
    RepairCreate,
    RepairDeliver,
    RepairDiagnosis,
    RepairListResponse,
    RepairPartCreate,
    RepairPhotoCreate,
    RepairResponse,
    RepairSearchParams,
    RepairStatistics,
    RepairStatusHistoryResponse,
    RepairStatusUpdate,
    RepairUpdate,
)

logger = logging.getLogger(__name__)


class RepairService:
    """Service for handling repair management logic."""

    def create_repair(
        self, db: Session, repair_data: RepairCreate, user_id: int
    ) -> RepairResponse:
        """Create a new repair order.

        Args:
            db: Database session.
            repair_data: Repair details.
            user_id: ID of user creating the repair.

        Returns:
            Created repair with full details.
        """
        logger.info(
            f"Creating repair for customer {repair_data.customer_id} - "
            f"{repair_data.device_brand} {repair_data.device_model}"
        )

        # Create repair
        repair = repair_crud.create_repair(
            db=db, repair_in=repair_data, received_by_id=user_id
        )

        # Return with full details
        return self._format_repair_response(db, repair)

    def get_repair(self, db: Session, repair_id: int) -> Optional[RepairResponse]:
        """Get repair by ID with full details.

        Args:
            db: Database session.
            repair_id: Repair ID.

        Returns:
            Repair details or None if not found.
        """
        repair = repair_crud.get_repair(db, repair_id)
        if not repair:
            return None

        return self._format_repair_response(db, repair)

    def search_repairs(
        self, db: Session, params: RepairSearchParams
    ) -> tuple[list[RepairListResponse], int]:
        """Search repairs with filters.

        Args:
            db: Database session.
            params: Search parameters.

        Returns:
            Tuple of (repairs list, total count).
        """
        repairs, total = repair_crud.search_repairs(db, params=params)

        # Format list response
        repair_list = [
            RepairListResponse(
                id=repair.id,
                repair_number=repair.repair_number,
                customer_name=repair.customer.name,
                device_type=repair.device_type,
                device_brand=repair.device_brand,
                device_model=repair.device_model,
                status=repair.status,
                received_date=repair.received_date,
                estimated_completion=repair.estimated_completion,
                is_express=repair.is_express,
                technician_name=(
                    repair.technician.full_name if repair.technician else None
                ),
            )
            for repair in repairs
        ]

        return repair_list, total

    def update_repair(
        self, db: Session, repair_id: int, repair_data: RepairUpdate
    ) -> Optional[RepairResponse]:
        """Update repair details.

        Args:
            db: Database session.
            repair_id: Repair ID.
            repair_data: Update data.

        Returns:
            Updated repair or None if not found.
        """
        repair = repair_crud.update_repair(
            db=db, repair_id=repair_id, repair_in=repair_data
        )
        if not repair:
            return None

        logger.info(f"Updated repair {repair.repair_number}")
        return self._format_repair_response(db, repair)

    def add_diagnosis(
        self, db: Session, repair_id: int, diagnosis: RepairDiagnosis, user_id: int
    ) -> Optional[RepairResponse]:
        """Add diagnosis to repair.

        Args:
            db: Database session.
            repair_id: Repair ID.
            diagnosis: Diagnosis details.
            user_id: ID of technician adding diagnosis.

        Returns:
            Updated repair or None if not found.
        """
        repair = repair_crud.add_diagnosis(
            db=db, repair_id=repair_id, diagnosis=diagnosis, user_id=user_id
        )
        if not repair:
            return None

        logger.info(
            f"Added diagnosis to repair {repair.repair_number} - "
            f"Estimated cost: ${diagnosis.estimated_cost}"
        )
        return self._format_repair_response(db, repair)

    def update_status(
        self,
        db: Session,
        repair_id: int,
        status_update: RepairStatusUpdate,
        user_id: int,
    ) -> Optional[RepairResponse]:
        """Update repair status.

        Args:
            db: Database session.
            repair_id: Repair ID.
            status_update: Status update details.
            user_id: ID of user updating status.

        Returns:
            Updated repair or None if not found.

        Raises:
            ValueError: If status transition is invalid.
        """
        try:
            repair = repair_crud.update_status(
                db=db, repair_id=repair_id, status_update=status_update, user_id=user_id
            )
            if not repair:
                return None

            logger.info(
                f"Updated repair {repair.repair_number} status to {status_update.status}"
            )

            # TODO: Send WhatsApp notification for status change

            return self._format_repair_response(db, repair)
        except ValueError as e:
            logger.error(f"Invalid status transition: {e}")
            raise

    def complete_repair(
        self, db: Session, repair_id: int, completion: RepairComplete, user_id: int
    ) -> Optional[RepairResponse]:
        """Mark repair as completed.

        Args:
            db: Database session.
            repair_id: Repair ID.
            completion: Completion details.
            user_id: ID of technician completing repair.

        Returns:
            Updated repair or None if not found.

        Raises:
            ValueError: If repair is not in correct status.
        """
        try:
            repair = repair_crud.complete_repair(
                db=db, repair_id=repair_id, completion=completion, user_id=user_id
            )
            if not repair:
                return None

            logger.info(
                f"Completed repair {repair.repair_number} - "
                f"Final cost: ${completion.final_cost}"
            )

            # TODO: Send WhatsApp notification for completion

            return self._format_repair_response(db, repair)
        except ValueError as e:
            logger.error(f"Cannot complete repair: {e}")
            raise

    def deliver_repair(
        self, db: Session, repair_id: int, delivery: RepairDeliver
    ) -> Optional[RepairResponse]:
        """Mark repair as delivered.

        Args:
            db: Database session.
            repair_id: Repair ID.
            delivery: Delivery details.

        Returns:
            Updated repair or None if not found.

        Raises:
            ValueError: If repair is not ready for delivery.
        """
        try:
            repair = repair_crud.deliver_repair(
                db=db, repair_id=repair_id, delivery=delivery
            )
            if not repair:
                return None

            logger.info(f"Delivered repair {repair.repair_number}")

            # TODO: Send WhatsApp notification for delivery

            return self._format_repair_response(db, repair)
        except ValueError as e:
            logger.error(f"Cannot deliver repair: {e}")
            raise

    def add_part(
        self, db: Session, repair_id: int, part_data: RepairPartCreate
    ) -> Optional[RepairPart]:
        """Add part to repair.

        Args:
            db: Database session.
            repair_id: Repair ID.
            part_data: Part details.

        Returns:
            Created part or None if repair not found.
        """
        part = repair_crud.add_part(db=db, repair_id=repair_id, part_in=part_data)
        if part:
            logger.info(
                f"Added part {part_data.part_name} to repair {repair_id} - "
                f"Cost: ${part_data.part_cost}"
            )
        return part

    def remove_part(self, db: Session, part_id: int) -> bool:
        """Remove part from repair.

        Args:
            db: Database session.
            part_id: Part ID.

        Returns:
            True if removed, False if not found.
        """
        removed = repair_crud.remove_part(db=db, part_id=part_id)
        if removed:
            logger.info(f"Removed part {part_id}")
        return removed

    def add_photo(
        self, db: Session, repair_id: int, photo_data: RepairPhotoCreate, user_id: int
    ) -> Optional[RepairPhoto]:
        """Add photo to repair.

        Args:
            db: Database session.
            repair_id: Repair ID.
            photo_data: Photo details.
            user_id: ID of user uploading photo.

        Returns:
            Created photo or None if repair not found.
        """
        photo = repair_crud.add_photo(
            db=db, repair_id=repair_id, photo_in=photo_data, user_id=user_id
        )
        if photo:
            logger.info(f"Added photo to repair {repair_id}")
        return photo

    def get_statistics(self, db: Session) -> RepairStatistics:
        """Get repair statistics.

        Args:
            db: Database session.

        Returns:
            Repair statistics.
        """
        stats = repair_crud.get_repair_statistics(db)
        return RepairStatistics(**stats)

    def _format_repair_response(self, db: Session, repair: Repair) -> RepairResponse:
        """Format repair object into response schema.

        Args:
            db: Database session.
            repair: Repair model instance.

        Returns:
            Formatted repair response.
        """
        # Calculate amount due if repair has final cost
        amount_due = None
        if repair.final_cost:
            # TODO: Calculate based on payments received
            amount_due = repair.final_cost

        # Format status history
        status_history = [
            RepairStatusHistoryResponse(
                id=sh.id,
                repair_id=sh.repair_id,
                status=sh.status,
                notes=sh.notes,
                changed_by=sh.changed_by,
                created_at=sh.created_at,
                user_name=sh.user.full_name if sh.user else None,
            )
            for sh in repair.status_history
        ]

        # Create a dict with only the scalar fields from repair
        repair_data = {
            "id": repair.id,
            "repair_number": repair.repair_number,
            "customer_id": repair.customer_id,
            "device_type": repair.device_type,
            "device_brand": repair.device_brand,
            "device_model": repair.device_model,
            "serial_number": repair.serial_number,
            "problem_description": repair.problem_description,
            "device_condition": repair.device_condition,
            "accessories_received": repair.accessories_received,
            "status": repair.status,
            "diagnosis_notes": repair.diagnosis_notes,
            "repair_notes": repair.repair_notes,
            "estimated_cost": repair.estimated_cost,
            "final_cost": repair.final_cost,
            "labor_cost": repair.labor_cost,
            "parts_cost": repair.parts_cost,
            "received_date": repair.received_date,
            "estimated_completion": repair.estimated_completion,
            "completed_date": repair.completed_date,
            "delivered_date": repair.delivered_date,
            "warranty_days": repair.warranty_days,
            "warranty_expires": repair.warranty_expires,
            "assigned_technician": repair.assigned_technician,
            "received_by": repair.received_by,
            "delivered_by": repair.delivered_by,
            "is_express": repair.is_express,
            "customer_approved": repair.customer_approved,
            "approval_date": repair.approval_date,
            "created_at": repair.created_at,
            "updated_at": repair.updated_at,
        }

        return RepairResponse(
            **repair_data,
            customer_name=repair.customer.name,
            customer_phone=repair.customer.phone,
            technician_name=repair.technician.full_name if repair.technician else None,
            receiver_name=repair.receiver.full_name if repair.receiver else None,
            deliverer_name=repair.deliverer.full_name if repair.deliverer else None,
            parts=repair.parts,
            photos=repair.photos,
            status_history=status_history,
            amount_due=amount_due,
        )


# Create singleton instance
repair_service = RepairService()
