"""Search schemas for TechStore SaaS."""


from pydantic import BaseModel


class ProductSchema(BaseModel):
    """Product schema for API responses."""

    id: int
    name: str
    category: str
    price: float


class SearchResponse(BaseModel):
    """Search response schema for API endpoints."""

    results: list[ProductSchema]
    total: int
    search_term: str
    category: str | None = None
    message: str


class CategoryResponse(BaseModel):
    """Category response schema for API endpoints."""

    categories: list[str]
