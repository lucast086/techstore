"""Sales web routes for HTMX interface."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.crud.sale import sale_crud
from app.database import get_async_session as get_db
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.cash_closing_service import cash_closing_service
from app.services.invoice_service import invoice_service
from app.utils.timezone import get_local_date

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/pos", response_class=HTMLResponse)
async def pos_interface(
    request: Request,
    repair_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Render Point of Sale interface."""
    # Check if cash register is open for today
    can_process, reason = cash_closing_service.check_can_process_sale(
        db=db, sale_date=get_local_date()
    )

    if not can_process:
        # Redirect to cash closings page with a message
        return RedirectResponse(
            url="/cash-closings?message=open_required", status_code=302
        )

    # Check if a repair_id was provided
    repair_data = None
    if repair_id:
        from app.models.repair import Repair

        repair = db.query(Repair).filter(Repair.id == repair_id).first()
        if repair:
            # Check if repair hasn't been invoiced yet
            if not repair.sale_id:
                repair_data = {
                    "id": repair.id,
                    "repair_number": repair.repair_number,
                    "description": f"Reparación #{repair.repair_number} - {repair.device_brand} {repair.device_model or repair.device_type}",
                    "price": float(repair.final_cost or repair.estimated_cost or 0),
                    "customer_id": repair.customer_id,
                    "customer_name": repair.customer.name if repair.customer else None,
                }
            else:
                # Repair already invoiced, show warning
                logger.warning(
                    f"Repair {repair_id} already invoiced with sale_id {repair.sale_id}"
                )

    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "Point of Sale",
        "repair_data": repair_data,
    }

    return templates.TemplateResponse("sales/pos.html", context)


