"""Search web interface for TechStore SaaS HTMX."""


import httpx
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.dependencies import SearchServiceDep
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["web-search"])


@router.post("/products", response_class=HTMLResponse)
async def search_products_htmx(
    request: Request,
    search_term: str = Form(..., alias="q"),
    category: str | None = Form(None),
    search_service: SearchService = SearchServiceDep,
):
    """
    HTMX search endpoint with hybrid approach:
    1. Try internal API call (production)
    2. Fallback to direct service call (testing/fallback)
    3. Convert result to HTML
    """
    try:
        # Try API call first (production path)
        base_url = str(request.base_url).rstrip("/")
        api_url = f"{base_url}/api/v1/search/products"

        params = {"q": search_term}
        if category:
            params["category"] = category

        async with httpx.AsyncClient() as client:
            api_response = await client.get(api_url, params=params, timeout=2.0)
            api_response.raise_for_status()
            api_data = api_response.json()

    except (httpx.RequestError, httpx.HTTPStatusError, httpx.TimeoutException):
        # Fallback to direct service call (testing/error path)
        api_data = search_service.search_products(
            search_term=search_term, category=category, max_results=10
        )

    # Handle empty results
    if not api_data["results"]:
        if not search_term.strip():
            return '<p class="text-muted"><i class="fas fa-search"></i> Enter a search term...</p>'
        else:
            return f'<p class="text-warning"><i class="fas fa-exclamation-triangle"></i> {api_data["message"]}</p>'

    # Build HTML response from API data
    html_parts = []
    html_parts.append(
        f'<p class="text-success mb-2"><i class="fas fa-check"></i> Found {api_data["total"]} products</p>'
    )

    for product in api_data["results"]:
        category_icon = _get_category_icon(product["category"])
        html_parts.append(
            f'<div class="result-item border-bottom py-2">'
            f'<div class="d-flex align-items-center">'
            f'<i class="{category_icon} text-primary me-2"></i>'
            f'<div class="flex-grow-1">'
            f'<strong>{product["name"]}</strong>'
            f'<br><small class="text-muted">{product["category"].title()} • ${product["price"]}</small>'
            f'</div></div></div>'
        )

    return "".join(html_parts)


@router.get("/categories", response_class=HTMLResponse)
async def get_categories_htmx(
    request: Request, search_service: SearchService = SearchServiceDep
):
    """Get categories as HTML options for select dropdown."""
    try:
        # Try API call first (production path)
        base_url = str(request.base_url).rstrip("/")
        api_url = f"{base_url}/api/v1/search/categories"

        async with httpx.AsyncClient() as client:
            api_response = await client.get(api_url, timeout=2.0)
            api_response.raise_for_status()
            api_data = api_response.json()
            categories = api_data["categories"]

    except (httpx.RequestError, httpx.HTTPStatusError, httpx.TimeoutException):
        # Fallback to direct service call (testing/error path)
        categories = search_service.get_categories()

    # Convert to HTML options
    html_parts = ['<option value="">All Categories</option>']
    for category in categories:
        html_parts.append(f'<option value="{category}">{category.title()}</option>')

    return "".join(html_parts)


def _get_category_icon(category: str) -> str:
    """Get Font Awesome icon for product category."""
    icons = {
        "smartphone": "fas fa-mobile-alt",
        "laptop": "fas fa-laptop",
        "tablet": "fas fa-tablet-alt",
        "audio": "fas fa-headphones",
        "default": "fas fa-box",
    }
    return icons.get(category, icons["default"])
