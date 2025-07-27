"""Tests for search API endpoints - JSON responses only."""

from fastapi.testclient import TestClient


def test_search_products_api_returns_json(client: TestClient):
    """Test search products API endpoint returns proper JSON structure."""
    response = client.get("/api/v1/search/products?q=iphone")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()

    # Verify JSON structure
    assert "results" in data
    assert "total" in data
    assert "search_term" in data
    assert "message" in data

    # Verify search worked
    assert data["search_term"] == "iphone"
    assert data["total"] >= 1

    # Verify product structure
    assert isinstance(data["results"], list)
    if data["results"]:
        product = data["results"][0]
        assert "id" in product
        assert "name" in product
        assert "category" in product
        assert "price" in product
        assert product["name"] == "iPhone 14 Pro"


def test_search_products_api_with_category_filter(client: TestClient):
    """Test search API with category filter returns only matching categories."""
    response = client.get("/api/v1/search/products?q=pro&category=smartphone")

    assert response.status_code == 200
    data = response.json()

    # All results should be smartphones
    for product in data["results"]:
        assert product["category"] == "smartphone"

    # Should find iPhone 14 Pro
    product_names = [p["name"] for p in data["results"]]
    assert "iPhone 14 Pro" in product_names


def test_search_products_api_empty_query_returns_empty(client: TestClient):
    """Test search API with empty query returns empty results."""
    response = client.get("/api/v1/search/products?q=")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["results"] == []
    assert data["search_term"] == ""
    assert "enter a search term" in data["message"].lower()


def test_search_products_api_no_matches(client: TestClient):
    """Test search API when no products match."""
    response = client.get("/api/v1/search/products?q=nonexistentproduct")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["results"] == []
    assert data["search_term"] == "nonexistentproduct"
    assert "no products found" in data["message"].lower()


def test_search_products_api_case_insensitive(client: TestClient):
    """Test search API is case insensitive."""
    responses = [
        client.get("/api/v1/search/products?q=iphone"),
        client.get("/api/v1/search/products?q=IPHONE"),
        client.get("/api/v1/search/products?q=iPhone"),
    ]

    # All should return same results
    for response in responses:
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["results"][0]["name"] == "iPhone 14 Pro"


def test_search_products_api_limit_parameter(client: TestClient):
    """Test search API respects limit parameter."""
    response = client.get("/api/v1/search/products?q=pro&limit=2")

    assert response.status_code == 200
    data = response.json()

    # Should return max 2 results even if more match
    assert len(data["results"]) <= 2


def test_get_categories_api_returns_list(client: TestClient):
    """Test get categories API endpoint returns proper JSON list."""
    response = client.get("/api/v1/search/categories")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()

    assert "categories" in data
    assert isinstance(data["categories"], list)
    assert len(data["categories"]) > 0

    # Verify expected categories exist
    categories = data["categories"]
    assert "smartphone" in categories
    assert "laptop" in categories
    assert "tablet" in categories
    assert "audio" in categories


def test_search_api_invalid_category(client: TestClient):
    """Test search API with invalid category."""
    response = client.get("/api/v1/search/products?q=pro&category=invalidcategory")

    assert response.status_code == 200
    data = response.json()

    # Should return no results for invalid category
    assert data["total"] == 0
    assert data["results"] == []
