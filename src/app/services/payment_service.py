"""Payment service for processing customer payments."""

import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.payment import payment_crud
from app.crud.sale import sale_crud
from app.models.payment import Payment
from app.models.sale import Sale
from app.schemas.payment import PaymentCreate, PaymentMethodDetail
from app.services.balance_service import balance_service

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for handling payment processing logic."""

    def process_payment(
        self,
        db: Session,
        customer_id: int,
        sale_id: Optional[int],
        payment_data: PaymentCreate,
        user_id: int,
        allow_overpayment: bool = False,
    ) -> Payment:
        """Process a payment for a customer.

        Args:
            db: Database session.
            customer_id: ID of the customer making payment.
            sale_id: Optional ID of related sale.
            payment_data: Payment details.
            user_id: ID of user processing payment.
            allow_overpayment: Whether to allow payment exceeding debt.

        Returns:
            Created payment object.

        Raises:
            ValueError: If payment validation fails.
        """
        from app.models.payment import PaymentType

        # Validate payment amount and determine payment type
        payment_type = self.validate_payment_amount(
            db, customer_id, payment_data.amount, allow_overpayment
        )

        # If it's an advance payment, require notes
        if payment_type == PaymentType.ADVANCE_PAYMENT and not payment_data.notes:
            raise ValueError(
                "Notes are required for advance payments. Please specify the purpose of this advance payment."
            )

        # Set the payment type if not already specified
        if not payment_data.payment_type:
            payment_data.payment_type = payment_type

        # Create payment record
        payment = payment_crud.create(
            db=db, customer_id=customer_id, payment=payment_data, received_by_id=user_id
        )

        # Update sale_id if provided
        if sale_id:
            payment.sale_id = sale_id
            db.commit()

            # Update sale payment status
            sale = sale_crud.get_with_details(db, sale_id)
            if sale:
                self.update_sale_payment_status(db, sale)

        logger.info(
            f"Payment processed: {payment.receipt_number} for customer {customer_id}"
        )

        return payment

    def process_mixed_payment(
        self,
        db: Session,
        customer_id: int,
        sale_id: Optional[int],
        payment_methods: list[PaymentMethodDetail],
        notes: Optional[str],
        user_id: int,
        allow_overpayment: bool = False,
    ) -> Payment:
        """Process a payment with multiple payment methods.

        Args:
            db: Database session.
            customer_id: ID of the customer making payment.
            sale_id: Optional ID of related sale.
            payment_methods: List of payment method details.
            notes: Optional payment notes.
            user_id: ID of user processing payment.
            allow_overpayment: Whether to allow payment exceeding debt.

        Returns:
            Created payment object.

        Raises:
            ValueError: If payment validation fails.
        """
        # Calculate total amount
        total_amount = sum(pm.amount for pm in payment_methods)

        # Validate total amount
        self.validate_payment_amount(db, customer_id, total_amount, allow_overpayment)

        # Create combined reference numbers
        reference_numbers = []
        for pm in payment_methods:
            if pm.reference_number:
                reference_numbers.append(f"{pm.payment_method}: {pm.reference_number}")

        combined_reference = "; ".join(reference_numbers) if reference_numbers else None

        # Format notes with method breakdown
        method_breakdown = ", ".join(
            f"{pm.payment_method}: ${pm.amount}" for pm in payment_methods
        )
        full_notes = f"Mixed payment ({method_breakdown})"
        if notes:
            full_notes += f" - {notes}"

        # Create single payment record with mixed method
        payment_data = PaymentCreate(
            amount=total_amount,
            payment_method="mixed",
            reference_number=combined_reference,
            notes=full_notes,
        )

        return self.process_payment(
            db, customer_id, sale_id, payment_data, user_id, allow_overpayment
        )

    def validate_payment_amount(
        self,
        db: Session,
        customer_id: int,
        payment_amount: Decimal,
        allow_overpayment: bool = False,
    ):
        """Validate payment amount against customer balance and determine payment type.

        Args:
            db: Database session.
            customer_id: ID of the customer.
            payment_amount: Amount being paid.
            allow_overpayment: Whether to allow overpayment.

        Returns:
            PaymentType: The determined type of payment.

        Raises:
            ValueError: If payment amount is invalid.
        """
        from app.models.payment import PaymentType

        # Get current balance (negative means customer owes money)
        current_balance = balance_service.calculate_balance(db, customer_id)

        # Determine payment type based on balance
        if current_balance >= 0:
            # Customer has no debt or has credit - this is an advance payment
            return PaymentType.ADVANCE_PAYMENT
        else:
            # Customer has debt
            debt_amount = abs(current_balance)
            if payment_amount > debt_amount and not allow_overpayment:
                raise ValueError(
                    f"Payment amount (${payment_amount}) exceeds outstanding balance (${debt_amount})"
                )
            return PaymentType.PAYMENT

    def update_sale_payment_status(self, db: Session, sale: Sale) -> None:
        """Update sale payment status based on payments received.

        Args:
            db: Database session.
            sale: Sale object to update.
        """
        # Calculate total paid for this sale
        total_paid = sum(
            payment.amount for payment in sale.payments if not payment.voided
        )

        if total_paid >= sale.total_amount:
            sale.payment_status = "paid"
        elif total_paid > 0:
            sale.payment_status = "partial"
        else:
            sale.payment_status = "pending"

        db.commit()
        logger.info(
            f"Updated sale {sale.invoice_number} payment status to {sale.payment_status}"
        )

    def generate_receipt_number(self, db: Session) -> str:
        """Generate unique payment receipt number.

        Args:
            db: Database session.

        Returns:
            Generated receipt number.
        """
        return payment_crud.generate_receipt_number(db)


# Global instance
payment_service = PaymentService()
