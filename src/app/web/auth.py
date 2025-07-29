"""Auth routes for web interface."""
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth import AuthService
from app.core.web_auth import get_current_user_from_cookie
from app.database import get_async_session

router = APIRouter()
templates = Jinja2Templates(directory="src/app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page."""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login-htmx", response_class=HTMLResponse)
async def login_htmx(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_async_session),
):
    """Handle HTMX login form submission.

    This endpoint handles the HTMX form submission and calls the API endpoint.
    Returns appropriate HTMX responses for success or error.
    """
    print("[WEB LOGIN DEBUG] HTMX login endpoint called")
    print(f"[WEB LOGIN DEBUG] Form data: email={email}")

    # Use AuthService directly instead of HTTP call
    auth_service = AuthService(db)
    print(f"[WEB LOGIN DEBUG] Authenticating user: {email}")

    user = auth_service.authenticate_user(email=email, password=password)

    if user:
        print(f"[WEB LOGIN DEBUG] Authentication successful for user: {user.email}")
        # Generate tokens
        tokens = auth_service.create_tokens(user)

        # Set cookies for web authentication
        response.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=8 * 3600,  # 8 hours
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=30 * 24 * 3600,  # 30 days
        )

        # Return HTMX redirect header
        response.headers["HX-Redirect"] = "/dashboard"
        return ""

    else:
        # Authentication failed
        print(f"[WEB LOGIN DEBUG] Authentication failed for user: {email}")
        return """
        <div class="bg-error-100 border border-error-500 text-error-600 px-4 py-3 rounded-md text-sm">
            <span class="font-medium">Error:</span> Invalid email or password.
        </div>
        """


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_async_session),
):
    """Display dashboard page for authenticated users."""
    if not access_token:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Get current user
        current_user = await get_current_user_from_cookie(request, access_token, db)
        return templates.TemplateResponse(
            "dashboard.html", {"request": request, "current_user": current_user}
        )
    except HTTPException:
        # If token is invalid, redirect to login
        return RedirectResponse(url="/login", status_code=302)


@router.post("/logout")
async def logout_web(
    response: Response, access_token: Annotated[str | None, Cookie()] = None
):
    """Web logout endpoint that handles cookie-based authentication.

    This endpoint is for web browsers using cookies. It clears the authentication
    cookies and redirects to the login page.
    """
    # Clear authentication cookies
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
    )

    # Return HTMX redirect to login page
    response.headers["HX-Redirect"] = "/login"
    return ""
