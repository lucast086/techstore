"""CRUD operations for repair management."""

from datetime import timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.customer import Customer
from app.models.repair import Repair, RepairPart, RepairPhoto, RepairStatusHistory
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
from app.utils.timezone import get_local_today, get_utc_now


class RepairCRUD:
    """CRUD operations for repairs."""

    def generate_repair_number(self, db: Session) -> str:
        """Generate unique repair number."""
        current_year = get_utc_now().year

        # Get the last repair number for current year
        last_repair = (
            db.query(Repair)
            .filter(Repair.repair_number.like(f"REP-{current_year}-%"))
            .order_by(desc(Repair.id))
            .first()
        )

        if last_repair:
            # Extract number and increment
            last_number = int(last_repair.repair_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"REP-{current_year}-{new_number:05d}"

    def create_repair(
        self, db: Session, *, repair_in: RepairCreate, received_by_id: int
    ) -> Repair:
        """Create new repair order."""
        # Validate customer exists
        customer = (
            db.query(Customer).filter(Customer.id == repair_in.customer_id).first()
        )
        if not customer:
            raise ValueError(f"Customer {repair_in.customer_id} not found")

        # Generate repair number
        repair_number = self.generate_repair_number(db)

        # Create repair
        db_repair = Repair(
            repair_number=repair_number,
            customer_id=repair_in.customer_id,
            device_type=repair_in.device_type,
            device_brand=repair_in.device_brand,
            device_model=repair_in.device_model,
            serial_number=repair_in.serial_number,
            problem_description=repair_in.problem_description,
            device_condition=repair_in.device_condition,
            accessories_received=repair_in.accessories_received,
            estimated_completion=repair_in.estimated_completion,
            warranty_days=repair_in.warranty_days,
            is_express=repair_in.is_express,
            assigned_technician=repair_in.assigned_technician,
            received_by=received_by_id,
            status=RepairStatus.RECEIVED,
        )

        db.add(db_repair)
        db.flush()

        # Add initial status history
        status_history = RepairStatusHistory(
            repair_id=db_repair.id,
            status=RepairStatus.RECEIVED,
            notes="Repair order created",
            changed_by=received_by_id,
        )
        db.add(status_history)

        db.commit()
        db.refresh(db_repair)
        return db_repair

    def get_repair(self, db: Session, repair_id: int) -> Optional[Repair]:
        """Get single repair by ID."""
        return (
            db.query(Repair)
            .options(
                joinedload(Repair.customer),
                joinedload(Repair.technician),
                joinedload(Repair.receiver),
                joinedload(Repair.deliverer),
                selectinload(Repair.parts),
                selectinload(Repair.photos),
                selectinload(Repair.status_history).joinedload(
                    RepairStatusHistory.user
                ),
            )
            .filter(Repair.id == repair_id)
            .first()
        )

    def get_repair_by_number(self, db: Session, repair_number: str) -> Optional[Repair]:
        """Get repair by repair number."""
        return (
            db.query(Repair)
            .options(
                joinedload(Repair.customer),
                joinedload(Repair.technician),
                selectinload(Repair.parts),
            )
            .filter(Repair.repair_number == repair_number)
            .first()
        )

    def search_repairs(
        self, db: Session, *, params: RepairSearchParams
    ) -> tuple[list[Repair], int]:
        """Search repairs with filters and pagination."""
        query = db.query(Repair).options(
            joinedload(Repair.customer),
            joinedload(Repair.technician),
        )

        # Text search
        if params.q:
            search_term = f"%{params.q}%"
            query = query.join(Customer).filter(
                or_(
                    Repair.repair_number.ilike(search_term),
                    Customer.name.ilike(search_term),
                    Customer.phone.ilike(search_term),
                    Repair.device_brand.ilike(search_term),
                    Repair.device_model.ilike(search_term),
                    Repair.serial_number.ilike(search_term),
                )
            )

        # Status filter
        if params.status:
            query = query.filter(Repair.status == params.status)

        # Technician filter
        if params.technician_id:
            query = query.filter(Repair.assigned_technician == params.technician_id)

        # Device filters
        if params.device_type:
            query = query.filter(Repair.device_type == params.device_type)
        if params.device_brand:
            query = query.filter(Repair.device_brand == params.device_brand)

        # Date range filter
        if params.date_from:
            query = query.filter(Repair.received_date >= params.date_from)
        if params.date_to:
            # Add one day to include the entire end date
            end_date = params.date_to + timedelta(days=1)
            query = query.filter(Repair.received_date < end_date)

        # Express filter
        if params.is_express is not None:
            query = query.filter(Repair.is_express == params.is_express)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        repairs = (
            query.order_by(desc(Repair.received_date))
            .offset(params.offset)
            .limit(params.page_size)
            .all()
        )

        return repairs, total

    def update_repair(
        self, db: Session, *, repair_id: int, repair_in: RepairUpdate
    ) -> Optional[Repair]:
        """Update repair details."""
        repair = self.get_repair(db, repair_id)
        if not repair:
            return None

        update_data = repair_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(repair, field, value)

        db.commit()
        db.refresh(repair)
        return repair

    def add_diagnosis(
        self,
        db: Session,
        *,
        repair_id: int,
        diagnosis: RepairDiagnosis,
        user_id: int,
    ) -> Optional[Repair]:
        """Add or update diagnosis for repair.

        If diagnosis is edited after customer approval, the repair will be
        reverted to 'diagnosing' status and customer approval will be removed.
        This allows technicians to update diagnosis at any time (except when
        repair is in 'ready' or 'delivered' status).
        """
        repair = self.get_repair(db, repair_id)
        if not repair:
            return None

        # Check if diagnosis was already set (this is an edit)
        is_edit = repair.diagnosis_notes is not None

        # Check if repair was previously approved
        was_approved = repair.customer_approved and repair.status in [
            RepairStatus.APPROVED.value,
            RepairStatus.REPAIRING.value,
            RepairStatus.TESTING.value,
        ]

        # Update repair with diagnosis
        repair.diagnosis_notes = diagnosis.diagnosis_notes
        repair.estimated_cost = diagnosis.estimated_cost
        repair.labor_cost = diagnosis.labor_cost
        repair.parts_cost = diagnosis.parts_cost

        # Add parts if provided
        if diagnosis.parts:
            for part_data in diagnosis.parts:
                part = RepairPart(
                    repair_id=repair_id,
                    part_name=part_data.part_name,
                    part_cost=part_data.part_cost,
                    quantity=part_data.quantity,
                    supplier=part_data.supplier,
                )
                db.add(part)

        # Handle status updates based on current state
        if repair.status == RepairStatus.RECEIVED.value:
            # First diagnosis - move to diagnosing
            repair.status = RepairStatus.DIAGNOSING.value
            status_history = RepairStatusHistory(
                repair_id=repair_id,
                status=RepairStatus.DIAGNOSING.value,
                notes="Diagnosis added",
                changed_by=user_id,
            )
            db.add(status_history)
        elif is_edit and was_approved:
            # Diagnosis edited after approval - revert to diagnosing and remove approval
            repair.status = RepairStatus.DIAGNOSING.value
            repair.customer_approved = False
            repair.approval_date = None
            status_history = RepairStatusHistory(
                repair_id=repair_id,
                status=RepairStatus.DIAGNOSING.value,
                notes="Diagnosis updated - customer approval reset",
                changed_by=user_id,
            )
            db.add(status_history)

        db.commit()
        db.refresh(repair)
        return repair

    def update_status(
        self,
        db: Session,
        *,
        repair_id: int,
        status_update: RepairStatusUpdate,
        user_id: int,
    ) -> Optional[Repair]:
        """Update repair status with validation."""
        repair = self.get_repair(db, repair_id)
        if not repair:
            return None

        # Validate status transition
        if not self._is_valid_status_transition(repair.status, status_update.status):
            raise ValueError(
                f"Invalid status transition from {repair.status} to {status_update.status}"
            )

        # Update status
        repair.status = status_update.status

        # Add status history
        status_history = RepairStatusHistory(
            repair_id=repair_id,
            status=status_update.status,
            notes=status_update.notes,
            changed_by=user_id,
        )
        db.add(status_history)

        # Handle specific status changes
        if status_update.status == RepairStatus.APPROVED:
            repair.customer_approved = True
            repair.approval_date = get_utc_now()

        db.commit()
        db.refresh(repair)
        return repair

    def complete_repair(
        self,
        db: Session,
        *,
        repair_id: int,
        completion: RepairComplete,
        user_id: int,
    ) -> Optional[Repair]:
        """Mark repair as completed."""
        repair = self.get_repair(db, repair_id)
        if not repair:
            return None

        if repair.status not in [RepairStatus.REPAIRING, RepairStatus.TESTING]:
            raise ValueError(
                "Repair must be in repairing or testing status to complete"
            )

        # Update repair
        repair.final_cost = completion.final_cost
        repair.repair_notes = completion.repair_notes
        repair.warranty_days = completion.warranty_days
        repair.completed_date = get_utc_now()
        repair.status = RepairStatus.READY

        # Calculate warranty expiration
        repair.warranty_expires = get_local_today() + timedelta(
            days=completion.warranty_days
        )

        # Add status history
        status_history = RepairStatusHistory(
            repair_id=repair_id,
            status=RepairStatus.READY,
            notes="Repair completed",
            changed_by=user_id,
        )
        db.add(status_history)

        db.commit()
        db.refresh(repair)
        return repair

    def deliver_repair(
        self,
        db: Session,
        *,
        repair_id: int,
        delivery: RepairDeliver,
    ) -> Optional[Repair]:
        """Mark repair as delivered and create associated sale."""
        repair = self.get_repair(db, repair_id)
        if not repair:
            return None

        if repair.status != RepairStatus.READY:
            raise ValueError("Repair must be ready for delivery")

        # Ensure repair has a final cost
        if not repair.final_cost or repair.final_cost <= 0:
            raise ValueError("Repair must have a final cost before delivery")

        # Get or create repair service product
        from app.models.product import Product

        repair_product = (
            db.query(Product)
            .filter(Product.sku == "REPAIR-SERVICE", Product.is_service == True)
            .first()
        )

        if not repair_product:
            raise ValueError(
                "Repair service product (SKU: REPAIR-SERVICE) not found. "
                "Please create a service product for repairs."
            )

        # Check customer credit
        from app.services.customer_account_service import customer_account_service

        has_credit = False
        available_credit = Decimal("0.00")
        if repair.customer_id:
            (
                has_credit,
                available_credit,
                _,
            ) = customer_account_service.check_credit_availability(
                db, repair.customer_id
            )

        # Calculate how much credit to apply
        credit_to_apply = (
            min(available_credit, repair.final_cost) if has_credit else Decimal("0.00")
        )

        # Create sale with amount_paid=0 initially
        # We'll apply credit separately to properly track it
        from app.crud.sale import sale_crud
        from app.schemas.sale import SaleCreate, SaleItemCreate

        sale_data = SaleCreate(
            customer_id=repair.customer_id,
            # Use account_credit if there's any credit to apply, not just if it covers full amount
            payment_method="account_credit" if credit_to_apply > 0 else "cash",
            items=[
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=repair.final_cost,
                    discount_percentage=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                )
            ],
            discount_amount=Decimal("0.00"),
            notes=f"Repair delivery: {repair.repair_number} - {repair.device_brand} {repair.device_model or ''}",
            amount_paid=Decimal("0.00"),  # Start with 0, apply credit after
        )

        sale = sale_crud.create_sale(
            db=db, sale_in=sale_data, user_id=delivery.delivered_by
        )

        # Apply credit if available
        if credit_to_apply > 0:
            customer_account_service.apply_credit(
                db=db,
                customer_id=repair.customer_id,
                amount=credit_to_apply,
                sale_id=sale.id,
                created_by_id=delivery.delivered_by,
                notes=f"Credit applied to repair {repair.repair_number}",
            )

            # Update sale with credit applied
            sale.paid_amount = credit_to_apply
            if credit_to_apply >= sale.total_amount:
                sale.payment_status = "paid"
            else:
                sale.payment_status = "partial"
            db.add(sale)

        # Update repair with sale reference
        repair.sale_id = sale.id
        repair.delivered_date = get_utc_now()
        repair.delivered_by = delivery.delivered_by
        repair.status = RepairStatus.DELIVERED

        # Add status history
        status_history = RepairStatusHistory(
            repair_id=repair_id,
            status=RepairStatus.DELIVERED,
            notes=delivery.delivery_notes or "Device delivered to customer",
            changed_by=delivery.delivered_by,
        )
        db.add(status_history)

        db.commit()
        db.refresh(repair)
        return repair

    def add_part(
        self, db: Session, *, repair_id: int, part_in: RepairPartCreate
    ) -> Optional[RepairPart]:
        """Add part to repair."""
        repair = db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            return None

        part = RepairPart(
            repair_id=repair_id,
            part_name=part_in.part_name,
            part_cost=part_in.part_cost,
            quantity=part_in.quantity,
            supplier=part_in.supplier,
        )
        db.add(part)

        # Update parts cost
        repair.parts_cost = (repair.parts_cost or Decimal("0")) + (
            part_in.part_cost * part_in.quantity
        )

        db.commit()
        db.refresh(part)
        return part

    def remove_part(self, db: Session, *, part_id: int) -> bool:
        """Remove part from repair."""
        part = db.query(RepairPart).filter(RepairPart.id == part_id).first()
        if not part:
            return False

        # Update repair parts cost
        repair = db.query(Repair).filter(Repair.id == part.repair_id).first()
        if repair:
            repair.parts_cost = (repair.parts_cost or Decimal("0")) - (
                part.part_cost * part.quantity
            )

        db.delete(part)
        db.commit()
        return True

    def add_photo(
        self,
        db: Session,
        *,
        repair_id: int,
        photo_in: RepairPhotoCreate,
        user_id: int,
    ) -> Optional[RepairPhoto]:
        """Add photo to repair."""
        repair = db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            return None

        photo = RepairPhoto(
            repair_id=repair_id,
            photo_url=photo_in.photo_url,
            photo_type=photo_in.photo_type,
            description=photo_in.description,
            uploaded_by=user_id,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return photo

    def get_repair_statistics(self, db: Session) -> dict:
        """Get repair statistics."""
        # Total repairs by status
        status_counts = (
            db.query(Repair.status, func.count(Repair.id)).group_by(Repair.status).all()
        )

        status_dict = dict(status_counts)

        # Calculate average repair time for completed repairs
        avg_repair_time = (
            db.query(
                func.avg(
                    func.extract(
                        "epoch",
                        Repair.completed_date - Repair.received_date,
                    )
                    / 86400  # Convert to days
                )
            )
            .filter(Repair.completed_date.isnot(None))
            .scalar()
        )

        # Total revenue
        total_revenue = db.query(func.sum(Repair.final_cost)).filter(
            Repair.final_cost.isnot(None)
        ).scalar() or Decimal("0")

        # Pending revenue
        pending_revenue = db.query(func.sum(Repair.estimated_cost)).filter(
            and_(
                Repair.status.notin_([RepairStatus.DELIVERED, RepairStatus.CANCELLED]),
                Repair.estimated_cost.isnot(None),
            )
        ).scalar() or Decimal("0")

        return {
            "total_repairs": sum(status_dict.values()),
            "pending_repairs": status_dict.get(RepairStatus.RECEIVED, 0)
            + status_dict.get(RepairStatus.DIAGNOSING, 0)
            + status_dict.get(RepairStatus.APPROVED, 0)
            + status_dict.get(RepairStatus.REPAIRING, 0)
            + status_dict.get(RepairStatus.TESTING, 0),
            "completed_repairs": status_dict.get(RepairStatus.READY, 0),
            "delivered_repairs": status_dict.get(RepairStatus.DELIVERED, 0),
            "express_repairs": db.query(Repair)
            .filter(Repair.is_express.is_(True))
            .count(),
            "average_repair_time_days": round(avg_repair_time, 1)
            if avg_repair_time
            else None,
            "total_revenue": total_revenue,
            "pending_revenue": pending_revenue,
        }

    def _is_valid_status_transition(
        self, current_status: RepairStatus, new_status: RepairStatus
    ) -> bool:
        """Validate status transition."""
        valid_transitions = {
            RepairStatus.RECEIVED: [
                RepairStatus.DIAGNOSING,
                RepairStatus.CANCELLED,
            ],
            RepairStatus.DIAGNOSING: [
                RepairStatus.APPROVED,
                RepairStatus.CANCELLED,
                RepairStatus.READY,  # For express repairs
            ],
            RepairStatus.APPROVED: [
                RepairStatus.REPAIRING,
                RepairStatus.CANCELLED,
            ],
            RepairStatus.REPAIRING: [
                RepairStatus.TESTING,
                RepairStatus.READY,
                RepairStatus.CANCELLED,
            ],
            RepairStatus.TESTING: [
                RepairStatus.READY,
                RepairStatus.REPAIRING,  # Back to repair if issues found
                RepairStatus.CANCELLED,
            ],
            RepairStatus.READY: [
                RepairStatus.DELIVERED,
                RepairStatus.REPAIRING,  # If customer reports issues
            ],
            RepairStatus.DELIVERED: [],  # Final status
            RepairStatus.CANCELLED: [],  # Final status
        }

        return new_status in valid_transitions.get(current_status, [])


# Create singleton instance
repair_crud = RepairCRUD()
