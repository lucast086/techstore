"""Tests for search service business logic."""


from app.services.search_service import SearchService


class TestSearchService:
    """Test search service business logic."""

    def test_search_products_with_valid_term(self):
        """Test searching with valid search term."""
        result = SearchService.search_products("iphone")

        assert result["total"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["name"] == "iPhone 14 Pro"
        assert result["search_term"] == "iphone"
        assert "success" in result["message"].lower()

    def test_search_products_case_insensitive(self):
        """Test search is case insensitive."""
        result_lower = SearchService.search_products("iphone")
        result_upper = SearchService.search_products("IPHONE")
        result_mixed = SearchService.search_products("iPhone")

        assert result_lower["total"] == result_upper["total"] == result_mixed["total"]

    def test_search_products_empty_term(self):
        """Test search with empty term."""
        result = SearchService.search_products("")

        assert result["total"] == 0
        assert result["results"] == []
        assert "enter a search term" in result["message"].lower()

    def test_search_products_no_results(self):
        """Test search with term that has no matches."""
        result = SearchService.search_products("nonexistent")

        assert result["total"] == 0
        assert result["results"] == []
        assert "no products found" in result["message"].lower()

    def test_search_products_with_category_filter(self):
        """Test search with category filter."""
        result = SearchService.search_products("pro", category="smartphone")

        assert result["total"] >= 1
        for product in result["results"]:
            assert product["category"] == "smartphone"

    def test_search_products_max_results_limit(self):
        """Test max results limiting."""
        result = SearchService.search_products("a", max_results=3)  # Many matches

        assert len(result["results"]) <= 3

    def test_get_categories(self):
        """Test getting all categories."""
        categories = SearchService.get_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "smartphone" in categories
        assert "laptop" in categories
