"""CRUD operations for repair deposits."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.repair_deposit import DepositStatus, RepairDeposit
from app.schemas.repair_deposit import DepositCreate, DepositListParams, DepositUpdate

logger = logging.getLogger(__name__)


class CRUDRepairDeposit(CRUDBase[RepairDeposit, DepositCreate, DepositUpdate]):
    """CRUD operations for repair deposits."""

    def create_deposit(
        self, db: Session, *, deposit_in: DepositCreate, received_by_id: int
    ) -> RepairDeposit:
        """Create a new repair deposit.

        Args:
            db: Database session
            deposit_in: Deposit data
            received_by_id: ID of user receiving the deposit

        Returns:
            Created deposit
        """
        # Generate receipt number
        receipt_number = self._generate_receipt_number(db)

        # Create deposit record
        db_obj = RepairDeposit(
            repair_id=deposit_in.repair_id,
            customer_id=deposit_in.customer_id,
            amount=deposit_in.amount,
            payment_method=deposit_in.payment_method,
            receipt_number=receipt_number,
            status=DepositStatus.ACTIVE,
            notes=deposit_in.notes,
            received_by_id=received_by_id,
        )

        db.add(db_obj)
        db.flush()  # Flush to get ID before committing

        logger.info(
            f"Created deposit {receipt_number} for repair {deposit_in.repair_id}. "
            f"Amount: ${deposit_in.amount}"
        )

        return db_obj

    def get_deposit(self, db: Session, deposit_id: int) -> Optional[RepairDeposit]:
        """Get deposit by ID with relationships loaded.

        Args:
            db: Database session
            deposit_id: Deposit ID

        Returns:
            Deposit or None if not found
        """
        return (
            db.query(RepairDeposit)
            .options(
                joinedload(RepairDeposit.repair),
                joinedload(RepairDeposit.customer),
                joinedload(RepairDeposit.received_by),
                joinedload(RepairDeposit.refunded_by),
            )
            .filter(RepairDeposit.id == deposit_id)
            .first()
        )

    def get_by_receipt(
        self, db: Session, receipt_number: str
    ) -> Optional[RepairDeposit]:
        """Get deposit by receipt number.

        Args:
            db: Database session
            receipt_number: Receipt number

        Returns:
            Deposit or None if not found
        """
        return (
            db.query(RepairDeposit)
            .options(
                joinedload(RepairDeposit.repair),
                joinedload(RepairDeposit.customer),
            )
            .filter(RepairDeposit.receipt_number == receipt_number)
            .first()
        )

    def get_repair_deposits(
        self, db: Session, repair_id: int, status: Optional[DepositStatus] = None
    ) -> list[RepairDeposit]:
        """Get all deposits for a repair.

        Args:
            db: Database session
            repair_id: Repair ID
            status: Optional status filter

        Returns:
            List of deposits
        """
        query = (
            db.query(RepairDeposit)
            .options(
                joinedload(RepairDeposit.customer),
                joinedload(RepairDeposit.received_by),
            )
            .filter(RepairDeposit.repair_id == repair_id)
        )

        if status:
            query = query.filter(RepairDeposit.status == status)

        return query.order_by(RepairDeposit.created_at.desc()).all()

    def get_customer_deposits(
        self, db: Session, customer_id: int, status: Optional[DepositStatus] = None
    ) -> list[RepairDeposit]:
        """Get all deposits for a customer.

        Args:
            db: Database session
            customer_id: Customer ID
            status: Optional status filter

        Returns:
            List of deposits
        """
        query = (
            db.query(RepairDeposit)
            .options(
                joinedload(RepairDeposit.repair),
                joinedload(RepairDeposit.received_by),
            )
            .filter(RepairDeposit.customer_id == customer_id)
        )

        if status:
            query = query.filter(RepairDeposit.status == status)

        return query.order_by(RepairDeposit.created_at.desc()).all()

    def calculate_total_deposits(
        self, db: Session, repair_id: int, status: Optional[DepositStatus] = None
    ) -> Decimal:
        """Calculate total deposits for a repair.

        Args:
            db: Database session
            repair_id: Repair ID
            status: Optional status filter (defaults to ACTIVE)

        Returns:
            Total deposit amount
        """
        if status is None:
            status = DepositStatus.ACTIVE

        result = (
            db.query(func.coalesce(func.sum(RepairDeposit.amount), 0))
            .filter(
                and_(
                    RepairDeposit.repair_id == repair_id,
                    RepairDeposit.status == status,
                )
            )
            .scalar()
        )

        return Decimal(str(result))

    def apply_to_sale(
        self, db: Session, deposit_id: int, sale_id: int
    ) -> Optional[RepairDeposit]:
        """Apply deposit to a sale.

        Args:
            db: Database session
            deposit_id: Deposit ID
            sale_id: Sale ID to apply to

        Returns:
            Updated deposit or None if not found
        """
        deposit = self.get_deposit(db, deposit_id)
        if not deposit:
            return None

        if deposit.status != DepositStatus.ACTIVE:
            raise ValueError(f"Cannot apply deposit in {deposit.status} status")

        deposit.status = DepositStatus.APPLIED
        deposit.sale_id = sale_id

        db.commit()
        db.refresh(deposit)

        logger.info(f"Applied deposit {deposit.receipt_number} to sale {sale_id}")

        return deposit

    def apply_deposits_to_sale(
        self, db: Session, repair_id: int, sale_id: int
    ) -> list[RepairDeposit]:
        """Apply all active deposits of a repair to a sale.

        Args:
            db: Database session
            repair_id: Repair ID
            sale_id: Sale ID

        Returns:
            List of applied deposits
        """
        deposits = self.get_repair_deposits(db, repair_id, DepositStatus.ACTIVE)
        applied_deposits = []

        for deposit in deposits:
            deposit.status = DepositStatus.APPLIED
            deposit.sale_id = sale_id
            applied_deposits.append(deposit)

        if applied_deposits:
            db.commit()
            logger.info(
                f"Applied {len(applied_deposits)} deposits from repair {repair_id} to sale {sale_id}"
            )

        return applied_deposits

    def refund_deposit(
        self,
        db: Session,
        deposit_id: int,
        refunded_by_id: int,
        refund_amount: Optional[Decimal] = None,
        refund_reason: Optional[str] = None,
    ) -> Optional[RepairDeposit]:
        """Refund a deposit.

        Args:
            db: Database session
            deposit_id: Deposit ID
            refunded_by_id: ID of user processing refund
            refund_amount: Amount to refund (None for full refund)
            refund_reason: Reason for refund

        Returns:
            Updated deposit or None if not found
        """
        deposit = self.get_deposit(db, deposit_id)
        if not deposit:
            return None

        if deposit.status not in [DepositStatus.ACTIVE, DepositStatus.APPLIED]:
            raise ValueError(f"Cannot refund deposit in {deposit.status} status")

        # Default to full refund
        if refund_amount is None:
            refund_amount = deposit.amount

        # Validate refund amount
        if refund_amount > deposit.amount:
            raise ValueError("Refund amount cannot exceed deposit amount")

        deposit.status = DepositStatus.REFUNDED
        deposit.refunded_amount = refund_amount
        deposit.refund_date = datetime.utcnow()
        deposit.refund_reason = refund_reason
        deposit.refunded_by_id = refunded_by_id

        db.commit()
        db.refresh(deposit)

        logger.info(
            f"Refunded deposit {deposit.receipt_number}. Amount: ${refund_amount}"
        )

        return deposit

    def void_deposit(
        self, db: Session, deposit_id: int, reason: Optional[str] = None
    ) -> Optional[RepairDeposit]:
        """Void a deposit.

        Args:
            db: Database session
            deposit_id: Deposit ID
            reason: Reason for voiding

        Returns:
            Updated deposit or None if not found
        """
        deposit = self.get_deposit(db, deposit_id)
        if not deposit:
            return None

        if deposit.status != DepositStatus.ACTIVE:
            raise ValueError(f"Cannot void deposit in {deposit.status} status")

        deposit.status = DepositStatus.VOIDED
        if reason:
            deposit.notes = f"Voided: {reason}\n{deposit.notes or ''}"

        db.commit()
        db.refresh(deposit)

        logger.info(f"Voided deposit {deposit.receipt_number}")

        return deposit

    def list_deposits(
        self, db: Session, params: DepositListParams
    ) -> tuple[list[RepairDeposit], int]:
        """List deposits with filters.

        Args:
            db: Database session
            params: List parameters

        Returns:
            Tuple of (deposits, total count)
        """
        query = db.query(RepairDeposit).options(
            joinedload(RepairDeposit.repair),
            joinedload(RepairDeposit.customer),
            joinedload(RepairDeposit.received_by),
        )

        # Apply filters
        if params.repair_id:
            query = query.filter(RepairDeposit.repair_id == params.repair_id)

        if params.customer_id:
            query = query.filter(RepairDeposit.customer_id == params.customer_id)

        if params.status:
            query = query.filter(RepairDeposit.status == params.status)

        if params.payment_method:
            query = query.filter(RepairDeposit.payment_method == params.payment_method)

        if params.date_from:
            query = query.filter(RepairDeposit.created_at >= params.date_from)

        if params.date_to:
            query = query.filter(RepairDeposit.created_at <= params.date_to)

        # Get total count
        total = query.count()

        # Apply pagination
        deposits = (
            query.order_by(RepairDeposit.created_at.desc())
            .offset(params.skip)
            .limit(params.limit)
            .all()
        )

        return deposits, total

    def get_daily_deposits_total(self, db: Session, date: datetime) -> Decimal:
        """Get total deposits received on a specific date.

        Args:
            db: Database session
            date: Date to check

        Returns:
            Total deposits amount
        """
        result = (
            db.query(func.coalesce(func.sum(RepairDeposit.amount), 0))
            .filter(
                and_(
                    func.date(RepairDeposit.created_at) == date.date(),
                    RepairDeposit.status.in_(
                        [DepositStatus.ACTIVE, DepositStatus.APPLIED]
                    ),
                )
            )
            .scalar()
        )

        return Decimal(str(result))

    def _generate_receipt_number(self, db: Session) -> str:
        """Generate unique receipt number.

        Args:
            db: Database session

        Returns:
            Generated receipt number
        """
        # Get the last receipt number
        last_deposit = db.query(RepairDeposit).order_by(RepairDeposit.id.desc()).first()

        if last_deposit and last_deposit.receipt_number.startswith("DEP"):
            try:
                last_number = int(last_deposit.receipt_number[3:])
                next_number = last_number + 1
            except ValueError:
                next_number = 1
        else:
            next_number = 1

        return f"DEP{next_number:06d}"


# Create singleton instance
repair_deposit_crud = CRUDRepairDeposit(RepairDeposit)
