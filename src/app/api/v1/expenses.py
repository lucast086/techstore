"""API endpoints for expense management."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import RequireRole, get_current_user
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.expense import (
    ExpenseCategoryCreate,
    ExpenseCategoryList,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdate,
    ExpenseCreate,
    ExpenseFilter,
    ExpenseResponse,
    ExpenseSummary,
    ExpenseUpdate,
)
from app.schemas.response import ResponseSchema
from app.services.expense_service import expense_service

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


@router.get(
    "/categories",
    response_model=ResponseSchema[list[ExpenseCategoryResponse]],
    dependencies=[Depends(RequireRole(["admin", "manager"]))],
)
async def list_expense_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all expense categories (Admin/Manager only)."""
    categories = expense_service.get_all_categories(db, skip=skip, limit=limit)
    return ResponseSchema(
        success=True,
        message="Categories retrieved successfully",
        data=categories,
    )


@router.get(
    "/categories/active",
    response_model=ResponseSchema[list[ExpenseCategoryList]],
)
async def list_active_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active expense categories for dropdown."""
    categories = expense_service.get_categories_for_dropdown(db)
    return ResponseSchema(
        success=True,
        message="Active categories retrieved successfully",
        data=categories,
    )


@router.post(
    "/categories",
    response_model=ResponseSchema[ExpenseCategoryResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequireRole(["admin"]))],
)
async def create_expense_category(
    category_in: ExpenseCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new expense category (Admin only)."""
    try:
        category = expense_service.manage_category(db, category_create=category_in)
        return ResponseSchema(
            success=True,
            message="Category created successfully",
            data=ExpenseCategoryResponse.model_validate(category),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/categories/{category_id}",
    response_model=ResponseSchema[ExpenseCategoryResponse],
    dependencies=[Depends(RequireRole(["admin"]))],
)
async def update_expense_category(
    category_id: int,
    category_in: ExpenseCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update expense category (Admin only)."""
    try:
        category = expense_service.manage_category(
            db, category_id=category_id, category_update=category_in
        )
        return ResponseSchema(
            success=True,
            message="Category updated successfully",
            data=ExpenseCategoryResponse.model_validate(category),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/categories/{category_id}",
    response_model=ResponseSchema[ExpenseCategoryResponse],
    dependencies=[Depends(RequireRole(["admin"]))],
)
async def deactivate_expense_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate expense category (Admin only)."""
    try:
        # Validate deletion
        can_delete, message = expense_service.validate_category_deletion(
            db, category_id=category_id
        )

        if not can_delete and "not found" in message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        # Deactivate category
        category = expense_service.deactivate_category(db, category_id=category_id)

        return ResponseSchema(
            success=True,
            message="Category deactivated successfully",
            data=ExpenseCategoryResponse.model_validate(category),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Expense Endpoints


@router.post(
    "",
    response_model=ResponseSchema[ExpenseResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new expense."""
    try:
        expense = expense_service.register_expense(
            db, expense_in=expense_in, current_user=current_user
        )

        # Get with relationships for response
        from app.crud.expense import expense as expense_crud

        expense = expense_crud.get(db, id=expense.id)

        return ResponseSchema(
            success=True,
            message="Expense created successfully",
            data=ExpenseResponse(
                **expense.__dict__,
                category_name=expense.category.name,
                created_by_name=expense.user.full_name,
            ),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=ResponseSchema[list[ExpenseResponse]],
)
async def list_expenses(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    category_id: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    payment_method: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List expenses with filters."""
    filters = ExpenseFilter(
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        min_amount=min_amount,
        max_amount=max_amount,
        payment_method=payment_method,
    )

    expenses = expense_service.get_expenses_with_filters(
        db, filters=filters, skip=skip, limit=limit
    )

    return ResponseSchema(
        success=True,
        message="Expenses retrieved successfully",
        data=expenses,
    )


@router.get(
    "/summary",
    response_model=ResponseSchema[ExpenseSummary],
)
async def get_expense_summary(
    target_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get expense summary for a date."""
    if not target_date:
        target_date = date.today()

    summary = expense_service.get_expense_summary(db, target_date=target_date)

    return ResponseSchema(
        success=True,
        message=f"Expense summary for {target_date}",
        data=summary,
    )


@router.get(
    "/{expense_id}",
    response_model=ResponseSchema[ExpenseResponse],
)
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single expense."""
    from app.crud.expense import expense as expense_crud

    expense = expense_crud.get(db, id=expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return ResponseSchema(
        success=True,
        message="Expense retrieved successfully",
        data=ExpenseResponse(
            **expense.__dict__,
            category_name=expense.category.name,
            created_by_name=expense.user.full_name,
        ),
    )


@router.put(
    "/{expense_id}",
    response_model=ResponseSchema[ExpenseResponse],
)
async def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update expense (same day only)."""
    try:
        expense = expense_service.update_expense(
            db,
            expense_id=expense_id,
            expense_in=expense_in,
            current_user=current_user,
        )

        return ResponseSchema(
            success=True,
            message="Expense updated successfully",
            data=ExpenseResponse(
                **expense.__dict__,
                category_name=expense.category.name,
                created_by_name=expense.user.full_name,
            ),
        )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
