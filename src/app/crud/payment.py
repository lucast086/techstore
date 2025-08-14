"""Payment CRUD operations for TechStore SaaS."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate


class PaymentCRUD:
    """CRUD operations for Payment model."""

    def create(
        self,
        db: Session,
        customer_id: int,
        payment: PaymentCreate,
        received_by_id: int,
        sale_id: int | None = None,
    ) -> Payment:
        """Record new payment."""
        # Generate receipt number
        receipt_number = self.generate_receipt_number(db)

        # Create payment with type if provided
        payment_data = {
            "customer_id": customer_id,
            "sale_id": sale_id,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "reference_number": payment.reference_number,
            "notes": payment.notes,
            "receipt_number": receipt_number,
            "received_by_id": received_by_id,
        }

        # Add payment_type if it's in the schema
        if hasattr(payment, "payment_type") and payment.payment_type:
            payment_data["payment_type"] = payment.payment_type

        db_payment = Payment(**payment_data)

        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)

        return db_payment

    def generate_receipt_number(self, db: Session) -> str:
        """Generate unique receipt number: PAY-YYYY-NNNNN."""
        year = datetime.now().year
        prefix = f"PAY-{year}"

        # Get count of payments this year
        count = (
            db.query(func.count(Payment.id))
            .filter(Payment.receipt_number.like(f"{prefix}%"))
            .scalar()
            or 0
        )

        return f"{prefix}-{str(count + 1).zfill(5)}"

    def get(self, db: Session, payment_id: int) -> Payment | None:
        """Get payment by ID."""
        return db.query(Payment).filter(Payment.id == payment_id).first()

    def get_by_receipt(self, db: Session, receipt_number: str) -> Payment | None:
        """Get payment by receipt number."""
        return (
            db.query(Payment).filter(Payment.receipt_number == receipt_number).first()
        )

    def get_customer_payments(
        self, db: Session, customer_id: int, include_voided: bool = False
    ) -> list[Payment]:
        """Get all payments for a customer."""
        query = db.query(Payment).filter(Payment.customer_id == customer_id)

        if not include_voided:
            query = query.filter(Payment.voided.is_(False))

        return query.order_by(Payment.created_at.desc()).all()

    def get_customer_payment_total(
        self, db: Session, customer_id: int, include_voided: bool = False
    ) -> float:
        """Get total payment amount for a customer.

        Calculates: (PAYMENT + ADVANCE_PAYMENT) - CREDIT_APPLICATION
        This gives the net credit/debt position.
        """
        from app.models.payment import PaymentType

        # Get payments that add to balance (money IN)
        payments_in_query = db.query(func.sum(Payment.amount)).filter(
            Payment.customer_id == customer_id,
            Payment.payment_type.in_(
                [PaymentType.payment.value, PaymentType.advance_payment.value]
            ),
        )

        # Get credit applications (credit OUT)
        credit_out_query = db.query(func.sum(Payment.amount)).filter(
            Payment.customer_id == customer_id,
            Payment.payment_type == PaymentType.credit_application.value,
        )

        if not include_voided:
            payments_in_query = payments_in_query.filter(Payment.voided.is_(False))
            credit_out_query = credit_out_query.filter(Payment.voided.is_(False))

        payments_in = payments_in_query.scalar() or 0.0
        credit_out = credit_out_query.scalar() or 0.0

        # Net = Money IN - Credit OUT
        return float(payments_in) - float(credit_out)

    def get_recent_payments(
        self, db: Session, skip: int = 0, limit: int = 50
    ) -> list[Payment]:
        """Get recent payments with customer data."""
        return (
            db.query(Payment)
            .options(joinedload(Payment.customer))
            .filter(Payment.voided.is_(False))
            .order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def void_payment(
        self, db: Session, payment_id: int, void_reason: str, voided_by_id: int
    ) -> bool:
        """Void a payment (cannot delete)."""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment or payment.voided:
            return False

        payment.voided = True
        payment.void_reason = void_reason
        payment.voided_by_id = voided_by_id
        payment.voided_at = datetime.now()

        db.commit()
        return True

    def list_payments(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        include_voided: bool = False,
        customer_id: int | None = None,
    ) -> list[Payment]:
        """List payments with pagination."""
        query = db.query(Payment)

        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)

        if not include_voided:
            query = query.filter(Payment.voided.is_(False))

        return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

    def count_payments(
        self,
        db: Session,
        include_voided: bool = False,
        customer_id: int | None = None,
    ) -> int:
        """Count total payments."""
        query = db.query(func.count(Payment.id))

        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)

        if not include_voided:
            query = query.filter(Payment.voided.is_(False))

        return query.scalar() or 0


payment_crud = PaymentCRUD()
