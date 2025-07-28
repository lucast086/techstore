"""Admin panel routes for system administrators."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.web_auth import get_current_user_from_cookie, require_web_role
from app.database import get_async_session
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(require_web_role(["admin"]))])
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
    "/dashboard", response_class=HTMLResponse, dependencies=[Depends(require_web_role(["admin"]))]
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
    "/users", response_class=HTMLResponse, dependencies=[Depends(require_web_role(["admin"]))]
)
async def admin_users(
    request: Request, current_user: Annotated[User, Depends(get_current_user_from_cookie)]
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
    "/users/list", response_class=HTMLResponse, dependencies=[Depends(require_web_role(["admin"]))]
)
async def admin_users_partial(
    request: Request, current_user: Annotated[User, Depends(get_current_user_from_cookie)]
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
    "/settings", response_class=HTMLResponse, dependencies=[Depends(require_web_role(["admin"]))]
)
async def admin_settings(
    request: Request, current_user: Annotated[User, Depends(get_current_user_from_cookie)]
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
    request: Request, current_user: Annotated[User, Depends(get_current_user_from_cookie)]
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
    "/logs", response_class=HTMLResponse, dependencies=[Depends(require_web_role(["admin"]))]
)
async def admin_logs(
    request: Request, current_user: Annotated[User, Depends(get_current_user_from_cookie)]
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
    request: Request, current_user: Annotated[User, Depends(get_current_user_from_cookie)]
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
