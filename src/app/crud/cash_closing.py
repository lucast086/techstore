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
        # Calculate expected cash (only cash transactions affect cash balance)
        expected_cash = (
            closing_data.opening_balance
            + closing_data.sales_cash
            - closing_data.expenses_cash
        )
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
            # Payment method breakdown
            sales_cash=closing_data.sales_cash,
            sales_credit=closing_data.sales_credit,
            sales_transfer=closing_data.sales_transfer,
            sales_mixed=closing_data.sales_mixed,
            expenses_cash=closing_data.expenses_cash,
            expenses_transfer=closing_data.expenses_transfer,
            expenses_card=closing_data.expenses_card,
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
        """Aggregate sales and expenses for a date with payment method breakdown."""
        # Get sales summary for the date
        sales_result = (
            db.query(
                func.coalesce(func.sum(Sale.total_amount), 0).label("total_sales"),
                func.count(Sale.id).label("sales_count"),
            )
            .filter(func.date(Sale.sale_date) == target_date)
            .filter(Sale.is_voided == False)  # noqa: E712
            .first()
        )

        # Get payments by method for accurate cash calculation
        # This gets the actual amount paid, not the total sale amount
        from app.models.payment import Payment, PaymentType

        # Get ALL payments for the date, including:
        # 1. Payments associated with sales (Payment.sale_id is not null)
        # 2. Payments for customer accounts/debt (Payment.sale_id is null)
        # We use created_at for payments without sales, and sale_date for payments with sales

        # First, get payments associated with sales for this date
        sale_payments = (
            db.query(Payment.payment_method, func.sum(Payment.amount).label("amount"))
            .join(Sale, Payment.sale_id == Sale.id)
            .filter(func.date(Sale.sale_date) == target_date)
            .filter(Sale.is_voided == False)  # noqa: E712
            .filter(Payment.voided == False)  # noqa: E712
            .group_by(Payment.payment_method)
            .all()
        )

        # Then, get account payments (no sale_id) for this date - KEEP SEPARATE
        account_payments = (
            db.query(Payment.payment_method, func.sum(Payment.amount).label("amount"))
            .filter(Payment.sale_id == None)  # noqa: E711
            .filter(func.date(Payment.created_at) == target_date)
            .filter(Payment.voided == False)  # noqa: E712
            # Exclude refunds from cash calculations
            .filter(Payment.payment_type != PaymentType.refund)
            .group_by(Payment.payment_method)
            .all()
        )

        # DON'T combine - keep sale payments separate from debt payments
        payments_by_method = (
            sale_payments  # Only sales-related payments for sales totals
        )

        # Get walk-in sales (no customer, paid in full)
        walkin_sales = (
            db.query(Sale.payment_method, func.sum(Sale.total_amount).label("amount"))
            .filter(func.date(Sale.sale_date) == target_date)
            .filter(Sale.is_voided == False)  # noqa: E712
            .filter(Sale.customer_id == None)  # noqa: E711
            .filter(Sale.payment_status == "paid")
            .group_by(Sale.payment_method)
            .all()
        )

        sales_cash = Decimal("0.00")
        sales_credit = Decimal("0.00")
        sales_transfer = Decimal("0.00")
        sales_card = Decimal("0.00")  # Separate card payments

        # Consolidate payment methods from both sale and account payments
        payment_totals = {}
        for row in payments_by_method:
            method = row.payment_method
            amount = row.amount or Decimal("0.00")
            if method in payment_totals:
                payment_totals[method] += amount
            else:
                payment_totals[method] = amount

        # Calculate actual payments received by method
        for method, amount in payment_totals.items():
            if method == "cash":
                sales_cash += amount
            elif method == "transfer":
                sales_transfer += amount
            elif method == "card":
                sales_card += amount
            elif method == "account_credit":
                # Account credit used as payment
                sales_credit += amount
            elif method == "mixed":
                # Mixed payments should now be handled as separate payment records
                # This case should not occur with the new implementation
                # But keeping for backward compatibility with old data
                # Distribute to cash as fallback
                sales_cash += amount

        # Add walk-in sales (these are paid in full without Payment records)
        for row in walkin_sales:
            if row.payment_method == "cash":
                sales_cash += row.amount or Decimal("0.00")
            elif row.payment_method == "transfer":
                sales_transfer += row.amount or Decimal("0.00")
            elif row.payment_method == "card":
                sales_card += row.amount or Decimal("0.00")
            elif row.payment_method == "mixed":
                # For walk-in mixed payments, we need to get the breakdown from the Sale record
                # Get all walk-in mixed sales for this date to get the breakdown
                walkin_mixed_sales = (
                    db.query(Sale)
                    .filter(func.date(Sale.sale_date) == target_date)
                    .filter(Sale.is_voided == False)  # noqa: E712
                    .filter(Sale.customer_id == None)  # noqa: E711
                    .filter(Sale.payment_method == "mixed")
                    .all()
                )
                for sale in walkin_mixed_sales:
                    if sale.cash_amount:
                        sales_cash += sale.cash_amount
                    if sale.transfer_amount:
                        sales_transfer += sale.transfer_amount
                    if sale.card_amount:
                        sales_card += sale.card_amount
                    # Note: credit_amount for walk-in should be 0, but included for completeness
                    if sale.credit_amount:
                        sales_credit += sale.credit_amount

        # Calculate credit sales (unpaid portion of TODAY'S sales only)
        # Credit sales are the unpaid portions of sales made TODAY
        # This should NOT include payments for old debts

        # Get the total unpaid amount from today's sales
        credit_sales_result = (
            db.query(
                func.coalesce(
                    func.sum(
                        Sale.total_amount
                        - func.coalesce(
                            db.query(func.sum(Payment.amount))
                            .filter(Payment.sale_id == Sale.id)
                            .filter(Payment.voided == False)  # noqa: E712
                            .scalar_subquery(),
                            0,
                        )
                    ),
                    0,
                ).label("credit_amount")
            )
            .filter(func.date(Sale.sale_date) == target_date)
            .filter(Sale.is_voided == False)  # noqa: E712
            .filter(Sale.customer_id != None)  # noqa: E711 - Only sales to registered customers can have credit
            .first()
        )

        sales_credit = credit_sales_result.credit_amount or Decimal("0.00")

        # Get expenses summary for the date
        expenses_result = (
            db.query(
                func.coalesce(func.sum(Expense.amount), 0).label("total_expenses"),
                func.count(Expense.id).label("expenses_count"),
            )
            .filter(Expense.expense_date == target_date)
            .first()
        )

        # Get expenses by payment method
        expenses_by_method = (
            db.query(Expense.payment_method, func.sum(Expense.amount).label("amount"))
            .filter(Expense.expense_date == target_date)
            .group_by(Expense.payment_method)
            .all()
        )

        expenses_cash = Decimal("0.00")
        expenses_transfer = Decimal("0.00")
        expenses_card = Decimal("0.00")

        for row in expenses_by_method:
            if row.payment_method == "cash":
                expenses_cash = row.amount or Decimal("0.00")
            elif row.payment_method == "transfer":
                expenses_transfer = row.amount or Decimal("0.00")
            elif row.payment_method == "card":
                expenses_card = row.amount or Decimal("0.00")

        total_expenses = expenses_result.total_expenses or Decimal("0.00")
        expenses_count = expenses_result.expenses_count or 0

        # Calculate debt payments separately (pagos de cuentas corrientes)
        debt_payments_cash = Decimal("0.00")
        debt_payments_transfer = Decimal("0.00")
        debt_payments_card = Decimal("0.00")

        for row in account_payments:
            if row.payment_method == "cash":
                debt_payments_cash += row.amount or Decimal("0.00")
            elif row.payment_method == "transfer":
                debt_payments_transfer += row.amount or Decimal("0.00")
            elif row.payment_method == "card":
                debt_payments_card += row.amount or Decimal("0.00")

        debt_payments_total = (
            debt_payments_cash + debt_payments_transfer + debt_payments_card
        )

        # Check if closing exists
        has_closing = self.check_closing_exists(db, closing_date=target_date)

        return DailySummary(
            date=target_date,
            total_sales=sales_result.total_sales or Decimal("0.00"),
            total_expenses=total_expenses,
            sales_count=sales_result.sales_count or 0,
            expenses_count=expenses_count,
            has_closing=has_closing,
            # Payment method breakdown
            sales_cash=sales_cash,
            sales_credit=sales_credit,
            sales_transfer=sales_transfer,
            sales_mixed=sales_card,  # Using sales_mixed field to store card payments
            expenses_cash=expenses_cash,
            expenses_transfer=expenses_transfer,
            expenses_card=expenses_card,
            # Debt payments (pagos de cuentas corrientes)
            debt_payments_cash=debt_payments_cash,
            debt_payments_transfer=debt_payments_transfer,
            debt_payments_card=debt_payments_card,
            debt_payments_total=debt_payments_total,
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
            # Initialize payment method breakdowns to zero
            sales_cash=Decimal("0.00"),
            sales_credit=Decimal("0.00"),
            sales_transfer=Decimal("0.00"),
            sales_mixed=Decimal("0.00"),
            expenses_cash=Decimal("0.00"),
            expenses_transfer=Decimal("0.00"),
            expenses_card=Decimal("0.00"),
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


# Create instance to use throughout the application
cash_closing = CRUDCashClosing(CashClosing)
