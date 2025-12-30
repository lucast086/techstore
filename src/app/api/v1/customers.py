"""Customer API endpoints - JSON adapter for CustomerService."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.dependencies import get_db
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.customer import customer_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create new customer - API endpoint.

    Args:
        customer: Customer data to create.
        db: Database session.
        current_user: Currently authenticated user.

    Returns:
        Created customer with calculated fields as JSON.

    Raises:
        HTTPException: If customer with phone already exists.
    """
    logger.info(f"Creating customer via API: {customer.name}")

    try:
        # Call service directly
        new_customer = customer_service.create_customer(
            db=db, customer_data=customer, created_by_id=current_user.id
        )

        # Return JSON response with calculated fields
        return CustomerResponse(
            id=new_customer.id,
            name=new_customer.name,
            phone=new_customer.phone,
            phone_secondary=new_customer.phone_secondary,
            email=new_customer.email,
            address=new_customer.address,
            notes=new_customer.notes,
            is_active=new_customer.is_active,
            created_at=new_customer.created_at,
            updated_at=new_customer.updated_at,
            created_by_id=new_customer.created_by_id,
            created_by_name=current_user.full_name,
            balance=customer_service.get_customer_balance(db, new_customer.id),
            transaction_count=customer_service.get_customer_transaction_count(
                db, new_customer.id
            ),
        )
    except ValueError as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/check-phone")
async def check_phone_availability(
    phone: Annotated[str, Query(min_length=1)],
    exclude_id: Annotated[int | None, Query()] = None,
    db: Session = Depends(get_db),
):
    """Check if phone number is already in use - API endpoint.

    Args:
        phone: Phone number to check.
        exclude_id: Customer ID to exclude from check.
        db: Database session.

    Returns:
        JSON with availability status and message.
    """
    # Call service directly
    return customer_service.check_phone_availability(
        db=db, phone=phone, exclude_id=exclude_id
    )


@router.get("/{customer_id}/balance")
async def get_customer_balance(
    customer_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get customer balance information.

    Args:
        customer_id: Customer ID.
        current_user: Currently authenticated user.
        db: Database session.

    Returns:
        Balance information including amount and status.
    """
    from app.services.customer_account_service import customer_account_service

    # Check customer exists
    customer = customer_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    # Get balance information from CustomerAccount (single source of truth)
    balance_info = customer_account_service.get_balance_summary(db, customer_id)

    return {
        "customer_id": customer_id,
        "customer_name": customer.name,
        "balance": float(balance_info["current_balance"]),  # Convert to float for JSON
        "has_debt": balance_info["has_debt"],
        "has_credit": balance_info["has_credit"],
        "formatted": balance_info["formatted"],
        "status": balance_info["status"],
    }


@router.get("/search")
async def search_customers(
    q: Annotated[str, Query(min_length=1)],
    include_inactive: Annotated[bool, Query()] = False,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search customers - API endpoint.

    Args:
        q: Search query string.
        include_inactive: Whether to include inactive customers.
        limit: Maximum number of results.
        db: Database session.
        current_user: Currently authenticated user.

    Returns:
        JSON with search results.
    """
    logger.info(f"Searching customers via API: {q}")

    # Call service directly
    customers = customer_service.search_customers(
        db=db, query=q, include_inactive=include_inactive, limit=limit
    )

    return {
        "results": [
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "phone_secondary": c.phone_secondary,
                "is_active": c.is_active,
            }
            for c in customers
        ]
    }
