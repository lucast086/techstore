"""Search service for TechStore SaaS."""


class SearchService:
    """Service for handling product search logic."""

    # Demo data - later this will come from database
    DEMO_PRODUCTS = [
        {"id": 1, "name": "iPhone 14 Pro", "category": "smartphone", "price": 999.99},
        {
            "id": 2,
            "name": "Samsung Galaxy S23",
            "category": "smartphone",
            "price": 899.99,
        },
        {"id": 3, "name": "MacBook Pro M2", "category": "laptop", "price": 1299.99},
        {"id": 4, "name": "iPad Air", "category": "tablet", "price": 599.99},
        {"id": 5, "name": "AirPods Pro", "category": "audio", "price": 249.99},
        {"id": 6, "name": "Dell XPS 13", "category": "laptop", "price": 1199.99},
        {"id": 7, "name": "Surface Pro 9", "category": "tablet", "price": 1099.99},
        {"id": 8, "name": "Xiaomi Mi 13", "category": "smartphone", "price": 699.99},
        {"id": 9, "name": "OnePlus 11", "category": "smartphone", "price": 799.99},
        {"id": 10, "name": "Google Pixel 7", "category": "smartphone", "price": 699.99},
    ]

    @classmethod
    def search_products(
        cls, search_term: str, category: str | None = None, max_results: int = 10
    ) -> dict[str, any]:
        """
        Search products by term and optional category.

        Args:
            search_term: Text to search in product names
            category: Optional category filter
            max_results: Maximum number of results to return

        Returns:
            Dict with results, total count, and metadata
        """
        if not search_term or not search_term.strip():
            return {
                "results": [],
                "total": 0,
                "search_term": search_term,
                "message": "Please enter a search term",
            }

        search_term = search_term.lower().strip()

        # Filter by search term
        filtered_products = [
            product
            for product in cls.DEMO_PRODUCTS
            if search_term in product["name"].lower()
        ]

        # Filter by category if provided
        if category:
            filtered_products = [
                product
                for product in filtered_products
                if product["category"].lower() == category.lower()
            ]

        # Limit results
        limited_results = filtered_products[:max_results]

        return {
            "results": limited_results,
            "total": len(limited_results),
            "search_term": search_term,
            "category": category,
            "message": "Search completed successfully"
            if limited_results
            else f"No products found for '{search_term}'",
        }

    @classmethod
    def get_categories(cls) -> list[str]:
        """Get all available product categories."""
        categories = list({product["category"] for product in cls.DEMO_PRODUCTS})
        return sorted(categories)
