"""CRUD operations for cash closings."""

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.cash_closing import CashClosing
from app.models.expense import Expense
from app.models.sale import Sale
from app.schemas.cash_closing import CashClosingCreate, CashClosingUpdate, DailySummary
from app.utils.timezone import local_date_to_utc_range


class CRUDCashClosing(CRUDBase[CashClosing, CashClosingCreate, CashClosingUpdate]):
    """CRUD operations for cash closings."""

    def get(self, db: Session, id: int) -> Optional[CashClosing]:
        """Get a cash closing by ID with relationships loaded."""
        return (
            db.query(CashClosing)
            .options(joinedload(CashClosing.user), joinedload(CashClosing.opener))
            .filter(CashClosing.id == id)
            .first()
        )

    def get_by_date(self, db: Session, *, closing_date: date) -> Optional[CashClosing]:
        """Retrieve closing for specific date."""
        return (
            db.query(CashClosing)
            .options(joinedload(CashClosing.user), joinedload(CashClosing.opener))
            .filter(CashClosing.closing_date == closing_date)
            .first()
        )

    def get_last_closing(self, db: Session) -> Optional[CashClosing]:
        """Get most recent closing for opening balance."""
        return (
            db.query(CashClosing)
            .options(joinedload(CashClosing.user), joinedload(CashClosing.opener))
            .filter(CashClosing.is_finalized == True)  # noqa: E712
            .order_by(CashClosing.closing_date.desc())
            .first()
        )

    def create_closing(
        self,
        db: Session,
        *,
        closing_data: CashClosingCreate,
        sales_total: Decimal,
        expenses_total: Decimal,
        closed_by: int,
    ) -> CashClosing:
        """Create new daily closing with calculated values."""
        # Calculate expected cash and difference
        expected_cash = closing_data.opening_balance + sales_total - expenses_total
        cash_difference = closing_data.cash_count - expected_cash

        # Create closing record
        db_obj = CashClosing(
            closing_date=closing_data.closing_date,
            opening_balance=closing_data.opening_balance,
            sales_total=sales_total,
            expenses_total=expenses_total,
            cash_count=closing_data.cash_count,
            expected_cash=expected_cash,
            cash_difference=cash_difference,
            notes=closing_data.notes,
            closed_by=closed_by,
            is_finalized=False,  # Always start as draft
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def finalize_closing(
        self, db: Session, *, closing_id: int
    ) -> Optional[CashClosing]:
        """Mark closing as final (immutable)."""
        db_obj = self.get(db, closing_id)
        if db_obj and not db_obj.is_finalized:
            db_obj.is_finalized = True
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def check_closing_exists(self, db: Session, *, closing_date: date) -> bool:
        """Verify if date already has closing."""
        return (
            db.query(CashClosing)
            .filter(CashClosing.closing_date == closing_date)
            .first()
            is not None
        )

    def get_daily_summary(self, db: Session, *, target_date: date) -> DailySummary:
        """Aggregate sales and expenses for a date."""
        # Convert local date to UTC range for querying
        utc_start, utc_end = local_date_to_utc_range(target_date)

        # Get sales summary for the date (sale_date is stored in UTC)
        sales_result = (
            db.query(
                func.coalesce(func.sum(Sale.total_amount), 0).label("total_sales"),
                func.count(Sale.id).label("sales_count"),
            )
            .filter(Sale.sale_date >= utc_start)
            .filter(Sale.sale_date <= utc_end)
            .filter(Sale.is_voided == False)  # noqa: E712
            .first()
        )

        # Get repair payments summary for the date (tracked separately, not as sales)
        from app.models.repair import Repair

        repairs_delivered_result = (
            db.query(
                func.count(Repair.id).label("repairs_count"),
                func.coalesce(func.sum(Repair.final_cost), 0).label("repairs_total"),
            )
            .filter(Repair.delivered_date >= utc_start)
            .filter(Repair.delivered_date <= utc_end)
            .filter(Repair.final_cost.isnot(None))
            .first()
        )

        # Get expenses summary for the date
        expenses_result = (
            db.query(
                func.coalesce(func.sum(Expense.amount), 0).label("total_expenses"),
                func.count(Expense.id).label("expenses_count"),
            )
            .filter(Expense.expense_date == target_date)
            .first()
        )

        total_expenses = expenses_result.total_expenses or Decimal("0.00")
        expenses_count = expenses_result.expenses_count or 0

        # Check if closing exists
        has_closing = self.check_closing_exists(db, closing_date=target_date)

        # Sales and repairs are tracked separately
        return DailySummary(
            date=target_date,
            total_sales=sales_result.total_sales or Decimal("0.00"),
            total_expenses=total_expenses,
            sales_count=sales_result.sales_count or 0,
            expenses_count=expenses_count,
            has_closing=has_closing,
            # Repair info tracked separately for reporting
            repairs_delivered_count=repairs_delivered_result.repairs_count
            if repairs_delivered_result
            else 0,
            repairs_total=repairs_delivered_result.repairs_total
            if repairs_delivered_result
            else Decimal("0.00"),
        )

    def get_finalized_closings(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[CashClosing]:
        """Get finalized closings with pagination."""
        return (
            db.query(CashClosing)
            .options(joinedload(CashClosing.user), joinedload(CashClosing.opener))
            .filter(CashClosing.is_finalized == True)  # noqa: E712
            .order_by(CashClosing.closing_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_closings_by_date_range(
        self, db: Session, *, start_date: date, end_date: date
    ) -> list[CashClosing]:
        """Get closings within date range."""
        return (
            db.query(CashClosing)
            .options(joinedload(CashClosing.user), joinedload(CashClosing.opener))
            .filter(
                and_(
                    CashClosing.closing_date >= start_date,
                    CashClosing.closing_date <= end_date,
                )
            )
            .order_by(CashClosing.closing_date.desc())
            .all()
        )

    def is_day_closed(self, db: Session, *, target_date: date) -> bool:
        """Check if a specific date has been finalized."""
        closing = self.get_by_date(db, closing_date=target_date)
        return closing is not None and closing.is_finalized

    def get_unfinalized_register(self, db: Session) -> Optional[CashClosing]:
        """Get any unfinalized cash register from any date.

        Returns:
            The first unfinalized cash register found, or None if all are closed.
        """
        return (
            db.query(CashClosing)
            .filter(CashClosing.is_finalized.is_(False))
            .order_by(CashClosing.closing_date.desc())
            .first()
        )

    def open_cash_register(
        self,
        db: Session,
        *,
        target_date: date,
        opening_balance: Decimal,
        opened_by: int,
    ) -> CashClosing:
        """Open cash register for the day."""
        # FIRST: Check if there's any unfinalized register from any date
        unfinalized = self.get_unfinalized_register(db)
        if unfinalized:
            raise ValueError(
                f"Cannot open new cash register. "
                f"Please close the cash register from {unfinalized.closing_date.strftime('%Y-%m-%d')} first."
            )

        # THEN: Check if already exists for this specific date
        existing = self.get_by_date(db, closing_date=target_date)
        if existing:
            # If it's finalized, we cannot open again
            if existing.is_finalized:
                raise ValueError(
                    f"Cash register was already closed for {target_date}. Cannot open again."
                )
            # If it's already open (not finalized), we cannot open again
            else:
                raise ValueError(f"Cash register is already open for {target_date}")

        # Create opening record
        db_obj = CashClosing(
            closing_date=target_date,
            opening_balance=opening_balance,
            sales_total=Decimal("0.00"),
            expenses_total=Decimal("0.00"),
            cash_count=opening_balance,  # Initially same as opening
            expected_cash=opening_balance,
            cash_difference=Decimal("0.00"),
            opened_at=func.now(),
            opened_by=opened_by,
            closed_by=opened_by,  # Set to same user initially
            is_finalized=False,
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def is_cash_register_open(self, db: Session, *, target_date: date) -> bool:
        """Check if cash register is open for a specific date."""
        closing = self.get_by_date(db, closing_date=target_date)
        # Cash is open if there's a record with opened_at but not finalized
        return (
            closing is not None
            and closing.opened_at is not None
            and not closing.is_finalized
        )

    def close_cash_register(
        self,
        db: Session,
        *,
        target_date: date,
        cash_count: Decimal,
        closed_by: int,
        notes: Optional[str] = None,
    ) -> CashClosing:
        """Close the cash register for the day.

        Args:
            db: Database session.
            target_date: Date to close register for.
            cash_count: Actual cash counted.
            closed_by: ID of user closing the register.
            notes: Optional closing notes.

        Returns:
            Updated cash closing record.

        Raises:
            ValueError: If register was not opened or already closed.
        """
        # Check if register is open
        existing = self.get_by_date(db, closing_date=target_date)

        if not existing:
            raise ValueError(
                f"Cannot close cash register for {target_date}. "
                "The cash register was never opened for this date."
            )

        if not existing.opened_at:
            raise ValueError(
                f"Cannot close cash register for {target_date}. "
                "The cash register was never properly opened."
            )

        if existing.is_finalized:
            raise ValueError(
                f"Cash register for {target_date} is already closed and finalized."
            )

        # Get daily totals
        from app.models.expense import Expense
        from app.models.sale import Sale

        # Convert local date to UTC range for querying
        utc_start, utc_end = local_date_to_utc_range(target_date)

        # Calculate sales total (sale_date is stored in UTC)
        sales_result = (
            db.query(func.coalesce(func.sum(Sale.total_amount), 0))
            .filter(Sale.sale_date >= utc_start)
            .filter(Sale.sale_date <= utc_end)
            .filter(Sale.is_voided == False)  # noqa: E712
            .scalar()
        )
        sales_total = sales_result or Decimal("0.00")

        # Calculate expenses total
        expenses_result = (
            db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(Expense.expense_date == target_date)
            .scalar()
        )
        expenses_total = expenses_result or Decimal("0.00")

        # Calculate expected cash and difference
        expected_cash = existing.opening_balance + sales_total - expenses_total
        cash_difference = cash_count - expected_cash

        # Update the closing record
        existing.sales_total = sales_total
        existing.expenses_total = expenses_total
        existing.cash_count = cash_count
        existing.expected_cash = expected_cash
        existing.cash_difference = cash_difference
        existing.closed_by = closed_by
        existing.closed_at = func.now()
        if notes:
            existing.notes = notes

        db.commit()
        db.refresh(existing)
        return existing


# Create instance to use throughout the application
cash_closing = CRUDCashClosing(CashClosing)
