"""Web routes for product management interface."""

import logging
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.dependencies import get_db
from app.models.user import User
from app.schemas.product import ProductCreate
from app.services.product_service import CategoryService, ProductService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products-web"])
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/", response_class=HTMLResponse)
async def products_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
    page: int = 1,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    stock_status: str = "all",
    sort_by: str = "name",
    sort_order: str = "asc",
    view: str = "table",
):
    """Display the products list page with enhanced filtering."""
    from app.schemas.filters import (
        ProductFilter,
        ProductListParams,
        SortField,
        SortOrder,
        StockStatus,
        ViewMode,
    )

    service = ProductService(db)
    category_service = CategoryService(db)

    # Build filter params
    filters = ProductFilter(
        search=search,
        category_ids=[category_id] if category_id else [],
        stock_status=StockStatus(stock_status),
        is_active=True,  # Only show active products by default
    )

    # Build list params
    params = ProductListParams(
        filters=filters,
        sort_by=SortField(sort_by),
        sort_order=SortOrder(sort_order),
        page=page,
        page_size=20,
        view_mode=ViewMode(view),
    )

    # Get products with new method
    products, total = await service.get_product_list(params)

    # Get categories for filter
    categories = await category_service.get_categories(is_active=True)

    # Get filter options
    filter_options = await service.get_filter_options()

    # Calculate pagination
    total_pages = (total + params.page_size - 1) // params.page_size

    return templates.TemplateResponse(
        "products/list.html",
        {
            "request": request,
            "user": current_user,
            "products": products,
            "categories": categories,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "search": search,
            "category_id": category_id,
            "stock_status": stock_status,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "view": view,
            "filter_options": filter_options,
        },
    )


@router.get("/create", response_class=HTMLResponse)
async def create_product_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Display the create product form."""
    category_service = CategoryService(db)
    categories = await category_service.get_categories(is_active=True)

    return templates.TemplateResponse(
        "products/create.html",
        {
            "request": request,
            "user": current_user,
            "categories": categories,
        },
    )


@router.post("/create", response_class=HTMLResponse)
async def create_product(
    request: Request,
    sku: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    brand: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    barcode: Optional[str] = Form(None),
    purchase_price: Decimal = Form(...),
    first_sale_price: Decimal = Form(...),
    second_sale_price: Decimal = Form(...),
    third_sale_price: Decimal = Form(...),
    tax_rate: Decimal = Form(Decimal("16.00")),
    current_stock: int = Form(0),
    minimum_stock: int = Form(0),
    maximum_stock: Optional[int] = Form(None),
    location: Optional[str] = Form(None),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Handle product creation."""
    service = ProductService(db)
    category_service = CategoryService(db)

    try:
        # Create product data
        product_data = ProductCreate(
            sku=sku,
            name=name,
            description=description,
            category_id=category_id,
            brand=brand,
            model=model,
            barcode=barcode,
            purchase_price=purchase_price,
            first_sale_price=first_sale_price,
            second_sale_price=second_sale_price,
            third_sale_price=third_sale_price,
            tax_rate=tax_rate,
            current_stock=current_stock,
            minimum_stock=minimum_stock,
            maximum_stock=maximum_stock,
            location=location,
            is_active=is_active,
        )

        # Create product
        product = await service.create_product(product_data, current_user.id)

        logger.info(
            f"Product created successfully: {product.id} by user {current_user.id}"
        )

        # Return success partial with HX-Trigger for notifications
        return HTMLResponse(
            f"""
            <div id="success-message" class="alert alert-success" role="alert">
                <i class="fas fa-check-circle"></i>
                Producto creado exitosamente: <strong>{product.name}</strong> (SKU: {product.sku})
            </div>
            """,
            status_code=201,
            headers={
                "HX-Trigger": "productCreated",
                "HX-Redirect": f"/products/{product.id}",
            },
        )

    except ValueError as e:
        logger.error(f"Validation error creating product: {str(e)}")

        # Get categories for re-rendering form
        categories = await category_service.get_categories(is_active=True)

        # Return form with error
        return templates.TemplateResponse(
            "products/_form.html",
            {
                "request": request,
                "user": current_user,
                "categories": categories,
                "errors": {"general": str(e)},
                "values": {
                    "sku": sku,
                    "name": name,
                    "description": description,
                    "category_id": category_id,
                    "brand": brand,
                    "model": model,
                    "barcode": barcode,
                    "purchase_price": purchase_price,
                    "first_sale_price": first_sale_price,
                    "second_sale_price": second_sale_price,
                    "third_sale_price": third_sale_price,
                    "tax_rate": tax_rate,
                    "current_stock": current_stock,
                    "minimum_stock": minimum_stock,
                    "maximum_stock": maximum_stock,
                    "location": location,
                    "is_active": is_active,
                },
            },
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Unexpected error creating product: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error interno al crear el producto"
        ) from e


@router.get("/{product_id}", response_class=HTMLResponse)
async def product_detail(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Display product detail page."""
    service = ProductService(db)
    product = await service.get_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return templates.TemplateResponse(
        "products/detail.html",
        {
            "request": request,
            "user": current_user,
            "product": product,
        },
    )


@router.get("/search", response_class=HTMLResponse)
async def search_products(
    request: Request,
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Search products and return HTML partial."""
    service = ProductService(db)

    products = await service.get_products(limit=10, search=q, is_active=True)

    return templates.TemplateResponse(
        "products/_search_results.html",
        {
            "request": request,
            "products": products,
        },
    )
