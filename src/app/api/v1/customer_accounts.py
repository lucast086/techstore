"""API endpoints for customer accounts management."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.customer_account import customer_account_crud
from app.models.customer_account import TransactionType
from app.models.user import User
from app.schemas.customer_account import (
    AccountsReceivableSummary,
    AccountStatement,
    CreditApplicationRequest,
    CreditApplicationResponse,
    CreditAvailabilityResponse,
    CustomerAccountCreate,
    CustomerAccountResponse,
    CustomerTransactionResponse,
    UpdateCreditLimit,
)
from app.services.customer_account_service import customer_account_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/customers/{customer_id}/account",
    response_model=CustomerAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_account(
    customer_id: int,
    account_in: CustomerAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CustomerAccountResponse:
    """Create a new customer account."""
    try:
        # Ensure customer_id matches
        account_in.customer_id = customer_id
        account = customer_account_service.create_account(
            db, account_in, current_user.id
        )
        return account
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating account for customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account",
        )


@router.get(
    "/customers/{customer_id}/account",
    response_model=CustomerAccountResponse,
)
def get_customer_account(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CustomerAccountResponse:
    """Get customer account details."""
    account = customer_account_service.get_account(db, customer_id)
    if not account:
        # Try to create one automatically
        try:
            customer_account_crud.get_or_create(db, customer_id, current_user.id)
            db.commit()
            account = customer_account_service.get_account(db, customer_id)
        except Exception as e:
            logger.error(f"Error creating account for customer {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer account not found",
            )

    return account


@router.get(
    "/customers/{customer_id}/transactions",
    response_model=dict,
)
def get_customer_transactions(
    customer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    transaction_type: Optional[TransactionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Get customer transaction history."""
    transactions, total = customer_account_crud.get_transactions(
        db,
        customer_id=customer_id,
        skip=skip,
        limit=limit,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
    )

    # Format transactions
    transaction_list = []
    for trans in transactions:
        transaction_list.append(
            CustomerTransactionResponse(
                id=trans.id,
                customer_id=trans.customer_id,
                account_id=trans.account_id,
                transaction_type=trans.transaction_type,
                amount=trans.amount,
                balance_before=trans.balance_before,
                balance_after=trans.balance_after,
                reference_type=trans.reference_type,
                reference_id=trans.reference_id,
                description=trans.description,
                notes=trans.notes,
                transaction_date=trans.transaction_date,
                created_at=trans.created_at,
                created_by_id=trans.created_by_id,
                created_by_name=trans.created_by.full_name
                if trans.created_by
                else None,
                is_debit=trans.is_debit,
                is_credit=trans.is_credit,
                impact_amount=trans.impact_amount,
            )
        )

    return {
        "transactions": transaction_list,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get(
    "/customers/{customer_id}/statement",
    response_model=AccountStatement,
)
def get_customer_statement(
    customer_id: int,
    start_date: Optional[datetime] = Query(
        None, description="Start date for statement period"
    ),
    end_date: Optional[datetime] = Query(
        None, description="End date for statement period"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AccountStatement:
    """Generate customer account statement."""
    # Default to last 30 days if dates not provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    try:
        statement = customer_account_service.get_statement(
            db, customer_id, start_date, end_date
        )
        return statement
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating statement for customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate statement",
        )


@router.get(
    "/customers/{customer_id}/credit/availability",
    response_model=CreditAvailabilityResponse,
)
def check_credit_availability(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CreditAvailabilityResponse:
    """Check customer credit availability."""
    has_credit, amount, message = customer_account_service.check_credit_availability(
        db, customer_id
    )

    return CreditAvailabilityResponse(
        has_credit=has_credit,
        available_amount=amount,
        message=message,
    )


@router.post(
    "/customers/{customer_id}/credit/apply",
    response_model=CreditApplicationResponse,
)
def apply_customer_credit(
    customer_id: int,
    request: CreditApplicationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CreditApplicationResponse:
    """Apply customer credit to a sale.

    TODO: This endpoint is not currently used.
    Credit is now automatically consumed when a sale is created (SALE transaction).
    This endpoint only records an informational CREDIT_APPLICATION transaction.
    Consider deprecating or repurposing this endpoint.
    """
    try:
        transaction, applied_amount = customer_account_service.apply_credit(
            db,
            customer_id,
            request.amount,
            request.sale_id,
            current_user.id,
            request.notes,
        )

        db.commit()

        return CreditApplicationResponse(
            transaction=transaction,
            amount_applied=applied_amount,
            success=True,
            message=f"Successfully applied ${applied_amount} credit to sale",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error applying credit for customer {customer_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply credit",
        )


@router.put(
    "/accounts/{account_id}/credit-limit",
    response_model=CustomerAccountResponse,
)
def update_account_credit_limit(
    account_id: int,
    update_data: UpdateCreditLimit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CustomerAccountResponse:
    """Update customer account credit limit."""
    try:
        account = customer_account_crud.update_credit_limit(
            db,
            account_id=account_id,
            credit_limit=update_data.credit_limit,
            updated_by_id=current_user.id,
        )

        # Return formatted response
        return CustomerAccountResponse(
            id=account.id,
            customer_id=account.customer_id,
            customer_name=account.customer.name,
            credit_limit=account.credit_limit,
            is_active=account.is_active,
            notes=account.notes,
            account_balance=account.account_balance,
            available_credit=account.available_credit,
            total_sales=account.total_sales,
            total_payments=account.total_payments,
            last_transaction_date=account.last_transaction_date,
            last_payment_date=account.last_payment_date,
            transaction_count=account.transaction_count,
            is_blocked=account.is_blocked,
            blocked_until=account.blocked_until,
            block_reason=account.block_reason,
            created_at=account.created_at,
            updated_at=account.updated_at,
            has_debt=account.has_debt,
            has_credit=account.has_credit,
            is_settled=account.is_settled,
            total_available_credit=account.total_available_credit,
            remaining_credit_limit=account.remaining_credit_limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating credit limit for account {account_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update credit limit",
        )


@router.get(
    "/accounts/summary",
    response_model=AccountsReceivableSummary,
)
def get_accounts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AccountsReceivableSummary:
    """Get accounts receivable summary."""
    summary = customer_account_crud.get_account_summary(db)

    return AccountsReceivableSummary(
        total_accounts=summary["total_accounts"],
        accounts_with_debt=summary["accounts_with_debt"],
        accounts_with_credit=summary["accounts_with_credit"],
        total_debt=summary["total_debt"],
        total_credit=summary["total_credit"],
        net_receivable=summary["net_receivable"],
        generated_at=datetime.utcnow(),
    )


@router.get(
    "/accounts/with-debt",
    response_model=dict,
)
def get_accounts_with_debt(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_balance: Optional[Decimal] = Query(None, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Get list of accounts with outstanding debt."""
    accounts, total = customer_account_crud.get_accounts_with_debt(
        db, skip=skip, limit=limit, min_balance=min_balance
    )

    # Format accounts
    account_list = []
    for account in accounts:
        account_list.append(
            {
                "id": account.id,
                "customer_id": account.customer_id,
                "customer_name": account.customer.name,
                "customer_phone": account.customer.phone,
                "account_balance": account.account_balance,
                "credit_limit": account.credit_limit,
                "last_transaction_date": account.last_transaction_date,
                "last_payment_date": account.last_payment_date,
                "is_blocked": account.is_blocked,
            }
        )

    return {
        "accounts": account_list,
        "total": total,
        "skip": skip,
        "limit": limit,
        "total_debt": sum(a["account_balance"] for a in account_list),
    }


@router.get(
    "/accounts/with-credit",
    response_model=dict,
)
def get_accounts_with_credit(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Get list of accounts with credit balance."""
    accounts, total = customer_account_crud.get_accounts_with_credit(
        db, skip=skip, limit=limit
    )

    # Format accounts
    account_list = []
    for account in accounts:
        account_list.append(
            {
                "id": account.id,
                "customer_id": account.customer_id,
                "customer_name": account.customer.name,
                "customer_phone": account.customer.phone,
                "account_balance": account.account_balance,
                "available_credit": abs(account.account_balance),
                "last_transaction_date": account.last_transaction_date,
                "is_active": account.is_active,
            }
        )

    return {
        "accounts": account_list,
        "total": total,
        "skip": skip,
        "limit": limit,
        "total_credit": sum(a["available_credit"] for a in account_list),
    }
