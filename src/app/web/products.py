"""Web routes for product management interface."""

import logging
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie
from app.dependencies import get_db
from app.models.user import User
from app.schemas.product import ProductCreate
from app.services.product_service import CategoryService, ProductService
from app.utils.templates import create_templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products-web"])
templates = create_templates()


@router.get("/", response_class=HTMLResponse)
async def products_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
    page: int = 1,
    search: str = "",
    category_id: str = "",
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

    # Clean up empty string parameters
    search_term = search if search and search.strip() else None
    cat_id = int(category_id) if category_id and category_id.isdigit() else None

    # Validate and set defaults for enums
    try:
        stock_enum = StockStatus(stock_status) if stock_status else StockStatus.ALL
    except ValueError:
        stock_enum = StockStatus.ALL

    try:
        sort_field = SortField(sort_by) if sort_by else SortField.NAME
    except ValueError:
        sort_field = SortField.NAME

    try:
        sort_ord = SortOrder(sort_order) if sort_order else SortOrder.ASC
    except ValueError:
        sort_ord = SortOrder.ASC

    try:
        view_mode = ViewMode(view) if view else ViewMode.TABLE
    except ValueError:
        view_mode = ViewMode.TABLE

    # Build filter params
    filters = ProductFilter(
        search=search_term,
        category_ids=[cat_id] if cat_id else [],
        stock_status=stock_enum,
        is_active=True,  # Only show active products by default
    )

    # Build list params
    params = ProductListParams(
        filters=filters,
        sort_by=sort_field,
        sort_order=sort_ord,
        page=page,
        page_size=20,
        view_mode=view_mode,
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
            "current_user": current_user,
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
            "current_user": current_user,
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
    tax_rate: Decimal = Form(Decimal("0.00")),
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

    # Log incoming form data for debugging
    logger.info("[CREATE PRODUCT] Incoming form data:")
    logger.info(f"  SKU: {sku}, Name: {name}, Category: {category_id}")
    logger.info(f"  Purchase Price: {purchase_price}")
    logger.info(
        f"  Sale Prices: {first_sale_price}, {second_sale_price}, {third_sale_price}"
    )

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

        # Provide more specific error message
        error_msg = str(e)
        if "Sale price cannot be less than purchase price" in error_msg:
            error_msg = "Error: Los precios de venta deben ser mayores o iguales al precio de compra"

        # Return form with error
        return templates.TemplateResponse(
            "products/_form.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": categories,
                "errors": {"general": error_msg},
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
        logger.error(f"Error type: {type(e).__name__}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")

        # Get categories for re-rendering form
        categories = await category_service.get_categories(is_active=True)

        # Return form with generic error
        return templates.TemplateResponse(
            "products/_form.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": categories,
                "errors": {
                    "general": f"Error inesperado: {str(e)}. Por favor, contacte al administrador."
                },
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
            status_code=500,
        )


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
            "current_user": current_user,
            "product": product,
        },
    )


@router.get("/{product_id}/edit", response_class=HTMLResponse)
async def edit_product_form(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Display the edit product form."""
    service = ProductService(db)
    category_service = CategoryService(db)

    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    categories = await category_service.get_categories(is_active=True)

    return templates.TemplateResponse(
        "products/edit.html",
        {
            "request": request,
            "current_user": current_user,
            "product": product,
            "categories": categories,
        },
    )


@router.post("/{product_id}/edit", response_class=HTMLResponse)
async def update_product(
    request: Request,
    product_id: int,
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
    tax_rate: Decimal = Form(Decimal("0.00")),
    current_stock: int = Form(0),
    minimum_stock: int = Form(0),
    maximum_stock: Optional[int] = Form(None),
    location: Optional[str] = Form(None),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Handle product update."""
    from app.schemas.product import ProductUpdate

    service = ProductService(db)
    category_service = CategoryService(db)

    logger.info(f"[UPDATE PRODUCT] Updating product {product_id}")
    logger.info(f"  SKU: {sku}, Name: {name}, Category: {category_id}")

    try:
        # Create update data
        update_data = ProductUpdate(
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

        # Update product
        product = await service.update_product(product_id, update_data)

        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        logger.info(
            f"Product updated successfully: {product_id} by user {current_user.id}"
        )

        # Return success with redirect
        return HTMLResponse(
            f"""
            <div id="success-message" class="alert alert-success" role="alert">
                <i class="fas fa-check-circle"></i>
                Producto actualizado exitosamente: <strong>{product.name}</strong>
            </div>
            """,
            status_code=200,
            headers={
                "HX-Trigger": "productUpdated",
                "HX-Redirect": f"/products/{product_id}",
            },
        )

    except ValueError as e:
        logger.error(f"Validation error updating product: {str(e)}")

        # Get categories for re-rendering form
        categories = await category_service.get_categories(is_active=True)

        # Provide more specific error message
        error_msg = str(e)
        if "Sale price cannot be less than purchase price" in error_msg:
            error_msg = "Error: Los precios de venta deben ser mayores o iguales al precio de compra"

        # Get current product data for form
        product = await service.get_product(product_id)

        return templates.TemplateResponse(
            "products/edit.html",
            {
                "request": request,
                "current_user": current_user,
                "product": product,
                "categories": categories,
                "errors": {"general": error_msg},
            },
            status_code=400,
        )

    except Exception as e:
        logger.error(f"Unexpected error updating product: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")

        # Get categories and product for re-rendering form
        categories = await category_service.get_categories(is_active=True)
        product = await service.get_product(product_id)

        return templates.TemplateResponse(
            "products/edit.html",
            {
                "request": request,
                "current_user": current_user,
                "product": product,
                "categories": categories,
                "errors": {"general": f"Error inesperado: {str(e)}"},
            },
            status_code=500,
        )


@router.delete("/{product_id}", response_class=HTMLResponse)
async def delete_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Soft delete a product (set is_active=False)."""
    service = ProductService(db)

    logger.info(
        f"[DELETE PRODUCT] Deleting product {product_id} by user {current_user.id}"
    )

    try:
        deleted = await service.delete_product(product_id)

        if not deleted:
            return HTMLResponse(
                """<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    Producto no encontrado
                </div>""",
                status_code=404,
            )

        logger.info(f"Product {product_id} deleted successfully")

        return HTMLResponse(
            """<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                Producto eliminado exitosamente
            </div>""",
            status_code=200,
            headers={"HX-Redirect": "/products"},
        )

    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        return HTMLResponse(
            f"""<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                Error al eliminar producto: {str(e)}
            </div>""",
            status_code=500,
        )
