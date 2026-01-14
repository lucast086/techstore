"""Admin panel routes for system administrators."""

import logging
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie, require_web_role
from app.database import get_async_session
from app.models.user import User
from app.utils.templates import create_templates

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])
templates = create_templates()


@router.get(
    "/",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_dashboard(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Render admin dashboard page.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with admin dashboard.
    """
    # Get some basic stats for the dashboard
    from app.models.user import User as UserModel

    total_users = db.query(UserModel).count()
    active_users = db.query(UserModel).filter(UserModel.is_active).count()
    admin_users = db.query(UserModel).filter(UserModel.role == "admin").count()

    context = {
        "request": request,
        "current_user": current_user,
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
        },
        "page_title": "Dashboard",
        "breadcrumbs": [
            {"name": "Admin", "url": "/admin"},
            {"name": "Dashboard", "url": "/admin", "active": True},
        ],
    }

    logger.info(f"Admin dashboard accessed by user: {current_user.email}")
    return templates.TemplateResponse("admin/dashboard.html", context)


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_dashboard_partial(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Render admin dashboard partial for HTMX.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with dashboard content partial.
    """
    from app.models.user import User as UserModel

    total_users = db.query(UserModel).count()
    active_users = db.query(UserModel).filter(UserModel.is_active).count()
    admin_users = db.query(UserModel).filter(UserModel.role == "admin").count()

    context = {
        "request": request,
        "current_user": current_user,
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
        },
    }

    return templates.TemplateResponse("admin/partials/dashboard_content.html", context)


@router.get(
    "/users",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_users(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
) -> HTMLResponse:
    """Render user management page.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.

    Returns:
        HTML response with user management page.
    """
    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "User Management",
        "breadcrumbs": [
            {"name": "Admin", "url": "/admin"},
            {"name": "User Management", "url": "/admin/users", "active": True},
        ],
    }

    logger.info(f"User management page accessed by admin: {current_user.email}")
    return templates.TemplateResponse("admin/users.html", context)


@router.get(
    "/users/list",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_users_partial(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
) -> HTMLResponse:
    """Render user management partial for HTMX.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.

    Returns:
        HTML response with user management content partial.
    """
    context = {"request": request, "current_user": current_user}

    return templates.TemplateResponse("admin/partials/users_content.html", context)


@router.get(
    "/settings",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_settings(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
) -> HTMLResponse:
    """Render system settings page.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.

    Returns:
        HTML response with system settings page.
    """
    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "System Settings",
        "breadcrumbs": [
            {"name": "Admin", "url": "/admin"},
            {"name": "System Settings", "url": "/admin/settings", "active": True},
        ],
    }

    logger.info(f"System settings page accessed by admin: {current_user.email}")
    return templates.TemplateResponse("admin/settings.html", context)


@router.get(
    "/settings/content",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_settings_partial(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
) -> HTMLResponse:
    """Render system settings partial for HTMX.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.

    Returns:
        HTML response with settings content partial.
    """
    context = {"request": request, "current_user": current_user}

    return templates.TemplateResponse("admin/partials/settings_content.html", context)


@router.get(
    "/logs",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_logs(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
) -> HTMLResponse:
    """Render activity logs page.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.

    Returns:
        HTML response with activity logs page.
    """
    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "Activity Logs",
        "breadcrumbs": [
            {"name": "Admin", "url": "/admin"},
            {"name": "Activity Logs", "url": "/admin/logs", "active": True},
        ],
    }

    logger.info(f"Activity logs page accessed by admin: {current_user.email}")
    return templates.TemplateResponse("admin/logs.html", context)


@router.get(
    "/logs/content",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_logs_partial(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
) -> HTMLResponse:
    """Render activity logs partial for HTMX.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.

    Returns:
        HTML response with logs content partial.
    """
    context = {"request": request, "current_user": current_user}

    return templates.TemplateResponse("admin/partials/logs_content.html", context)


@router.get(
    "/categories",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_categories(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Render category management page.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with category management page.
    """
    from app.services.category_service import EnhancedCategoryService

    service = EnhancedCategoryService(db)

    # Get category tree and stats
    tree = await service.get_category_tree()
    stats = await service.get_category_stats()

    context = {
        "request": request,
        "current_user": current_user,
        "category_tree": tree,
        "stats": stats,
        "page_title": "Category Management",
        "breadcrumbs": [
            {"name": "Admin", "url": "/admin"},
            {"name": "Category Management", "url": "/admin/categories", "active": True},
        ],
    }

    logger.info(f"Category management page accessed by admin: {current_user.email}")

    # Check if this is an HTMX request
    if request.headers.get("HX-Request"):
        # For HTMX requests, return just the content without the base template
        return templates.TemplateResponse(
            "admin/partials/categories_page.html", context
        )

    return templates.TemplateResponse("admin/categories.html", context)


@router.get(
    "/categories/content",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_categories_partial(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
    search: Optional[str] = None,
) -> HTMLResponse:
    """Render category management partial for HTMX.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.
        db: Database session.
        search: Optional search query.

    Returns:
        HTML response with category management content partial.
    """
    from app.services.category_service import EnhancedCategoryService

    service = EnhancedCategoryService(db)

    # Always get stats for the template
    stats = await service.get_category_stats()

    if search:
        # Search mode - flat list
        categories = await service.search_categories(search)
        context = {
            "request": request,
            "current_user": current_user,
            "categories": categories,
            "search": search,
            "stats": stats,
        }
    else:
        # Tree view mode
        tree = await service.get_category_tree()
        context = {
            "request": request,
            "current_user": current_user,
            "category_tree": tree,
            "stats": stats,
        }

    return templates.TemplateResponse("admin/partials/categories_content.html", context)


@router.get(
    "/categories/create",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_categories_create(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Render category creation form.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with category creation form.
    """
    from app.services.category_service import EnhancedCategoryService

    service = EnhancedCategoryService(db)

    # Get all categories for parent selection
    categories = await service.get_categories_flat()

    context = {
        "request": request,
        "current_user": current_user,
        "categories": categories,
        "page_title": "Create Category",
        "breadcrumbs": [
            {"name": "Admin", "url": "/admin"},
            {"name": "Category Management", "url": "/admin/categories"},
            {"name": "Create", "url": "/admin/categories/create", "active": True},
        ],
    }

    return templates.TemplateResponse("admin/partials/category_form.html", context)


@router.get(
    "/categories/{category_id}/edit",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_categories_edit(
    request: Request,
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Render category edit form.

    Args:
        request: FastAPI request object.
        category_id: ID of category to edit.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with category edit form.
    """
    from app.services.category_service import EnhancedCategoryService

    service = EnhancedCategoryService(db)

    # Get category
    category = await service.get_category(category_id)
    if not category:
        # Return error or redirect
        return templates.TemplateResponse(
            "admin/partials/error.html",
            {"request": request, "error": "Category not found"},
        )

    # Get all categories for parent selection (excluding self and descendants)
    categories = await service.get_categories_flat()

    context = {
        "request": request,
        "current_user": current_user,
        "category": category,
        "categories": categories,
        "page_title": f"Edit Category: {category.name}",
        "breadcrumbs": [
            {"name": "Admin", "url": "/admin"},
            {"name": "Category Management", "url": "/admin/categories"},
            {
                "name": "Edit",
                "url": f"/admin/categories/{category_id}/edit",
                "active": True,
            },
        ],
    }

    return templates.TemplateResponse("admin/partials/category_form.html", context)


@router.post(
    "/categories",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_categories_create_post(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Handle category creation.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with updated categories list.
    """
    from app.schemas.category import CategoryCreate
    from app.services.category_service import EnhancedCategoryService

    service = EnhancedCategoryService(db)

    # Get form data
    form = await request.form()

    try:
        # Create category
        category_data = CategoryCreate(
            name=form.get("name"),
            description=form.get("description", ""),
            parent_id=int(form.get("parent_id")) if form.get("parent_id") else None,
            display_order=int(form.get("display_order", 0)),
            is_active="is_active" in form,
        )

        await service.create_category(category_data)

        # Return updated categories list
        tree = await service.get_category_tree()
        stats = await service.get_category_stats()

        context = {
            "request": request,
            "current_user": current_user,
            "category_tree": tree,
            "stats": stats,
        }

        return templates.TemplateResponse(
            "admin/partials/categories_content.html", context
        )

    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return templates.TemplateResponse(
            "admin/partials/error.html", {"request": request, "error": str(e)}
        )


@router.post(
    "/categories/{category_id}",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_categories_update_post(
    request: Request,
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Handle category update.

    Args:
        request: FastAPI request object.
        category_id: ID of category to update.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with updated categories list.
    """
    from app.schemas.category import CategoryUpdate
    from app.services.category_service import EnhancedCategoryService

    service = EnhancedCategoryService(db)

    # Get form data
    form = await request.form()

    try:
        # Update category
        category_data = CategoryUpdate(
            name=form.get("name"),
            description=form.get("description", ""),
            parent_id=int(form.get("parent_id")) if form.get("parent_id") else None,
            display_order=int(form.get("display_order", 0)),
            is_active="is_active" in form,
        )

        await service.update_category(category_id, category_data)

        # Return updated categories list
        tree = await service.get_category_tree()
        stats = await service.get_category_stats()

        context = {
            "request": request,
            "current_user": current_user,
            "category_tree": tree,
            "stats": stats,
        }

        return templates.TemplateResponse(
            "admin/partials/categories_content.html", context
        )

    except Exception as e:
        logger.error(f"Error updating category: {e}")
        return templates.TemplateResponse(
            "admin/partials/error.html", {"request": request, "error": str(e)}
        )


@router.post(
    "/categories/{category_id}/delete",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_categories_delete(
    request: Request,
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Handle category deletion.

    Args:
        request: FastAPI request object.
        category_id: ID of category to delete.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with updated categories list.
    """
    from app.services.category_service import EnhancedCategoryService

    service = EnhancedCategoryService(db)

    try:
        # Delete category
        await service.delete_category(category_id)

        # Return updated categories list
        tree = await service.get_category_tree()
        stats = await service.get_category_stats()

        context = {
            "request": request,
            "current_user": current_user,
            "category_tree": tree,
            "stats": stats,
        }

        return templates.TemplateResponse(
            "admin/partials/categories_content.html", context
        )

    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        return templates.TemplateResponse(
            "admin/partials/error.html", {"request": request, "error": str(e)}
        )


@router.get(
    "/statistics",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_statistics(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Render statistics overview page.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with statistics overview page.
    """
    from app.services.dashboard_service import dashboard_service

    stats = dashboard_service.get_dashboard_stats(db)

    context = {
        "request": request,
        "current_user": current_user,
        "stats": stats,
        "page_title": "Estadísticas",
        "breadcrumbs": [
            {"name": "Admin", "url": "/admin"},
            {"name": "Estadísticas", "url": "/admin/statistics", "active": True},
        ],
    }

    logger.info(f"Statistics page accessed by admin: {current_user.email}")

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "admin/partials/statistics_content.html", context
        )

    return templates.TemplateResponse("admin/statistics.html", context)


@router.get(
    "/statistics/content",
    response_class=HTMLResponse,
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_statistics_partial(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> HTMLResponse:
    """Render statistics partial for HTMX.

    Args:
        request: FastAPI request object.
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        HTML response with statistics content partial.
    """
    from app.services.dashboard_service import dashboard_service

    stats = dashboard_service.get_dashboard_stats(db)

    context = {
        "request": request,
        "current_user": current_user,
        "stats": stats,
    }

    return templates.TemplateResponse("admin/partials/statistics_content.html", context)


@router.get(
    "/reports/low-stock/pdf",
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_report_low_stock_pdf(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> Response:
    """Generate and download low stock inventory PDF report.

    Args:
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        PDF file download response.
    """
    from app.services.report_service import report_service

    logger.info(f"Low stock report requested by admin: {current_user.email}")

    pdf_content = report_service.generate_low_stock_report(db)

    filename = f"inventario_bajo_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/reports/accounts-receivable/pdf",
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_report_accounts_receivable_pdf(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    db: Session = Depends(get_async_session),
) -> Response:
    """Generate and download accounts receivable PDF report.

    Args:
        current_user: Currently authenticated admin user.
        db: Database session.

    Returns:
        PDF file download response.
    """
    from app.services.report_service import report_service

    logger.info(f"Accounts receivable report requested by admin: {current_user.email}")

    pdf_content = report_service.generate_accounts_receivable_report(db)

    filename = f"cuentas_por_cobrar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/reports/repairs-monthly/pdf",
    dependencies=[Depends(require_web_role(["admin"]))],
)
async def admin_report_repairs_monthly_pdf(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    year: int,
    month: int,
    db: Session = Depends(get_async_session),
) -> Response:
    """Generate and download monthly repairs PDF report.

    Args:
        current_user: Currently authenticated admin user.
        year: Year to filter (e.g., 2024).
        month: Month to filter (1-12).
        db: Database session.

    Returns:
        PDF file download response.
    """
    from app.services.report_service import report_service

    if month < 1 or month > 12:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Mes inválido (debe ser 1-12)")

    logger.info(
        f"Monthly repairs report requested by admin: {current_user.email} "
        f"for {year}-{month:02d}"
    )

    pdf_content = report_service.generate_monthly_repairs_report(db, year, month)

    filename = f"reparaciones_{year}_{month:02d}.pdf"

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