@router.get("/pos/products/search", response_class=HTMLResponse)
async def search_products_htmx(
    request: Request,
    q: str = Query(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Search products and return HTMX partial."""
    # Only search if query has at least 1 character
    if len(q.strip()) < 1:
        products = []
    else:
        products = sale_crud.search_products(db, query=q.strip(), limit=10)

    context = {
        "request": request,
        "products": products,
    }

    return templates.TemplateResponse(
        "sales/partials/product_search_results.html", context
    )


@router.get("/pos/customers", response_class=HTMLResponse)
async def get_customers_htmx(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Get customer list for select dropdown."""
    from app.models.customer import Customer

    customers = (
        db.query(Customer)
        .filter(Customer.is_active.is_(True))
        .order_by(Customer.name)
        .all()
    )

    html = '<option value="">Walk-in Customer</option>'
    for customer in customers:
        html += f'<option value="{customer.id}">{customer.name}</option>'

    return HTMLResponse(content=html)


@router.get("/pos/customers/search", response_class=HTMLResponse)
async def search_customers_htmx(
    request: Request,
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Search customers and return HTMX partial."""
    from sqlalchemy import or_

    from app.models.customer import Customer

    query = q.lower()
    customers = (
        db.query(Customer)
        .filter(
            Customer.is_active.is_(True),
            or_(
                Customer.name.ilike(f"%{query}%"),
                Customer.phone.ilike(f"%{query}%"),
                Customer.email.ilike(f"%{query}%"),
            ),
        )
        .limit(20)
        .all()
    )

    context = {
        "request": request,
        "customers": customers,
    }

    return templates.TemplateResponse(
        "sales/partials/customer_search_results.html", context
    )


@router.get("/pos/customers/{customer_id}/balance")
async def get_customer_balance_json(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Get customer balance for POS (returns JSON)."""
    from app.crud.customer import customer_crud
    from app.services.balance_service import balance_service

    # Check customer exists
    customer = customer_crud.get(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    # Get balance information
    balance_info = balance_service.get_balance_summary(db, customer_id)

    return {
        "customer_id": customer_id,
        "customer_name": customer.name,
        "balance": float(
            balance_info["current_balance"]
        ),  # Convert to float for template
        "has_debt": balance_info["has_debt"],
        "has_credit": balance_info["has_credit"],
        "formatted": balance_info["formatted"],
        "status": balance_info["status"],
    }


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
    repair_id_to_invoice = None

    # Count how many items we have
    for key in form_data.keys():
        if key.startswith("product_id_"):
            item_count += 1

    # Extract item data
    for i in range(item_count):
        product_id = form_data.get(f"product_id_{i}")
        quantity = form_data.get(f"quantity_{i}")
        unit_price = form_data.get(f"unit_price_{i}")
        is_custom_price = (
            form_data.get(f"is_custom_price_{i}", "false").lower() == "true"
        )

        if product_id and quantity and unit_price:
            # Check if this is a repair item
            if str(product_id).startswith("repair_"):
                # Extract repair ID
                repair_id_to_invoice = int(str(product_id).replace("repair_", ""))

                # Create a special product entry for the repair
                # We'll handle this specially in the sale creation
                from app.models.product import Product

                # Find a service product or create a temporary one
                service_product = (
                    db.query(Product)
                    .filter(
                        Product.name.ilike("%servicio%")
                        | Product.name.ilike("%reparaci%")
                    )
                    .first()
                )

                if service_product:
                    items.append(
                        SaleItemCreate(
                            product_id=service_product.id,
                            quantity=int(quantity),
                            unit_price=Decimal(unit_price)
                            if unit_price and str(unit_price).strip()
                            else Decimal("0"),
                            is_custom_price=is_custom_price,
                        )
                    )
                else:
                    # If no service product exists, we'll need to handle this differently
                    logger.warning("No service product found for repair invoicing")
                    # For now, skip adding to items but continue with the repair_id_to_invoice
            else:
                items.append(
                    SaleItemCreate(
                        product_id=int(product_id),
                        quantity=int(quantity),
                        unit_price=Decimal(unit_price)
                        if unit_price and str(unit_price).strip()
                        else Decimal("0"),
                        is_custom_price=is_custom_price,
                    )
                )

    if not items:
        return HTMLResponse(
            '<div class="alert alert-danger">No items in cart</div>',
            status_code=400,
        )

    # Extract payment information
    payment_method = form_data.get("payment_method", "cash")

    # Add payment details to notes if applicable
    notes = form_data.get("notes", "")

    # Track actual amount paid (for partial payments)
    amount_paid = None  # Will default to full amount if not specified

    if payment_method == "cash":
        amount_received = form_data.get("amount_received", "0")
        # Handle empty or whitespace-only values
        if amount_received and amount_received.strip():
            amount_paid = Decimal(amount_received)
        else:
            amount_paid = Decimal("0")
        notes = f"Amount received: ${amount_paid}\n{notes}".strip()
    elif payment_method == "transfer":
        reference_number = form_data.get("reference_number")
        if reference_number:
            notes = f"Reference: {reference_number}\n{notes}".strip()
        # For transfer, check for the transfer amount paid field
        transfer_amount_paid = form_data.get("transfer_amount_paid")
        if transfer_amount_paid and transfer_amount_paid.strip():
            amount_paid = Decimal(transfer_amount_paid)
        else:
            # Fallback to transfer_amount if exists (for mixed payments)
            transfer_amount = form_data.get("transfer_amount")
            if transfer_amount and transfer_amount.strip():
                amount_paid = Decimal(transfer_amount)
    elif payment_method == "card":
        card_operation_number = form_data.get("card_operation_number")
        if card_operation_number:
            notes = f"Card operation: {card_operation_number}\n{notes}".strip()
        # For card, check for the card amount paid field
        card_amount_paid = form_data.get("card_amount_paid")
        if card_amount_paid and card_amount_paid.strip():
            amount_paid = Decimal(card_amount_paid)
        else:
            # Fallback to card_amount if exists (for mixed payments)
            card_amount = form_data.get("card_amount")
            if card_amount and card_amount.strip():
                amount_paid = Decimal(card_amount)
    elif payment_method == "account_credit":
        # Credit payment handling
        credit_amount = form_data.get("credit_amount", "0")
        customer_id = form_data.get("customer_id")

        if not customer_id:
            return HTMLResponse(
                '<div class="alert alert-danger">Customer required for credit payment</div>',
                status_code=400,
            )

        # Import balance service to validate credit
        from app.services.balance_service import balance_service

        # Check customer credit balance
        balance_info = balance_service.get_balance_summary(db, int(customer_id))
        available_credit = (
            Decimal(str(balance_info["current_balance"]))
            if balance_info["has_credit"]
            else Decimal("0")
        )

        credit_to_use = (
            Decimal(credit_amount)
            if credit_amount and credit_amount.strip()
            else Decimal("0")
        )
        if credit_to_use > available_credit:
            return HTMLResponse(
                f'<div class="alert alert-danger">Insufficient credit. Available: ${available_credit:.2f}</div>',
                status_code=400,
            )

        amount_paid = credit_to_use
        notes = f"Paid with account credit: ${credit_to_use:.2f}\n{notes}".strip()

    elif payment_method == "mixed":
        cash_amount = form_data.get("cash_amount", "0")
        transfer_amount = form_data.get("transfer_amount", "0")
        card_amount = form_data.get("card_amount", "0")
        mixed_credit_amount = form_data.get("mixed_credit_amount", "0")

        # Validate credit if used in mixed payment
        customer_id = form_data.get("customer_id")
        if Decimal(mixed_credit_amount or "0") > 0:
            if not customer_id:
                return HTMLResponse(
                    '<div class="alert alert-danger">Customer required for credit payment</div>',
                    status_code=400,
                )

            # Import balance service to validate credit
            from app.services.balance_service import balance_service

            # Check customer credit balance
            balance_info = balance_service.get_balance_summary(db, int(customer_id))
            available_credit = (
                Decimal(str(balance_info["current_balance"]))
                if balance_info["has_credit"]
                else Decimal("0")
            )

            credit_to_use = (
                Decimal(mixed_credit_amount)
                if mixed_credit_amount and mixed_credit_amount.strip()
                else Decimal("0")
            )
            if credit_to_use > available_credit:
                return HTMLResponse(
                    f'<div class="alert alert-danger">Insufficient credit. Available: ${available_credit:.2f}</div>',
                    status_code=400,
                )

        # Calculate total amount paid in mixed payment
        # Handle empty values by defaulting to 0
        safe_cash = (
            Decimal(cash_amount)
            if cash_amount and cash_amount.strip()
            else Decimal("0")
        )
        safe_transfer = (
            Decimal(transfer_amount)
            if transfer_amount and transfer_amount.strip()
            else Decimal("0")
        )
        safe_card = (
            Decimal(card_amount)
            if card_amount and card_amount.strip()
            else Decimal("0")
        )
        safe_credit = (
            Decimal(mixed_credit_amount)
            if mixed_credit_amount and mixed_credit_amount.strip()
            else Decimal("0")
        )

        total_paid = safe_cash + safe_transfer + safe_card + safe_credit
        if total_paid > 0:
            amount_paid = total_paid

        payment_details = []
        if safe_cash > 0:
            payment_details.append(f"Cash: ${safe_cash}")
        if safe_transfer > 0:
            payment_details.append(f"Transfer: ${safe_transfer}")
        if safe_card > 0:
            payment_details.append(f"Card: ${safe_card}")
        if safe_credit > 0:
            payment_details.append(f"Credit: ${safe_credit}")
        if payment_details:
            notes = f"Payment breakdown: {', '.join(payment_details)}\n{notes}".strip()

    # Create sale data
    sale_data = SaleCreate(
        customer_id=int(form_data.get("customer_id"))
        if form_data.get("customer_id")
        else None,
        payment_method=payment_method,
        discount_amount=Decimal(form_data.get("discount_amount", "0")),
        notes=notes,
        items=items,
        amount_paid=amount_paid,  # Include the actual amount paid
    )

    try:
        # Check if cash register is open for today
        can_process, reason = cash_closing_service.check_can_process_sale(
            db=db, sale_date=get_local_date()
        )
        if not can_process:
            return HTMLResponse(
                f"""<div class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                            </svg>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800">Cash Register Not Open</h3>
                            <div class="mt-2 text-sm text-red-700">
                                <p>{reason}</p>
                                <p class="mt-2">
                                    <a href="/cash-closings/open" class="font-medium underline text-red-600 hover:text-red-500">
                                        Open Cash Register Now →
                                    </a>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>""",
                status_code=400,
            )

        # Create sale
        sale = sale_crud.create_sale(db=db, sale_in=sale_data, user_id=current_user.id)

        # Process credit usage if account_credit was used as payment
        if payment_method == "account_credit" and amount_paid and sale.customer_id:
            credit_used = amount_paid
            logger.info(
                f"Processing credit usage: ${credit_used} for customer {sale.customer_id}"
            )

            # Apply customer credit using the payment service
            from app.services.payment_service import PaymentService

            payment_service = PaymentService()

            try:
                payment_service.apply_customer_credit(
                    db=db,
                    customer_id=sale.customer_id,
                    credit_amount=credit_used,
                    sale_id=sale.id,
                    user_id=current_user.id,
                    notes=f"Credit applied to sale {sale.invoice_number}",
                )
                logger.info(f"Credit usage processed successfully for sale {sale.id}")
            except Exception as e:
                logger.error(f"Failed to process credit usage: {e}")
                db.rollback()
                return HTMLResponse(
                    f'<div class="alert alert-danger">Error processing credit payment: {str(e)}</div>',
                    status_code=500,
                )

        # Handle mixed payment with credit
        elif (
            payment_method == "mixed"
            and mixed_credit_amount
            and mixed_credit_amount.strip()
            and sale.customer_id
        ):
            credit_used = Decimal(mixed_credit_amount)
            logger.info(
                f"Processing mixed payment credit usage: ${credit_used} for customer {sale.customer_id}"
            )

            # Apply customer credit using the payment service
            from app.services.payment_service import PaymentService

            payment_service = PaymentService()

            try:
                payment_service.apply_customer_credit(
                    db=db,
                    customer_id=sale.customer_id,
                    credit_amount=credit_used,
                    sale_id=sale.id,
                    user_id=current_user.id,
                    notes=f"Credit portion applied to mixed payment for sale {sale.invoice_number}",
                )
                logger.info(
                    f"Mixed payment credit usage processed successfully for sale {sale.id}"
                )
            except Exception as e:
                logger.error(f"Failed to process mixed payment credit usage: {e}")
                db.rollback()
                return HTMLResponse(
                    f'<div class="alert alert-danger">Error processing credit payment: {str(e)}</div>',
                    status_code=500,
                )

        # If this sale was for a repair, update the repair with the sale_id
        if repair_id_to_invoice:
            from app.models.repair import Repair

            repair = db.query(Repair).filter(Repair.id == repair_id_to_invoice).first()
            if repair and not repair.sale_id:
                repair.sale_id = sale.id
                db.add(repair)
                db.commit()
                logger.info(
                    f"Updated repair {repair_id_to_invoice} with sale_id {sale.id}"
                )

        # Redirect to receipt
        return HTMLResponse(
            f'<script>window.location.href="/sales/{sale.id}/receipt";</script>',
            headers={"HX-Redirect": f"/sales/{sale.id}/receipt"},
        )

    except ValueError as e:
        logger.error(f"Error creating sale: {e}")
        error_message = str(e)

        # Create a more user-friendly error message for walk-in customer payment issues
        if "Walk-in customers must pay in full" in error_message:
            return HTMLResponse(
                f"""<div class="mt-4 p-4 bg-red-50 border-2 border-red-400 rounded-lg">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-lg font-semibold text-red-800">Pago Incompleto</h3>
                            <div class="mt-2 text-sm text-red-700">
                                <p>Los clientes de mostrador deben pagar el total completo.</p>
                                <p class="mt-1">{error_message}</p>
                            </div>
                        </div>
                    </div>
                </div>""",
                status_code=400,
            )

        # Generic error message for other validation errors
        return HTMLResponse(
            f"""<div class="mt-4 p-4 bg-red-50 border-2 border-red-400 rounded-lg">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <h3 class="text-lg font-semibold text-red-800">Error en la Venta</h3>
                        <div class="mt-2 text-sm text-red-700">
                            <p>{error_message}</p>
                        </div>
                    </div>
                </div>
            </div>""",
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
    customer_id: Optional[str] = Query(None),
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
    start_datetime = None
    end_datetime = None

    if start_date and start_date.strip():
        try:
            # Try to parse as date string first (YYYY-MM-DD)
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            # Fallback to ISO format if it includes time
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                logger.warning(f"Invalid start_date format: {start_date}")

    if end_date and end_date.strip():
        try:
            # Try to parse as date string first (YYYY-MM-DD)
            # Add time to make it end of day for proper filtering
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
        except ValueError:
            # Fallback to ISO format if it includes time
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                logger.warning(f"Invalid end_date format: {end_date}")

    # Convert customer_id to int if provided
    customer_id_int = None
    if customer_id and customer_id.strip():
        try:
            customer_id_int = int(customer_id)
        except ValueError:
            logger.warning(f"Invalid customer_id: {customer_id}")

    # Get sales
    sales, total = sale_crud.get_multi_with_filters(
        db,
        skip=skip,
        limit=page_size,
        customer_id=customer_id_int,
        start_date=start_datetime,
        end_date=end_datetime,
        payment_status=payment_status
        if payment_status and payment_status.strip()
        else None,
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
    print: bool = Query(False),
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
        "print_mode": print,
    }

    return templates.TemplateResponse("sales/receipt.html", context)


@router.get("/{sale_id}/invoice/download")
async def download_invoice_web(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
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
