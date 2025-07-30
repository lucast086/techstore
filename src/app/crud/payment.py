"""Payment CRUD operations for TechStore SaaS."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate


class PaymentCRUD:
    """CRUD operations for Payment model."""

    def create(
        self, db: Session, customer_id: int, payment: PaymentCreate, received_by_id: int
    ) -> Payment:
        """Record new payment."""
        # Generate receipt number
        receipt_number = self.generate_receipt_number(db)

        db_payment = Payment(
            customer_id=customer_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            notes=payment.notes,
            receipt_number=receipt_number,
            received_by_id=received_by_id,
        )

        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)

        return db_payment

    def generate_receipt_number(self, db: Session) -> str:
        """Generate unique receipt number: REC-YYYYMMDD-XXXX."""
        today = datetime.now()
        prefix = f"REC-{today.strftime('%Y%m%d')}"

        # Get count of receipts today
        count = (
            db.query(func.count(Payment.id))
            .filter(Payment.receipt_number.like(f"{prefix}%"))
            .scalar()
            or 0
        )

        return f"{prefix}-{str(count + 1).zfill(4)}"

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
        """Get total payment amount for a customer."""
        query = db.query(func.sum(Payment.amount)).filter(
            Payment.customer_id == customer_id
        )

        if not include_voided:
            query = query.filter(Payment.voided.is_(False))

        result = query.scalar()
        return float(result) if result else 0.0

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
