"""HTMX web routes for customer accounts management."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.customer import customer_crud
from app.crud.customer_account import customer_account_crud
from app.models.customer_account import TransactionType
from app.models.user import User
from app.services.customer_account_service import customer_account_service
from app.utils.templates import create_templates

logger = logging.getLogger(__name__)
templates = create_templates()

router = APIRouter()


@router.get("/customers/{customer_id}/account", response_class=HTMLResponse)
async def view_customer_account(
    request: Request,
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """View customer account overview."""
    # Get customer
    customer = customer_crud.get(db, id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    # Get or create account
    account = customer_account_crud.get_or_create(db, customer_id, current_user.id)
    db.commit()

    # Get recent transactions
    transactions, _ = customer_account_crud.get_transactions(
        db, customer_id=customer_id, limit=10
    )

    # Calculate summary stats
    account_status = "settled"
    if account.account_balance > 0:
        account_status = "debt"
    elif account.account_balance < 0:
        account_status = "credit"

    return templates.TemplateResponse(
        "accounts/account_overview.html",
        {
            "request": request,
            "customer": customer,
            "account": account,
            "transactions": transactions,
            "account_status": account_status,
            "current_user": current_user,
        },
    )


@router.get("/customers/{customer_id}/transactions", response_class=HTMLResponse)
async def view_customer_transactions(
    request: Request,
    customer_id: int,
    page: int = Query(1, ge=1),
    transaction_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """View customer transaction history."""
    # Get customer
    customer = customer_crud.get(db, id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    # Parse dates
    start_datetime = None
    end_datetime = None
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            pass
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        except ValueError:
            pass

    # Parse transaction type
    trans_type = None
    if transaction_type and transaction_type != "all":
        try:
            trans_type = TransactionType(transaction_type)
        except ValueError:
            pass

    # Pagination
    limit = 20
    skip = (page - 1) * limit

    # Get transactions
    transactions, total = customer_account_crud.get_transactions(
        db,
        customer_id=customer_id,
        skip=skip,
        limit=limit,
        transaction_type=trans_type,
        start_date=start_datetime,
        end_date=end_datetime,
    )

    # Calculate pagination
    total_pages = (total + limit - 1) // limit

    return templates.TemplateResponse(
        "accounts/transaction_list.html",
        {
            "request": request,
            "customer": customer,
            "transactions": transactions,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "transaction_type": transaction_type or "all",
            "start_date": start_date,
            "end_date": end_date,
            "TransactionType": TransactionType,
            "current_user": current_user,
        },
    )


@router.get("/customers/{customer_id}/statement", response_class=HTMLResponse)
async def generate_customer_statement(
    request: Request,
    customer_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generate customer account statement."""
    # Get customer
    customer = customer_crud.get(db, id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    # Parse dates
    end_datetime = datetime.utcnow()
    start_datetime = end_datetime - timedelta(days=30)

    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            pass
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        except ValueError:
            pass

    try:
        # Generate statement
        statement = customer_account_service.get_statement(
            db, customer_id, start_datetime, end_datetime
        )

        return templates.TemplateResponse(
            "accounts/statement.html",
            {
                "request": request,
                "customer": customer,
                "statement": statement,
                "current_user": current_user,
            },
        )
    except Exception as e:
        logger.error(f"Error generating statement for customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate statement",
        )


@router.post("/customers/{customer_id}/credit/apply", response_class=HTMLResponse)
async def apply_credit_to_sale(
    request: Request,
    customer_id: int,
    sale_id: int = Form(...),
    amount: Decimal = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Apply customer credit to a sale."""
    try:
        # Apply credit
        transaction, applied_amount = customer_account_service.apply_credit(
            db, customer_id, amount, sale_id, current_user.id, notes
        )

        db.commit()

        # Return success response (could be a partial or redirect)
        return HTMLResponse(
            content=f"""
            <div class="rounded-md bg-green-50 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-green-800">
                            Successfully applied ${applied_amount} credit to sale #{sale_id}
                        </p>
                    </div>
                </div>
            </div>
            """,
            status_code=200,
        )
    except ValueError as e:
        return HTMLResponse(
            content=f"""
            <div class="rounded-md bg-red-50 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-red-800">{str(e)}</p>
                    </div>
                </div>
            </div>
            """,
            status_code=400,
        )


@router.get("/customers/{customer_id}/credit/check", response_class=HTMLResponse)
async def check_customer_credit(
    request: Request,
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Check customer credit availability (HTMX endpoint)."""
    has_credit, amount, message = customer_account_service.check_credit_availability(
        db, customer_id
    )

    if has_credit:
        return HTMLResponse(
            content=f"""
            <div class="text-green-600 font-semibold">
                ${amount} credit available
            </div>
            """,
            status_code=200,
        )
    else:
        return HTMLResponse(
            content=f"""
            <div class="text-gray-500">
                {message}
            </div>
            """,
            status_code=200,
        )


@router.put("/accounts/{account_id}/credit-limit", response_class=HTMLResponse)
async def update_credit_limit(
    request: Request,
    account_id: int,
    credit_limit: Decimal = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update account credit limit."""
    try:
        customer_account_crud.update_credit_limit(
            db,
            account_id=account_id,
            credit_limit=credit_limit,
            updated_by_id=current_user.id,
        )

        return HTMLResponse(
            content=f"""
            <div class="rounded-md bg-green-50 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-green-800">
                            Credit limit updated to ${credit_limit}
                        </p>
                    </div>
                </div>
            </div>
            """,
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error updating credit limit for account {account_id}: {e}")
        return HTMLResponse(
            content="""
            <div class="rounded-md bg-red-50 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-red-800">Failed to update credit limit</p>
                    </div>
                </div>
            </div>
            """,
            status_code=500,
        )


@router.get("/accounts/dashboard", response_class=HTMLResponse)
async def accounts_receivable_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Accounts receivable dashboard."""
    # Get summary
    summary = customer_account_crud.get_account_summary(db)

    # Get top debtors
    top_debtors, _ = customer_account_crud.get_accounts_with_debt(db, limit=5)

    # Get accounts with credit
    credit_accounts, _ = customer_account_crud.get_accounts_with_credit(db, limit=5)

    return templates.TemplateResponse(
        "accounts/dashboard.html",
        {
            "request": request,
            "summary": summary,
            "top_debtors": top_debtors,
            "credit_accounts": credit_accounts,
            "current_user": current_user,
        },
    )
