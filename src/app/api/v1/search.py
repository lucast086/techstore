"""Search API endpoints for TechStore SaaS."""


from fastapi import APIRouter, Query

from app.schemas.search import CategoryResponse, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/products", response_model=SearchResponse)
async def search_products_api(
    q: str = Query(..., description="Search term"),
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
):
    """
    Search products API endpoint.

    Pure business logic endpoint that returns JSON data.
    Can be consumed by:
    - HTMX web interface
    - Mobile applications
    - External integrations
    - Admin dashboards
    """
    result = SearchService.search_products(search_term=q, category=category, max_results=limit)

    return SearchResponse(**result)


@router.get("/categories", response_model=CategoryResponse)
async def get_categories_api():
    """Get all available product categories."""
    categories = SearchService.get_categories()
    return CategoryResponse(categories=categories)
