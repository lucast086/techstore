"""Sales service for processing sales with payments."""

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud.payment import payment_crud
from app.crud.sale import sale_crud
from app.models.payment import Payment, PaymentType
from app.models.sale import Sale
from app.schemas.sale import SaleCreate
from app.services.customer_account_service import customer_account_service

logger = logging.getLogger(__name__)


class SalesService:
    """Service for handling sales processing with integrated payments."""

    def process_sale_with_payment(
        self,
        db: Session,
        sale_data: SaleCreate,
        user_id: int,
    ) -> Sale:
        """Process a sale and automatically create payment if amount_paid is provided.

        This method orchestrates:
        1. Sale creation (creates SALE transaction - debt)
        2. Payment creation if amount_paid > 0 (creates PAYMENT transaction)
        3. Updates sale payment status based on payment

        Args:
            db: Database session
            sale_data: Sale creation data including amount_paid
            user_id: ID of user processing the sale

        Returns:
            Created sale with payment information

        Raises:
            ValueError: If sale validation fails
        """
        logger.info(
            f"Processing sale with payment. Customer: {sale_data.customer_id}, "
            f"Payment method: {sale_data.payment_method}, "
            f"Amount paid: {sale_data.amount_paid}"
        )

        # Step 1: Create the sale (this creates SALE transaction - debt)
        # We implement this directly to avoid circular dependency
        from app.crud.sale import sale_crud  # Import here to get helper methods

        # Use the internal method to avoid circular dependency
        sale = sale_crud._create_sale_internal(
            db=db, sale_in=sale_data, user_id=user_id
        )
        logger.info(
            f"Sale created: {sale.invoice_number}, Total: ${sale.total_amount}, "
            f"Customer: {sale.customer_id}"
        )

        # Step 2: Process payment if amount_paid is provided and not on account or mixed
        # "account" or "account_credit" payment methods mean sale on credit, no immediate payment
        # "mixed" payment method means multiple payment methods will be handled separately
        if (
            sale_data.amount_paid
            and sale_data.amount_paid > 0
            and sale_data.payment_method not in ("account", "account_credit", "mixed")
        ):
            # Determine actual payment amount (cap at total, rest is change)
            payment_amount = min(sale_data.amount_paid, sale.total_amount)
            change_amount = (
                sale_data.amount_paid - sale.total_amount
                if sale_data.amount_paid > sale.total_amount
                else Decimal("0")
            )

            if change_amount > 0:
                logger.info(
                    f"Change amount: ${change_amount} for sale {sale.invoice_number}"
                )
                sale.change_amount = change_amount

            # Map payment methods correctly
            payment_method = sale_data.payment_method
            if payment_method in ("account", "account_credit"):
                # "account" or "account_credit" means on credit, no immediate payment
                logger.info(
                    f"Sale {sale.invoice_number} is on account/credit. No payment created."
                )
                return sale

            # Create payment record
            logger.info(
                f"Creating payment: ${payment_amount} via {payment_method} "
                f"for sale {sale.invoice_number}"
            )

            # Generate receipt number
            receipt_number = payment_crud.generate_receipt_number(db)

            # Create payment object
            payment = Payment(
                customer_id=sale.customer_id if sale.customer_id else None,
                sale_id=sale.id,
                amount=payment_amount,
                payment_method=payment_method,
                payment_type=PaymentType.payment.value,
                receipt_number=receipt_number,
                received_by_id=user_id,
                notes=f"Payment for sale {sale.invoice_number}",
            )
            db.add(payment)
            db.flush()  # Get payment.id without committing

            logger.info(
                f"Payment created: {payment.receipt_number}, Amount: ${payment.amount}"
            )

            # Step 3: Record payment in customer account (if customer exists)
            if sale.customer_id:
                try:
                    customer_account_service.record_payment(db, payment, user_id)
                    logger.info(
                        f"Recorded PAYMENT transaction: ${payment_amount} "
                        f"for customer {sale.customer_id}"
                    )
                except Exception as e:
                    logger.error(f"Failed to record payment in account system: {e}")
                    db.rollback()
                    raise ValueError(f"Failed to record payment transaction: {e}")

            # Step 4: Update sale payment status
            self._update_sale_payment_status(db, sale)
        else:
            # For credit sales (account or account_credit), log but don't create payment
            if sale_data.payment_method in ("account", "account_credit"):
                logger.info(
                    f"Sale {sale.invoice_number} is on credit ({sale_data.payment_method}). "
                    f"No Payment record created. Amount: ${sale_data.amount_paid or 0}"
                )

        # Commit all changes
        db.commit()
        db.refresh(sale)

        # Load relationships for complete sale object
        sale = sale_crud.get_with_details(db, sale.id)

        logger.info(
            f"Sale processing complete: {sale.invoice_number}, "
            f"Payment status: {sale.payment_status}, "
            f"Balance due: ${sale.balance_due if sale.balance_due else 0}"
        )

        return sale

    def _update_sale_payment_status(self, db: Session, sale: Sale) -> None:
        """Update sale payment status based on payments received.

        Args:
            db: Database session
            sale: Sale object to update
        """
        from app.models.customer_account import CustomerTransaction, TransactionType

        # Get all payments for this sale
        payments = (
            db.query(Payment)
            .filter(Payment.sale_id == sale.id, Payment.voided.is_(False))
            .all()
        )

        # Get all credit applications for this sale
        credit_applications = (
            db.query(CustomerTransaction)
            .filter(
                CustomerTransaction.reference_type == "sale",
                CustomerTransaction.reference_id == sale.id,
                CustomerTransaction.transaction_type
                == TransactionType.CREDIT_APPLICATION,
            )
            .all()
        )

        # Calculate total paid (payments + credit applications)
        total_paid = sum(payment.amount for payment in payments) + sum(
            credit.amount for credit in credit_applications
        )

        # Update payment status and amounts
        if total_paid >= sale.total_amount:
            sale.payment_status = "paid"
            sale.paid_amount = sale.total_amount
            # balance_due is calculated property, no need to set
        elif total_paid > 0:
            sale.payment_status = "partial"
            sale.paid_amount = total_paid
            # balance_due is calculated property, no need to set
        else:
            sale.payment_status = "pending"
            sale.paid_amount = Decimal("0")
            # balance_due is calculated property, no need to set

        db.add(sale)
        logger.info(
            f"Updated sale {sale.invoice_number}: Status={sale.payment_status}, "
            f"Paid=${sale.paid_amount}, Due=${sale.balance_due}"
        )

    def process_mixed_payment(
        self,
        db: Session,
        sale_data: SaleCreate,
        payment_methods: dict,
        user_id: int,
    ) -> Sale:
        """Process a sale with multiple payment methods.

        Args:
            db: Database session
            sale_data: Sale creation data
            payment_methods: Dict with payment method amounts
                e.g., {"cash": 50.00, "card": 30.00, "credit": 20.00}
            user_id: ID of user processing the sale

        Returns:
            Created sale with payments

        Raises:
            ValueError: If payment validation fails
        """
        # Create the sale first
        sale = sale_crud.create_sale(db=db, sale_in=sale_data, user_id=user_id)

        # Process each payment method
        for method, amount in payment_methods.items():
            if amount and amount > 0:
                if method == "credit":
                    # Apply customer credit
                    customer_account_service.apply_credit(
                        db=db,
                        customer_id=sale.customer_id,
                        amount=amount,
                        sale_id=sale.id,
                        created_by_id=user_id,
                        notes=f"Credit applied to sale {sale.invoice_number}",
                    )
                else:
                    # Create regular payment
                    receipt_number = payment_crud.generate_receipt_number(db)
                    payment = Payment(
                        customer_id=sale.customer_id,
                        sale_id=sale.id,
                        amount=amount,
                        payment_method=method,
                        payment_type=PaymentType.payment.value,
                        receipt_number=receipt_number,
                        received_by_id=user_id,
                        notes=f"Mixed payment ({method}) for sale {sale.invoice_number}",
                    )
                    db.add(payment)
                    db.flush()

                    if sale.customer_id:
                        customer_account_service.record_payment(db, payment, user_id)

        # Update sale payment status
        self._update_sale_payment_status(db, sale)

        db.commit()
        db.refresh(sale)

        return sale_crud.get_with_details(db, sale.id)


# Global instance
sales_service = SalesService()
