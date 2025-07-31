"""Sales web routes for HTMX interface."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.crud.sale import sale_crud
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/pos", response_class=HTMLResponse)
async def pos_interface(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render Point of Sale interface."""
    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "Point of Sale",
    }

    return templates.TemplateResponse("sales/pos.html", context)


@router.get("/pos/products/search", response_class=HTMLResponse)
async def search_products_htmx(
    request: Request,
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Search products and return HTMX partial."""
    products = sale_crud.search_products(db, query=q, limit=10)

    context = {
        "request": request,
        "products": products,
    }

    return templates.TemplateResponse(
        "sales/partials/product_search_results.html", context
    )


@router.post("/pos/cart/add", response_class=HTMLResponse)
async def add_to_cart(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Add product to cart (HTMX endpoint)."""
    # Get product details
    from app.models.product import Product

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return HTMLResponse(
            '<div class="alert alert-danger">Product not found</div>',
            status_code=404,
        )

    if product.current_stock < quantity:
        return HTMLResponse(
            f'<div class="alert alert-warning">Insufficient stock. Available: {product.current_stock}</div>',
            status_code=400,
        )

    # Create cart item data
    cart_item = {
        "product_id": product.id,
        "product_name": product.name,
        "product_sku": product.sku,
        "quantity": quantity,
        "unit_price": float(product.first_sale_price),
        "total_price": float(product.first_sale_price * quantity),
    }

    context = {
        "request": request,
        "item": cart_item,
    }

    return templates.TemplateResponse("sales/partials/cart_item.html", context)


@router.post("/pos/checkout", response_class=HTMLResponse)
async def process_checkout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Process checkout and create sale."""
    # Parse form data
    form_data = await request.form()

    # Extract cart items
    items = []
    item_count = 0

    # Count how many items we have
    for key in form_data.keys():
        if key.startswith("product_id_"):
            item_count += 1

    # Extract item data
    for i in range(item_count):
        product_id = form_data.get(f"product_id_{i}")
        quantity = form_data.get(f"quantity_{i}")
        unit_price = form_data.get(f"unit_price_{i}")

        if product_id and quantity and unit_price:
            items.append(
                SaleItemCreate(
                    product_id=int(product_id),
                    quantity=int(quantity),
                    unit_price=Decimal(unit_price),
                )
            )

    if not items:
        return HTMLResponse(
            '<div class="alert alert-danger">No items in cart</div>',
            status_code=400,
        )

    # Create sale data
    sale_data = SaleCreate(
        customer_id=int(form_data.get("customer_id"))
        if form_data.get("customer_id")
        else None,
        payment_method=form_data.get("payment_method", "cash"),
        discount_amount=Decimal(form_data.get("discount_amount", "0")),
        notes=form_data.get("notes", ""),
        items=items,
    )

    try:
        # Create sale
        sale = sale_crud.create_sale(db=db, sale_in=sale_data, user_id=current_user.id)

        # Redirect to receipt
        return HTMLResponse(
            f'<script>window.location.href="/sales/{sale.id}/receipt";</script>',
            headers={"HX-Redirect": f"/sales/{sale.id}/receipt"},
        )

    except ValueError as e:
        logger.error(f"Error creating sale: {e}")
        return HTMLResponse(
            f'<div class="alert alert-danger">{str(e)}</div>',
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Unexpected error creating sale: {e}")
        return HTMLResponse(
            '<div class="alert alert-danger">Error processing sale</div>',
            status_code=500,
        )


@router.get("/", response_class=HTMLResponse)
async def sales_history(
    request: Request,
    page: int = Query(1, ge=1),
    search: Optional[str] = None,
    customer_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payment_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Display sales history."""
    page_size = 20
    skip = (page - 1) * page_size

    # Parse dates
    start_datetime = datetime.fromisoformat(start_date) if start_date else None
    end_datetime = datetime.fromisoformat(end_date) if end_date else None

    # Get sales
    sales, total = sale_crud.get_multi_with_filters(
        db,
        skip=skip,
        limit=page_size,
        customer_id=customer_id,
        start_date=start_datetime,
        end_date=end_datetime,
        payment_status=payment_status,
        is_voided=False,
    )

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size

    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "Sales History",
        "sales": sales,
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "search": search,
        "customer_id": customer_id,
        "start_date": start_date,
        "end_date": end_date,
        "payment_status": payment_status,
    }

    return templates.TemplateResponse("sales/history.html", context)


@router.get("/{sale_id}", response_class=HTMLResponse)
async def sale_detail(
    request: Request,
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Display sale details."""
    sale = sale_crud.get_with_details(db, id=sale_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    context = {
        "request": request,
        "current_user": current_user,
        "page_title": f"Sale {sale.invoice_number}",
        "sale": sale,
    }

    return templates.TemplateResponse("sales/detail.html", context)


@router.get("/{sale_id}/receipt", response_class=HTMLResponse)
async def sale_receipt(
    request: Request,
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Display sale receipt."""
    sale = sale_crud.get_with_details(db, id=sale_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found",
        )

    context = {
        "request": request,
        "current_user": current_user,
        "page_title": f"Receipt - {sale.invoice_number}",
        "sale": sale,
        "company": {
            "name": "TechStore",
            "address": "123 Main St, City",
            "phone": "+1234567890",
            "email": "info@techstore.com",
            "tax_id": "TAX123456",
        },
    }

    return templates.TemplateResponse("sales/receipt.html", context)


@router.post("/{sale_id}/void", response_class=HTMLResponse)
async def void_sale_htmx(
    request: Request,
    sale_id: int,
    reason: str = Form(..., min_length=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Void a sale (admin only)."""
    if not current_user.is_admin:
        return HTMLResponse(
            '<div class="alert alert-danger">Only administrators can void sales</div>',
            status_code=403,
        )

    try:
        sale = sale_crud.void_sale(
            db, sale_id=sale_id, reason=reason, user_id=current_user.id
        )

        return HTMLResponse(
            f'<div class="alert alert-success">Sale {sale.invoice_number} voided successfully</div>',
            headers={"HX-Redirect": f"/sales/{sale_id}"},
        )

    except ValueError as e:
        return HTMLResponse(
            f'<div class="alert alert-danger">{str(e)}</div>',
            status_code=400,
        )
