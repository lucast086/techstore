"""Cash closing service for managing daily cash register operations."""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.cash_closing import cash_closing
from app.schemas.cash_closing import (
    CashClosingCreate,
    CashClosingResponse,
    DailySummary,
)

logger = logging.getLogger(__name__)


class CashClosingService:
    """Service for handling cash closing business logic."""

    def start_daily_closing(
        self, db: Session, closing_date: date, user_id: int
    ) -> tuple[DailySummary, Optional[Decimal]]:
        """Initialize daily closing process.

        Args:
            db: Database session.
            closing_date: Date for the closing.
            user_id: ID of user starting the closing.

        Returns:
            Tuple of daily summary and opening balance from last closing.

        Raises:
            ValueError: If closing already exists for this date.
        """
        logger.info(f"Starting daily closing for {closing_date} by user {user_id}")

        # Check if closing already exists
        if cash_closing.check_closing_exists(db, closing_date=closing_date):
            raise ValueError(f"Closing already exists for date {closing_date}")

        # Get daily summary with sales and expenses
        daily_summary = cash_closing.get_daily_summary(db, target_date=closing_date)

        # Get opening balance from last finalized closing
        last_closing = cash_closing.get_last_closing(db)
        opening_balance = last_closing.cash_count if last_closing else Decimal("0.00")

        logger.info(
            f"Daily summary: {daily_summary.sales_count} sales totaling "
            f"${daily_summary.total_sales}, opening balance: ${opening_balance}"
        )

        return daily_summary, opening_balance

    def calculate_daily_totals(self, db: Session, target_date: date) -> DailySummary:
        """Calculate daily sales and expenses totals.

        Args:
            db: Database session.
            target_date: Date to calculate totals for.

        Returns:
            Daily summary with calculated totals.
        """
        logger.info(f"Calculating daily totals for {target_date}")
        return cash_closing.get_daily_summary(db, target_date=target_date)

    def validate_cash_difference(
        self, cash_difference: Decimal, threshold: Decimal = Decimal("10.00")
    ) -> tuple[bool, str]:
        """Validate if cash difference is within acceptable threshold.

        Args:
            cash_difference: Difference between expected and actual cash.
            threshold: Maximum acceptable difference (default $10.00).

        Returns:
            Tuple of (is_valid, warning_message).
        """
        abs_difference = abs(cash_difference)

        if abs_difference <= threshold:
            return True, ""

        if cash_difference > 0:
            warning = f"Cash overage of ${abs_difference:.2f} exceeds threshold of ${threshold:.2f}"
        else:
            warning = f"Cash shortage of ${abs_difference:.2f} exceeds threshold of ${threshold:.2f}"

        logger.warning(f"Cash difference validation failed: {warning}")
        return False, warning

    def get_pending_cash_register(self, db: Session) -> Optional[CashClosingResponse]:
        """Get any pending (unfinalized) cash register.

        Args:
            db: Database session.

        Returns:
            Pending cash register details if exists, None otherwise.
        """
        pending = cash_closing.get_unfinalized_register(db)
        if pending:
            logger.info(f"Found pending cash register from {pending.closing_date}")
            return CashClosingResponse.model_validate(pending)
        return None

    def open_cash_register(
        self, db: Session, opening_date: date, opening_balance: Decimal, user_id: int
    ) -> CashClosingResponse:
        """Open cash register for the day.

        Args:
            db: Database session.
            opening_date: Date to open register for.
            opening_balance: Starting cash amount.
            user_id: ID of user opening the register.

        Returns:
            Created opening record.

        Raises:
            ValueError: If register already opened for this date.
        """
        logger.info(
            f"Opening cash register for {opening_date} with balance ${opening_balance}"
        )

        try:
            db_opening = cash_closing.open_cash_register(
                db,
                target_date=opening_date,
                opening_balance=opening_balance,
                opened_by=user_id,
            )
            logger.info(f"Cash register opened for {opening_date}")
            return CashClosingResponse.model_validate(db_opening)
        except ValueError as e:
            logger.error(f"Failed to open cash register: {e}")
            raise

    def create_closing(
        self,
        db: Session,
        closing_data: CashClosingCreate,
        user_id: int,
    ) -> CashClosingResponse:
        """Create a new cash closing record.

        Args:
            db: Database session.
            closing_data: Closing details from form.
            user_id: ID of user creating the closing.

        Returns:
            Created closing with full details.

        Raises:
            ValueError: If closing already exists or validation fails.
        """
        logger.info(
            f"Creating closing for {closing_data.closing_date} by user {user_id}"
        )

        # Get existing record (from opening) or check if already closed
        existing = cash_closing.get_by_date(db, closing_date=closing_data.closing_date)

        if existing and existing.closed_at and existing.closed_by:
            # If it was already properly closed (not just opened)
            if existing.opened_at != existing.closed_at:
                raise ValueError(
                    f"Closing already exists for date {closing_data.closing_date}"
                )

        if not existing:
            # If no opening exists, we need to create the full record
            logger.warning(
                f"No opening record found for {closing_data.closing_date}, creating full closing"
            )

        # Get calculated totals for the date
        daily_summary = self.calculate_daily_totals(db, closing_data.closing_date)

        if existing:
            # Update the existing opening record with closing data
            expected_cash = (
                closing_data.opening_balance
                + daily_summary.total_sales
                - daily_summary.total_expenses
            )
            cash_difference = closing_data.cash_count - expected_cash

            existing.sales_total = daily_summary.total_sales
            existing.expenses_total = daily_summary.total_expenses
            existing.cash_count = closing_data.cash_count
            existing.expected_cash = expected_cash
            existing.cash_difference = cash_difference
            existing.notes = closing_data.notes
            existing.closed_by = user_id
            existing.closed_at = func.now()

            db.commit()
            db.refresh(existing)
            db_closing = existing
        else:
            # Create new closing record if no opening exists
            db_closing = cash_closing.create_closing(
                db,
                closing_data=closing_data,
                sales_total=daily_summary.total_sales,
                expenses_total=daily_summary.total_expenses,
                closed_by=user_id,
            )

        # Validate cash difference
        is_valid, warning = self.validate_cash_difference(db_closing.cash_difference)
        if not is_valid:
            logger.warning(f"Closing created with cash difference warning: {warning}")

        logger.info(
            f"Closing created with ID {db_closing.id}, "
            f"difference: ${db_closing.cash_difference:.2f}"
        )

        return CashClosingResponse.model_validate(db_closing)

    def finalize_closing(
        self, db: Session, closing_id: int, user_id: int
    ) -> CashClosingResponse:
        """Finalize a cash closing, making it immutable.

        Args:
            db: Database session.
            closing_id: ID of closing to finalize.
            user_id: ID of user finalizing the closing.

        Returns:
            Finalized closing details.

        Raises:
            ValueError: If closing not found or already finalized.
        """
        logger.info(f"Finalizing closing {closing_id} by user {user_id}")

        # Get current closing
        db_closing = cash_closing.get(db, closing_id)
        if not db_closing:
            raise ValueError(f"Closing with ID {closing_id} not found")

        if db_closing.is_finalized:
            raise ValueError(f"Closing {closing_id} is already finalized")

        # Finalize the closing
        finalized_closing = cash_closing.finalize_closing(db, closing_id=closing_id)
        if not finalized_closing:
            raise ValueError(f"Failed to finalize closing {closing_id}")

        logger.info(f"Closing {closing_id} finalized successfully")
        return CashClosingResponse.model_validate(finalized_closing)

    def check_can_process_sale(self, db: Session, sale_date: date) -> tuple[bool, str]:
        """Check if sales can be processed for a given date.

        Args:
            db: Database session.
            sale_date: Date to check for sale processing.

        Returns:
            Tuple of (can_process, reason_if_not).
        """
        # Check if cash register is open for the date
        if not cash_closing.is_cash_register_open(db, target_date=sale_date):
            return (
                False,
                f"Cash register must be opened before processing sales for {sale_date}",
            )

        # Check if the date has been closed and finalized
        if cash_closing.is_day_closed(db, target_date=sale_date):
            return False, f"Sales cannot be processed - day {sale_date} has been closed"

        return True, ""

    def get_closing_by_date(
        self, db: Session, closing_date: date
    ) -> Optional[CashClosingResponse]:
        """Get closing record for a specific date.

        Args:
            db: Database session.
            closing_date: Date to retrieve closing for.

        Returns:
            Closing details if found, None otherwise.
        """
        db_closing = cash_closing.get_by_date(db, closing_date=closing_date)
        if db_closing:
            return CashClosingResponse.model_validate(db_closing)
        return None

    def get_current_closing_status(
        self, db: Session, target_date: date = None
    ) -> dict[str, any]:
        """Get current closing status for today or specified date.

        Args:
            db: Database session.
            target_date: Date to check status for (default: today).

        Returns:
            Status information including whether closing exists and daily summary.
        """
        if target_date is None:
            target_date = date.today()

        # Get daily summary
        daily_summary = self.calculate_daily_totals(db, target_date)

        # Check if closing exists
        existing_closing = self.get_closing_by_date(db, target_date)

        # Get opening balance for the day
        # If there's an existing closing/opening record for today, use its opening balance
        if existing_closing and existing_closing.opening_balance is not None:
            opening_balance = existing_closing.opening_balance
        else:
            # Otherwise, use the cash count from the last closing
            last_closing = cash_closing.get_last_closing(db)
            opening_balance = (
                last_closing.cash_count if last_closing else Decimal("0.00")
            )

        return {
            "date": target_date,
            "has_closing": existing_closing is not None,
            "closing": existing_closing,
            "daily_summary": daily_summary,
            "opening_balance": opening_balance,
            "can_create_closing": not daily_summary.has_closing,
            "is_open": cash_closing.is_cash_register_open(db, target_date=target_date),
        }

    def get_recent_closings(
        self, db: Session, limit: int = 10
    ) -> list[CashClosingResponse]:
        """Get recent finalized closings.

        Args:
            db: Database session.
            limit: Maximum number of closings to return.

        Returns:
            List of recent closings.
        """
        db_closings = cash_closing.get_finalized_closings(db, limit=limit)
        return [CashClosingResponse.model_validate(closing) for closing in db_closings]


# Create service instance
cash_closing_service = CashClosingService()
