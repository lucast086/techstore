"""Sales API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.crud.sale import sale_crud
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.base import ResponseSchema
from app.schemas.sale import (
    ProductSearchResult,
    SaleCreate,
    SaleListResponse,
    SaleResponse,
    SaleSummary,
    VoidSaleRequest,
)
from app.services.invoice_service import invoice_service

router = APIRouter()


@router.post("/", response_model=ResponseSchema)
async def create_sale(
    sale_in: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Create new sale transaction.

    - **items**: List of products with quantities and prices
    - **customer_id**: Optional customer ID (null for walk-in)
    - **payment_method**: cash, transfer, card, or mixed
    - **discount_amount**: Optional discount on total
    """
    try:
        sale = sale_crud.create_sale(db=db, sale_in=sale_in, user_id=current_user.id)

        # Convert to response schema
        sale_response = SaleResponse(
            **sale.__dict__,
            items=[
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "discount_percentage": item.discount_percentage,
                    "discount_amount": item.discount_amount,
                    "total_price": item.total_price,
                    "product_name": item.product.name,
                    "product_sku": item.product.sku,
                }
                for item in sale.items
            ],
            customer_name=sale.customer.name if sale.customer else None,
            user_name=sale.user.full_name,
            amount_paid=sale.amount_paid,
            amount_due=sale.amount_due,
        )

        # Check if debt was generated and create notification message
        message = "Sale created successfully"
        if sale.customer_id and sale.amount_due > 0:
            from app.services.debt_service import debt_service

            debt_message = debt_service.get_debt_notification_message(
                db, sale.customer_id, sale.amount_due
            )
            message = f"Sale created successfully. {debt_message}"

        return ResponseSchema(
            success=True,
            message=message,
            data=sale_response.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sale: {str(e)}",
        ) from e


@router.get("/", response_model=ResponseSchema)
async def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    customer_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    payment_status: Optional[str] = Query(None, pattern="^(pending|partial|paid)$"),
    payment_method: Optional[str] = Query(
        None, pattern="^(cash|transfer|card|mixed|account_credit)$"
    ),
    is_voided: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Get list of sales with filters.

    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **customer_id**: Filter by customer
    - **start_date**: Filter by start date
    - **end_date**: Filter by end date
    - **payment_status**: Filter by payment status
    - **payment_method**: Filter by payment method
    - **is_voided**: Filter voided/active sales
    """
    sales, total = sale_crud.get_multi_with_filters(
        db,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        payment_status=payment_status,
        payment_method=payment_method,
        is_voided=is_voided,
    )

    sales_list = [
        SaleListResponse(
            id=sale.id,
            invoice_number=sale.invoice_number,
            sale_date=sale.sale_date,
            customer_name=sale.customer.name if sale.customer else "Walk-in",
            total_amount=sale.total_amount,
            payment_status=sale.payment_status,
            payment_method=sale.payment_method,
            is_voided=sale.is_voided,
        )
        for sale in sales
    ]

    return ResponseSchema(
        success=True,
        data={
            "items": [sale.model_dump() for sale in sales_list],
            "total": total,
            "page": skip // limit + 1,
            "pages": (total + limit - 1) // limit,
        },
    )


@router.get("/summary", response_model=ResponseSchema)
async def get_sales_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Get sales summary statistics.

    - **start_date**: Start date for summary
    - **end_date**: End date for summary
    """
    summary_data = sale_crud.get_sales_summary(
        db, start_date=start_date, end_date=end_date
    )

    summary = SaleSummary(**summary_data)

    return ResponseSchema(
        success=True,
        data=summary.model_dump(),
    )


@router.get("/products/search", response_model=ResponseSchema)
async def search_products(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Search products for POS.

    - **q**: Search query (name, SKU, or barcode)
    - **limit**: Maximum results to return
    """
    products = sale_crud.search_products(db, query=q, limit=limit)

    results = [
        ProductSearchResult(
            id=product.id,
            sku=product.sku,
            name=product.name,
            barcode=product.barcode,
            price=product.first_sale_price,
            stock=product.current_stock,
            category=product.category.name,
        )
        for product in products
    ]

    return ResponseSchema(
        success=True,
        data=[result.model_dump() for result in results],
    )


@router.get("/{sale_id}", response_model=ResponseSchema)
async def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Get sale details by ID."""
    sale = sale_crud.get_with_details(db, id=sale_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    sale_response = SaleResponse(
        **sale.__dict__,
        items=[
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "discount_percentage": item.discount_percentage,
                "discount_amount": item.discount_amount,
                "total_price": item.total_price,
                "product_name": item.product.name,
                "product_sku": item.product.sku,
            }
            for item in sale.items
        ],
        customer_name=sale.customer.name if sale.customer else None,
        user_name=sale.user.full_name,
        amount_paid=sale.amount_paid,
        amount_due=sale.amount_due,
    )

    return ResponseSchema(
        success=True,
        data=sale_response.model_dump(),
    )


@router.post("/{sale_id}/void", response_model=ResponseSchema)
async def void_sale(
    sale_id: int,
    void_request: VoidSaleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Void a sale (admin only).

    - **reason**: Reason for voiding (minimum 10 characters)
    """
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can void sales",
        )

    try:
        sale = sale_crud.void_sale(
            db, sale_id=sale_id, reason=void_request.reason, user_id=current_user.id
        )

        return ResponseSchema(
            success=True,
            message="Sale voided successfully",
            data={"invoice_number": sale.invoice_number},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{sale_id}/receipt", response_model=ResponseSchema)
async def get_receipt(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResponseSchema:
    """Get receipt data for a sale."""
    sale = sale_crud.get_with_details(db, id=sale_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    # This would typically come from settings
    receipt_data = {
        "sale": SaleResponse(
            **sale.__dict__,
            items=[
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "discount_percentage": item.discount_percentage,
                    "discount_amount": item.discount_amount,
                    "total_price": item.total_price,
                    "product_name": item.product.name,
                    "product_sku": item.product.sku,
                }
                for item in sale.items
            ],
            customer_name=sale.customer.name if sale.customer else None,
            user_name=sale.user.full_name,
            amount_paid=sale.amount_paid,
            amount_due=sale.amount_due,
        ).model_dump(),
        "company_name": "TechStore",
        "company_address": "123 Main St, City",
        "company_phone": "+1234567890",
        "company_email": "info@techstore.com",
        "tax_id": "TAX123456",
    }

    return ResponseSchema(
        success=True,
        data=receipt_data,
    )


@router.get("/{sale_id}/invoice/download")
async def download_invoice(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download invoice as PDF."""
    sale = sale_crud.get_with_details(db, id=sale_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    # Generate PDF
    pdf_bytes = invoice_service.generate_invoice_pdf(sale)

    from fastapi.responses import Response

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="invoice_{sale.invoice_number}.pdf"'
        },
    )


@router.post("/{sale_id}/credit-note")
async def generate_credit_note(
    sale_id: int,
    reason: str = Query(..., min_length=10, description="Reason for credit note"),
    amount: Optional[float] = Query(None, description="Credit amount (if partial)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a credit note for a sale (admin only)."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can generate credit notes",
        )

    sale = sale_crud.get_with_details(db, id=sale_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    # Generate credit note PDF
    from decimal import Decimal

    credit_amount = Decimal(str(amount)) if amount else None
    pdf_bytes = invoice_service.generate_credit_note(sale, reason, credit_amount)

    from fastapi.responses import Response

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="credit_note_{sale.invoice_number}.pdf"'
        },
    )
