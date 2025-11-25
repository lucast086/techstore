"""Service layer for repair deposits management."""

import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.repair_deposit import repair_deposit_crud
from app.models.customer_account import TransactionType
from app.models.repair_deposit import DepositStatus, RepairDeposit
from app.schemas.repair_deposit import (
    DepositCreate,
    DepositListParams,
    DepositRefund,
    DepositResponse,
    DepositSummary,
)
from app.services.customer_account_service import customer_account_service

logger = logging.getLogger(__name__)


class RepairDepositService:
    """Service for handling repair deposit business logic."""

    def record_deposit(
        self, db: Session, deposit_data: DepositCreate, received_by_id: int
    ) -> DepositResponse:
        """Record a new deposit for a repair.

        Args:
            db: Database session
            deposit_data: Deposit details
            received_by_id: ID of user receiving the deposit

        Returns:
            Created deposit with full details

        Raises:
            ValueError: If validation fails
        """
        # Verify repair exists
        from app.crud.repair import repair_crud
        from app.schemas.repair import RepairStatus

        repair = repair_crud.get_repair(db, deposit_data.repair_id)
        if not repair:
            raise ValueError(f"Repair {deposit_data.repair_id} not found")

        # Verify customer matches repair
        if repair.customer_id != deposit_data.customer_id:
            raise ValueError("Customer does not match repair")

        # Verify repair status allows deposits (not delivered or cancelled)
        if repair.status in [RepairStatus.DELIVERED, RepairStatus.CANCELLED]:
            raise ValueError(f"Cannot add deposit to {repair.status} repair")

        # Validate deposit amount
        if deposit_data.amount <= 0:
            raise ValueError("Deposit amount must be greater than zero")

        # Check if repair has a cost estimate
        if repair.estimated_cost:
            # Calculate existing deposits
            existing_deposits = self.calculate_total_deposits(
                db, deposit_data.repair_id, DepositStatus.ACTIVE
            )

            # Verify total deposits don't exceed repair cost
            total_with_new = existing_deposits + deposit_data.amount
            if total_with_new > repair.estimated_cost:
                raise ValueError(
                    f"Total deposits (${total_with_new:.2f}) would exceed "
                    f"repair estimated cost (${repair.estimated_cost:.2f})"
                )

        # Create deposit record
        deposit = repair_deposit_crud.create_deposit(
            db=db, deposit_in=deposit_data, received_by_id=received_by_id
        )

        # Record in customer account as a credit (negative balance)
        try:
            transaction = customer_account_service.record_transaction(
                db=db,
                customer_id=deposit_data.customer_id,
                transaction_type=TransactionType.REPAIR_DEPOSIT,
                amount=-deposit_data.amount,  # Negative because it's a credit to customer
                reference_id=deposit.id,
                description=f"Deposit for repair {repair.repair_number}",
                created_by_id=received_by_id,
                notes=deposit_data.notes,
            )

            # Update deposit with transaction reference
            deposit.transaction_id = transaction.id

            db.commit()
            db.refresh(deposit)

            logger.info(
                f"Recorded deposit {deposit.receipt_number} for repair {repair.repair_number}. "
                f"Customer account transaction: {transaction.id}"
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record deposit in customer account: {e}")
            raise ValueError(f"Failed to record deposit: {str(e)}")

        return self._format_deposit_response(db, deposit)

    def get_deposit(self, db: Session, deposit_id: int) -> Optional[DepositResponse]:
        """Get deposit by ID.

        Args:
            db: Database session
            deposit_id: Deposit ID

        Returns:
            Deposit details or None if not found
        """
        deposit = repair_deposit_crud.get_deposit(db, deposit_id)
        if not deposit:
            return None

        return self._format_deposit_response(db, deposit)

    def get_repair_deposits(self, db: Session, repair_id: int) -> DepositSummary:
        """Get all deposits for a repair with summary.

        Args:
            db: Database session
            repair_id: Repair ID

        Returns:
            Deposit summary with list of deposits
        """
        deposits = repair_deposit_crud.get_repair_deposits(db, repair_id)

        # Calculate totals by status
        total_deposits = Decimal("0.00")
        active_deposits = Decimal("0.00")
        applied_deposits = Decimal("0.00")
        refunded_deposits = Decimal("0.00")

        for deposit in deposits:
            total_deposits += deposit.amount

            if deposit.status == DepositStatus.ACTIVE:
                active_deposits += deposit.amount
            elif deposit.status == DepositStatus.APPLIED:
                applied_deposits += deposit.amount
            elif deposit.status == DepositStatus.REFUNDED:
                refunded_deposits += deposit.refunded_amount or deposit.amount

        # Format deposit responses
        deposit_responses = [
            self._format_deposit_response(db, deposit) for deposit in deposits
        ]

        return DepositSummary(
            repair_id=repair_id,
            total_deposits=total_deposits,
            active_deposits=active_deposits,
            applied_deposits=applied_deposits,
            refunded_deposits=refunded_deposits,
            deposit_count=len(deposits),
            deposits=deposit_responses,
        )

    def calculate_total_deposits(
        self, db: Session, repair_id: int, status: Optional[DepositStatus] = None
    ) -> Decimal:
        """Calculate total deposits for a repair.

        Args:
            db: Database session
            repair_id: Repair ID
            status: Optional status filter

        Returns:
            Total deposit amount
        """
        return repair_deposit_crud.calculate_total_deposits(db, repair_id, status)

    def apply_deposits_to_sale(
        self, db: Session, repair_id: int, sale_id: int
    ) -> list[DepositResponse]:
        """Apply all active deposits of a repair to a sale.

        Args:
            db: Database session
            repair_id: Repair ID
            sale_id: Sale ID

        Returns:
            List of applied deposits
        """
        applied = repair_deposit_crud.apply_deposits_to_sale(db, repair_id, sale_id)

        # Update customer account transactions
        for deposit in applied:
            if deposit.transaction_id:
                # Update the transaction to link it to the sale
                from app.models.customer_account import CustomerTransaction

                transaction = (
                    db.query(CustomerTransaction)
                    .filter(CustomerTransaction.id == deposit.transaction_id)
                    .first()
                )
                if transaction:
                    transaction.sale_id = sale_id
                    transaction.description = (
                        f"Deposit applied to sale #{sale_id} "
                        f"(Repair {deposit.repair.repair_number})"
                    )

        db.commit()

        logger.info(
            f"Applied {len(applied)} deposits from repair {repair_id} to sale {sale_id}"
        )

        return [self._format_deposit_response(db, deposit) for deposit in applied]

    def refund_deposit(
        self,
        db: Session,
        deposit_id: int,
        refund_data: DepositRefund,
        refunded_by_id: int,
    ) -> DepositResponse:
        """Refund a deposit.

        Args:
            db: Database session
            deposit_id: Deposit ID
            refund_data: Refund details
            refunded_by_id: ID of user processing refund

        Returns:
            Updated deposit

        Raises:
            ValueError: If validation fails
        """
        # Get deposit
        deposit = repair_deposit_crud.get_deposit(db, deposit_id)
        if not deposit:
            raise ValueError(f"Deposit {deposit_id} not found")

        # Validate deposit can be refunded
        if deposit.status == DepositStatus.REFUNDED:
            raise ValueError("Deposit has already been refunded")

        if deposit.status == DepositStatus.APPLIED:
            raise ValueError("Cannot refund an applied deposit. Void the sale first")

        if deposit.status == DepositStatus.VOIDED:
            raise ValueError("Cannot refund a voided deposit")

        # Process refund
        refund_amount = refund_data.refund_amount or deposit.amount

        # Validate refund amount
        if refund_amount <= 0:
            raise ValueError("Refund amount must be greater than zero")

        if refund_amount > deposit.amount:
            raise ValueError(
                f"Refund amount cannot exceed deposit amount (${deposit.amount:.2f})"
            )

        deposit = repair_deposit_crud.refund_deposit(
            db=db,
            deposit_id=deposit_id,
            refunded_by_id=refunded_by_id,
            refund_amount=refund_amount,
            refund_reason=refund_data.refund_reason,
        )

        # Record refund in customer account (positive amount to reduce credit)
        try:
            transaction = customer_account_service.record_transaction(
                db=db,
                customer_id=deposit.customer_id,
                transaction_type=TransactionType.REPAIR_DEPOSIT,
                amount=refund_amount,  # Positive to reduce credit
                reference_id=deposit.id,
                description=f"Refund of deposit {deposit.receipt_number}",
                created_by_id=refunded_by_id,
                notes=refund_data.refund_reason,
            )

            db.commit()

            logger.info(
                f"Refunded deposit {deposit.receipt_number}. "
                f"Amount: ${refund_amount}, Transaction: {transaction.id}"
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record refund in customer account: {e}")
            raise ValueError(f"Failed to process refund: {str(e)}")

        return self._format_deposit_response(db, deposit)

    def void_deposit(
        self, db: Session, deposit_id: int, reason: str, voided_by_id: int
    ) -> DepositResponse:
        """Void a deposit.

        Args:
            db: Database session
            deposit_id: Deposit ID
            reason: Reason for voiding
            voided_by_id: ID of user voiding the deposit

        Returns:
            Updated deposit
        """
        # Get deposit
        deposit = repair_deposit_crud.get_deposit(db, deposit_id)
        if not deposit:
            raise ValueError(f"Deposit {deposit_id} not found")

        # Void the deposit
        deposit = repair_deposit_crud.void_deposit(db, deposit_id, reason)

        # Reverse the customer account transaction
        if deposit.transaction_id:
            try:
                transaction = customer_account_service.record_transaction(
                    db=db,
                    customer_id=deposit.customer_id,
                    transaction_type=TransactionType.REPAIR_DEPOSIT,
                    amount=deposit.amount,  # Positive to reverse the credit
                    reference_id=deposit.id,
                    description=f"Voided deposit {deposit.receipt_number}",
                    created_by_id=voided_by_id,
                    notes=f"Void reason: {reason}",
                )

                db.commit()

                logger.info(
                    f"Voided deposit {deposit.receipt_number}. "
                    f"Reversal transaction: {transaction.id}"
                )

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to reverse deposit in customer account: {e}")
                raise ValueError(f"Failed to void deposit: {str(e)}")

        return self._format_deposit_response(db, deposit)

    def list_deposits(
        self, db: Session, params: DepositListParams
    ) -> tuple[list[DepositResponse], int]:
        """List deposits with filters.

        Args:
            db: Database session
            params: Filter parameters

        Returns:
            Tuple of (deposits, total count)
        """
        deposits, total = repair_deposit_crud.list_deposits(db, params)

        deposit_responses = [
            self._format_deposit_response(db, deposit) for deposit in deposits
        ]

        return deposit_responses, total

    def get_daily_deposits_total(self, db: Session, date) -> Decimal:
        """Get total deposits received on a specific date.

        Args:
            db: Database session
            date: Date to check

        Returns:
            Total deposits amount
        """
        return repair_deposit_crud.get_daily_deposits_total(db, date)

    def _format_deposit_response(
        self, db: Session, deposit: RepairDeposit
    ) -> DepositResponse:
        """Format deposit into response schema.

        Args:
            db: Database session
            deposit: Deposit model instance

        Returns:
            Formatted deposit response
        """
        return DepositResponse(
            id=deposit.id,
            repair_id=deposit.repair_id,
            customer_id=deposit.customer_id,
            sale_id=deposit.sale_id,
            amount=deposit.amount,
            payment_method=deposit.payment_method,
            receipt_number=deposit.receipt_number,
            status=deposit.status,
            refunded_amount=deposit.refunded_amount,
            refund_date=deposit.refund_date,
            refund_reason=deposit.refund_reason,
            transaction_id=deposit.transaction_id,
            notes=deposit.notes,
            received_by_id=deposit.received_by_id,
            created_at=deposit.created_at,
            updated_at=deposit.updated_at,
            customer_name=deposit.customer.name if deposit.customer else None,
            repair_number=deposit.repair.repair_number if deposit.repair else None,
            received_by_name=deposit.received_by.full_name
            if deposit.received_by
            else None,
            refunded_by_name=deposit.refunded_by.full_name
            if deposit.refunded_by
            else None,
        )


# Create singleton instance
repair_deposit_service = RepairDepositService()
