"""Debt service for handling customer debt generation and management."""

import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.sale import Sale
from app.services.customer_account_service import customer_account_service

logger = logging.getLogger(__name__)


class DebtService:
    """Service for handling customer debt operations."""

    def generate_debt_for_partial_payment(
        self,
        db: Session,
        sale: Sale,
        amount_paid: Decimal,
    ) -> tuple[bool, str]:
        """Generate debt when customer pays less than total amount.

        Args:
            db: Database session.
            sale: Sale object.
            amount_paid: Amount customer actually paid.

        Returns:
            Tuple of (success, message).
        """
        if not sale.customer_id:
            return False, "Cannot generate debt for walk-in customers"

        if amount_paid >= sale.total_amount:
            return False, "No debt to generate - payment covers full amount"

        debt_amount = sale.total_amount - amount_paid

        try:
            # Update sale payment status based on partial payment
            if amount_paid > Decimal("0"):
                sale.payment_status = "partial"
            else:
                sale.payment_status = "pending"

            # Create payment record if amount was paid
            if amount_paid > Decimal("0"):
                from app.crud.payment import payment_crud
                from app.models.payment import Payment

                payment = Payment(
                    customer_id=sale.customer_id,
                    sale_id=sale.id,
                    amount=amount_paid,
                    payment_method=sale.payment_method or "cash",
                    receipt_number=payment_crud.generate_receipt_number(db),
                    received_by_id=sale.user_id,
                    notes=f"Partial payment for sale {sale.invoice_number}",
                )
                db.add(payment)

            # The debt is automatically tracked via the sale being unpaid/partially paid
            # and the balance service calculation

            db.commit()

            logger.info(
                f"Debt of ${debt_amount} generated for customer {sale.customer_id} "
                f"from sale {sale.invoice_number}"
            )

            return True, f"Debt of ${debt_amount} generated for customer"

        except Exception as e:
            db.rollback()
            logger.error(f"Error generating debt: {str(e)}")
            return False, f"Error generating debt: {str(e)}"

    def calculate_customer_total_debt(self, db: Session, customer_id: int) -> Decimal:
        """Calculate total debt for a customer.

        Args:
            db: Database session.
            customer_id: Customer ID.

        Returns:
            Total debt amount (positive number).
        """
        # Use CustomerAccount as single source of truth
        # positive balance = debt, negative = credit
        balance_info = customer_account_service.get_balance_summary(db, customer_id)
        balance = balance_info["current_balance"]
        return balance if balance > 0 else Decimal("0")

    def get_debt_notification_message(
        self, db: Session, customer_id: int, debt_amount: Decimal
    ) -> str:
        """Generate notification message for debt creation.

        Args:
            db: Database session.
            customer_id: Customer ID.
            debt_amount: Amount of new debt.

        Returns:
            Formatted notification message.
        """
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        customer_name = customer.name if customer else "Unknown Customer"

        total_debt = self.calculate_customer_total_debt(db, customer_id)

        return (
            f"Debt of ${debt_amount:,.2f} generated for {customer_name}. "
            f"Total customer debt: ${total_debt:,.2f}"
        )

    def validate_partial_payment(
        self,
        amount_paid: Optional[Decimal],
        total_amount: Decimal,
        payment_method: Optional[str],
    ) -> tuple[bool, str]:
        """Validate partial payment parameters.

        Args:
            amount_paid: Amount customer is paying.
            total_amount: Total sale amount.
            payment_method: Payment method used.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if amount_paid is None:
            return True, ""  # Full payment assumed

        if amount_paid < Decimal("0"):
            return False, "Amount paid cannot be negative"

        if amount_paid > total_amount:
            return (
                False,
                f"Amount paid (${amount_paid}) cannot exceed total amount (${total_amount})",
            )

        # All payment methods can be partial now
        return True, ""


# Global instance
debt_service = DebtService()
