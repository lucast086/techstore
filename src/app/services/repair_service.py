"""Repair service for managing device repairs."""

import logging
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.crud.repair import repair_crud
from app.models.repair import Repair, RepairPart, RepairPhoto
from app.models.repair_deposit import DepositStatus, RepairDeposit
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
from app.utils.timezone import get_local_today

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
            ValueError: If status transition is invalid or cash register is not open.
        """
        # Validate cash register is open when marking as delivered
        if status_update.status == "delivered":
            from app.crud.cash_closing import cash_closing
            from app.utils.timezone import get_local_date

            if not cash_closing.is_cash_register_open(
                db, target_date=get_local_today()
            ):
                logger.error(
                    f"Cannot deliver repair {repair_id}: Cash register is not open"
                )
                raise ValueError(
                    "Cash register must be open to deliver repairs. Please open the cash register first."
                )

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
            ValueError: If repair is not ready for delivery or cash register is not open.
        """
        # Validate cash register is open before delivering

        from app.crud.cash_closing import cash_closing
        from app.utils.timezone import get_local_date

        if not cash_closing.is_cash_register_open(db, target_date=get_local_date()):
            logger.error(
                f"Cannot deliver repair {repair_id}: Cash register is not open"
            )
            raise ValueError(
                "Cash register must be open to deliver repairs. Please open the cash register first."
            )

        try:
            # Mark repair as delivered
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

    def prepare_for_sale(self, db: Session, repair_id: int) -> Optional[dict[str, Any]]:
        """Prepare repair for POS sale.

        Gets repair details, calculates deposits, and returns data needed
        for adding the repair to POS cart.

        Args:
            db: Database session.
            repair_id: Repair ID.

        Returns:
            Dictionary with repair sale data or None if not found.

        Raises:
            ValueError: If repair is not ready for delivery.
        """
        # Get repair
        repair = repair_crud.get_repair(db, repair_id)
        if not repair:
            return None

        # Validate repair is ready for delivery
        if repair.status not in ["completed", "ready_for_pickup"]:
            raise ValueError(
                f"Repair {repair.repair_number} is not ready for delivery. "
                f"Current status: {repair.status}"
            )

        # Must have final cost
        if not repair.final_cost:
            raise ValueError(
                f"Repair {repair.repair_number} does not have a final cost set"
            )

        # Calculate total deposits
        total_deposits = Decimal("0.00")
        active_deposits = (
            db.query(RepairDeposit)
            .filter(
                and_(
                    RepairDeposit.repair_id == repair_id,
                    RepairDeposit.status == DepositStatus.ACTIVE,
                )
            )
            .all()
        )

        for deposit in active_deposits:
            total_deposits += deposit.amount

        # Calculate amount due
        amount_due = repair.final_cost - total_deposits

        logger.info(
            f"Prepared repair {repair.repair_number} for sale: "
            f"Total ${repair.final_cost}, Deposits ${total_deposits}, Due ${amount_due}"
        )

        return {
            "repair_id": repair.id,
            "repair_number": repair.repair_number,
            "customer_id": repair.customer_id,
            "customer_name": repair.customer.name,
            "device": f"{repair.device_brand} {repair.device_model or ''}".strip(),
            "device_type": repair.device_type,
            "problem": repair.problem_description,
            "total_cost": float(repair.final_cost),
            "labor_cost": float(repair.labor_cost) if repair.labor_cost else 0,
            "parts_cost": float(repair.parts_cost) if repair.parts_cost else 0,
            "total_deposits": float(total_deposits),
            "amount_due": float(amount_due),
            "deposits": [
                {
                    "id": deposit.id,
                    "amount": float(deposit.amount),
                    "payment_method": deposit.payment_method,
                    "receipt_number": deposit.receipt_number,
                    "date": deposit.created_at.isoformat(),
                }
                for deposit in active_deposits
            ],
        }

    def complete_sale_delivery(
        self, db: Session, repair_id: int, sale_id: int, user_id: int
    ) -> Optional[RepairResponse]:
        """Complete repair delivery after POS sale.

        Links repair to sale, applies deposits, and marks as delivered.

        Args:
            db: Database session.
            repair_id: Repair ID.
            sale_id: Sale ID from POS checkout.
            user_id: User completing the delivery.

        Returns:
            Updated repair or None if not found.

        Raises:
            ValueError: If repair is not ready for delivery.
        """
        # Get repair
        repair = repair_crud.get_repair(db, repair_id)
        if not repair:
            return None

        # Validate repair is ready
        if repair.status != "ready":
            raise ValueError(
                f"Repair {repair.repair_number} is not ready for delivery. "
                f"Current status: {repair.status}"
            )

        try:
            # Link repair to sale
            repair.sale_id = sale_id
            repair.delivered_by = user_id
            repair.delivered_date = func.now()
            repair.status = "delivered"

            # Apply deposits to sale
            deposits = (
                db.query(RepairDeposit)
                .filter(
                    and_(
                        RepairDeposit.repair_id == repair_id,
                        RepairDeposit.status == DepositStatus.ACTIVE,
                    )
                )
                .all()
            )

            for deposit in deposits:
                deposit.status = DepositStatus.APPLIED
                deposit.sale_id = sale_id
                logger.info(
                    f"Applied deposit {deposit.receipt_number} (${deposit.amount}) to sale {sale_id}"
                )

            # Add status history
            from app.models.repair import RepairStatusHistory

            status_history = RepairStatusHistory(
                repair_id=repair_id,
                status="delivered",
                notes=f"Delivered through POS sale #{sale_id}",
                changed_by=user_id,
            )
            db.add(status_history)

            # Set warranty expiration if applicable
            if repair.warranty_days > 0:
                from datetime import timedelta

                repair.warranty_expires = get_local_today() + timedelta(
                    days=repair.warranty_days
                )

            db.commit()

            logger.info(
                f"Completed delivery of repair {repair.repair_number} through sale {sale_id}"
            )

            return self._format_repair_response(db, repair)

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to complete repair delivery: {e}")
            raise

    def get_repair_by_number(
        self, db: Session, repair_number: str
    ) -> Optional[RepairResponse]:
        """Get repair by repair number.

        Args:
            db: Database session.
            repair_number: Repair number to search.

        Returns:
            Repair details or None if not found.
        """
        repair = db.query(Repair).filter(Repair.repair_number == repair_number).first()
        if not repair:
            return None

        return self._format_repair_response(db, repair)

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
            "sale_id": repair.sale_id,
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
