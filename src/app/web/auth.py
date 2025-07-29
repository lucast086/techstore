"""Auth routes for web interface."""
from typing import Annotated

import httpx
from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
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
    print(f"[WEB LOGIN DEBUG] Base URL: {request.base_url}")

    # Call the API endpoint using httpx
    async with httpx.AsyncClient(base_url=str(request.base_url)) as client:
        print("[WEB LOGIN DEBUG] Calling API endpoint: /api/v1/auth/login")
        api_response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
            headers={
                "X-Forwarded-For": request.client.host if request.client else "unknown"
            },
        )
        print(f"[WEB LOGIN DEBUG] API response status: {api_response.status_code}")
        print(f"[WEB LOGIN DEBUG] API response body: {api_response.text}")

    if api_response.status_code == 200:
        # Success - get tokens from JSON response
        tokens = api_response.json()

        # Set cookies for web authentication
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=8 * 3600,  # 8 hours
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=30 * 24 * 3600,  # 30 days
        )

        # Return HTMX redirect header
        response.headers["HX-Redirect"] = "/dashboard"
        return ""

    elif api_response.status_code == 429:
        # Rate limit exceeded
        return """
        <div class="bg-error-100 border border-error-500 text-error-600 px-4 py-3 rounded-md text-sm">
            <span class="font-medium">Error:</span> Too many login attempts. Please try again later.
        </div>
        """

    else:
        # Authentication failed
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
