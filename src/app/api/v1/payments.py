"""Payment API endpoints."""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.crud.customer import customer_crud
from app.crud.payment import payment_crud
from app.crud.sale import sale_crud
from app.dependencies import get_db
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentListResponse,
    PaymentResponse,
    PaymentVoid,
)
from app.services.payment_service import payment_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    customer_id: int = Query(..., description="Customer ID"),
    sale_id: Optional[int] = Query(None, description="Related sale ID"),
    allow_overpayment: bool = Query(False, description="Allow payment exceeding debt"),
) -> PaymentResponse:
    """Process a customer payment.

    Args:
        payment_data: Payment details including amount and method.
        customer_id: ID of the customer making payment.
        sale_id: Optional ID of related sale.
        allow_overpayment: Whether to allow overpayment.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        Created payment details.

    Raises:
        HTTPException: If customer not found or payment validation fails.
    """
    # Verify customer exists
    customer = customer_crud.get(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify sale exists if provided
    if sale_id:
        sale = sale_crud.get(db, sale_id)
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        if sale.customer_id != customer_id:
            raise HTTPException(
                status_code=400, detail="Sale does not belong to this customer"
            )

    try:
        # Process payment based on method
        if payment_data.payment_method == "mixed" and payment_data.payment_methods:
            payment = payment_service.process_mixed_payment(
                db=db,
                customer_id=customer_id,
                sale_id=sale_id,
                payment_methods=payment_data.payment_methods,
                notes=payment_data.notes,
                user_id=current_user.id,
                allow_overpayment=allow_overpayment,
            )
        else:
            payment = payment_service.process_payment(
                db=db,
                customer_id=customer_id,
                sale_id=sale_id,
                payment_data=payment_data,
                user_id=current_user.id,
                allow_overpayment=allow_overpayment,
            )

        logger.info(f"Payment created: {payment.receipt_number}")

        return PaymentResponse(
            id=payment.id,
            receipt_number=payment.receipt_number,
            customer_id=payment.customer_id,
            customer_name=payment.customer.name,
            sale_id=payment.sale_id,
            amount=float(payment.amount),
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            notes=payment.notes,
            received_by=payment.received_by.full_name,
            created_at=payment.created_at,
            voided=payment.voided,
            void_reason=payment.void_reason,
            voided_by=payment.voided_by.full_name if payment.voided_by else None,
            voided_at=payment.voided_at,
        )

    except ValueError as e:
        logger.error(f"Payment validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/customer/{customer_id}", response_model=PaymentListResponse)
async def get_customer_payments(
    customer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_voided: bool = Query(False),
) -> PaymentListResponse:
    """Get all payments for a customer.

    Args:
        customer_id: ID of the customer.
        current_user: Currently authenticated user.
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        include_voided: Whether to include voided payments.

    Returns:
        List of customer payments.

    Raises:
        HTTPException: If customer not found.
    """
    # Verify customer exists
    customer = customer_crud.get(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get payments
    payments = payment_crud.list_payments(
        db=db,
        customer_id=customer_id,
        skip=skip,
        limit=limit,
        include_voided=include_voided,
    )

    total = payment_crud.count_payments(
        db=db,
        customer_id=customer_id,
        include_voided=include_voided,
    )

    # Convert to response format
    items = [
        PaymentResponse(
            id=payment.id,
            receipt_number=payment.receipt_number,
            customer_id=payment.customer_id,
            customer_name=payment.customer.name,
            sale_id=payment.sale_id,
            amount=float(payment.amount),
            payment_method=payment.payment_method,
            reference_number=payment.reference_number,
            notes=payment.notes,
            received_by=payment.received_by.full_name,
            created_at=payment.created_at,
            voided=payment.voided,
            void_reason=payment.void_reason,
            voided_by=payment.voided_by.full_name if payment.voided_by else None,
            voided_at=payment.voided_at,
        )
        for payment in payments
    ]

    return PaymentListResponse(
        items=items,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
    )


@router.get("/receipt/{receipt_number}", response_model=PaymentResponse)
async def get_payment_by_receipt(
    receipt_number: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> PaymentResponse:
    """Get payment by receipt number.

    Args:
        receipt_number: Unique receipt number.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        Payment details.

    Raises:
        HTTPException: If payment not found.
    """
    payment = payment_crud.get_by_receipt(db, receipt_number)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return PaymentResponse(
        id=payment.id,
        receipt_number=payment.receipt_number,
        customer_id=payment.customer_id,
        customer_name=payment.customer.name,
        sale_id=payment.sale_id,
        amount=float(payment.amount),
        payment_method=payment.payment_method,
        reference_number=payment.reference_number,
        notes=payment.notes,
        received_by=payment.received_by.full_name,
        created_at=payment.created_at,
        voided=payment.voided,
        void_reason=payment.void_reason,
        voided_by=payment.voided_by.full_name if payment.voided_by else None,
        voided_at=payment.voided_at,
    )


@router.post("/{payment_id}/void", response_model=PaymentResponse)
async def void_payment(
    payment_id: int,
    void_data: PaymentVoid,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> PaymentResponse:
    """Void a payment.

    Args:
        payment_id: ID of payment to void.
        void_data: Void reason details.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        Updated payment details.

    Raises:
        HTTPException: If payment not found or already voided.
    """
    # Get payment
    payment = payment_crud.get(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.voided:
        raise HTTPException(status_code=400, detail="Payment already voided")

    # Void the payment
    success = payment_crud.void_payment(
        db=db,
        payment_id=payment_id,
        void_reason=void_data.void_reason,
        voided_by_id=current_user.id,
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to void payment")

    # Update sale status if needed
    if payment.sale_id:
        sale = sale_crud.get(db, payment.sale_id)
        if sale:
            payment_service.update_sale_payment_status(db, sale)

    # Refresh payment data
    db.refresh(payment)

    logger.info(f"Payment voided: {payment.receipt_number} by {current_user.username}")

    return PaymentResponse(
        id=payment.id,
        receipt_number=payment.receipt_number,
        customer_id=payment.customer_id,
        customer_name=payment.customer.name,
        sale_id=payment.sale_id,
        amount=float(payment.amount),
        payment_method=payment.payment_method,
        reference_number=payment.reference_number,
        notes=payment.notes,
        received_by=payment.received_by.full_name,
        created_at=payment.created_at,
        voided=payment.voided,
        void_reason=payment.void_reason,
        voided_by=payment.voided_by.full_name if payment.voided_by else None,
        voided_at=payment.voided_at,
    )
