"""Tests for HTMX search endpoints that return HTML."""

from fastapi.testclient import TestClient


def test_search_htmx_endpoint_returns_html(client: TestClient):
    """Test HTMX search endpoint returns properly formatted HTML."""
    # First verify API works (dependency)
    api_response = client.get("/api/v1/search/products?q=iphone")
    assert api_response.status_code == 200

    # Test HTMX endpoint that calls the API internally
    response = client.post("/htmx/search/products", data={"q": "iphone"})

    assert response.status_code == 200
    html_content = response.text

    # Verify it's HTML, not JSON
    assert not html_content.startswith("{")
    assert not html_content.startswith("[")

    # Verify product is displayed
    assert "iPhone 14 Pro" in html_content

    # Verify HTML structure
    assert '<div class="result-item' in html_content
    assert "<strong>iPhone 14 Pro</strong>" in html_content
    assert "Found 1 products" in html_content

    # Verify styling elements
    assert "text-success" in html_content
    assert "fas fa-" in html_content  # Font Awesome icons


def test_search_htmx_endpoint_empty_query(client: TestClient):
    """Test HTMX search endpoint with empty query returns proper message."""
    # Test with completely empty query
    response = client.post("/htmx/search/products", data={"q": " "})  # Space instead of empty

    assert response.status_code == 200
    html_content = response.text

    # Should show empty state message
    assert "Enter a search term" in html_content
    assert 'class="text-muted"' in html_content
    assert '<i class="fas fa-search">' in html_content


def test_search_htmx_endpoint_no_results(client: TestClient):
    """Test HTMX search endpoint when no products match."""
    response = client.post("/htmx/search/products", data={"q": "nonexistentproduct"})

    assert response.status_code == 200
    html_content = response.text

    # Should show no results message
    assert "No products found" in html_content
    assert 'class="text-warning"' in html_content
    assert '<i class="fas fa-exclamation-triangle">' in html_content


def test_search_htmx_endpoint_with_category(client: TestClient):
    """Test HTMX search endpoint with category filter."""
    response = client.post("/htmx/search/products", data={"q": "pro", "category": "smartphone"})

    assert response.status_code == 200
    html_content = response.text

    # Should find smartphone products
    assert "iPhone 14 Pro" in html_content
    assert "smartphone" in html_content.lower()


def test_search_htmx_endpoint_multiple_results(client: TestClient):
    """Test HTMX search endpoint with multiple results."""
    response = client.post("/htmx/search/products", data={"q": "pro"})

    assert response.status_code == 200
    html_content = response.text

    # Should show multiple products
    assert "iPhone 14 Pro" in html_content
    assert "AirPods Pro" in html_content
    assert "Surface Pro 9" in html_content

    # Should show correct count (4 products: iPhone 14 Pro, AirPods Pro, Surface Pro 9, MacBook Pro M2)
    assert "Found 4 products" in html_content


def test_categories_htmx_endpoint(client: TestClient):
    """Test HTMX categories endpoint returns HTML options."""
    # First verify API works
    api_response = client.get("/api/v1/search/categories")
    assert api_response.status_code == 200

    # Test HTMX endpoint
    response = client.get("/htmx/search/categories")

    assert response.status_code == 200
    html_content = response.text

    # Should return HTML options
    assert '<option value="">All Categories</option>' in html_content
    assert '<option value="smartphone">Smartphone</option>' in html_content
    assert '<option value="laptop">Laptop</option>' in html_content
    assert '<option value="tablet">Tablet</option>' in html_content
