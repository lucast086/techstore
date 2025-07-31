"""Category service for hierarchical product organization."""

import logging
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Category, Product
from app.schemas.category import (
    CategoryCreate,
    CategoryNode,
    CategoryStats,
    CategoryUpdate,
)

logger = logging.getLogger(__name__)


class EnhancedCategoryService:
    """Service for managing hierarchical categories."""

    def __init__(self, db: Session):
        """Initialize category service.

        Args:
            db: Database session.
        """
        self.db = db
        self.max_depth = 3

    async def get_category(self, category_id: int) -> Optional[Category]:
        """Get a single category by ID.

        Args:
            category_id: Category ID.

        Returns:
            Category if found, None otherwise.
        """
        return self.db.query(Category).filter(Category.id == category_id).first()

    async def get_categories_flat(
        self, include_inactive: bool = False
    ) -> list[Category]:
        """Get all categories in a flat list ordered for display.

        Args:
            include_inactive: Whether to include inactive categories.

        Returns:
            Flat list of categories ordered by hierarchy.
        """
        query = self.db.query(Category)
        if not include_inactive:
            query = query.filter(Category.is_active.is_(True))

        return query.order_by(Category.full_path).all()

    async def get_category_tree(
        self, include_inactive: bool = False
    ) -> list[CategoryNode]:
        """Get all categories organized in tree structure.

        Args:
            include_inactive: Whether to include inactive categories.

        Returns:
            List of root category nodes with children.
        """
        logger.info("Fetching category tree")

        # Base query
        query = self.db.query(
            Category,
            func.count(Product.id).label("product_count"),
        ).outerjoin(Product, Category.id == Product.category_id)

        if not include_inactive:
            query = query.filter(Category.is_active.is_(True))

        # Group by category
        categories = query.group_by(Category.id).all()

        # Build tree structure
        category_map = {}
        roots = []

        for cat, count in categories:
            node = CategoryNode(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                parent_id=cat.parent_id,
                icon=cat.icon,
                display_order=cat.display_order,
                is_active=cat.is_active,
                level=cat.level or 0,
                full_path=cat.full_path or cat.name,
                direct_product_count=count,
                children=[],
                created_at=cat.created_at,
                updated_at=cat.updated_at,
            )
            category_map[cat.id] = node

            if cat.parent_id is None:
                roots.append(node)

        # Link children to parents
        for cat, _ in categories:
            if cat.parent_id and cat.parent_id in category_map:
                category_map[cat.parent_id].children.append(category_map[cat.id])

        # Calculate total product counts
        for root in roots:
            self._calculate_total_products(root)

        # Sort by display order
        self._sort_tree(roots)
        return roots

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category.

        Args:
            category_data: Category creation data.

        Returns:
            Created category.

        Raises:
            ValueError: If validation fails.
        """
        logger.info(f"Creating category: {category_data.name}")

        # Validate parent and depth
        level = 0
        full_path = category_data.name

        if category_data.parent_id:
            parent = await self._get_category(category_data.parent_id)
            if not parent.is_active:
                raise ValueError("Cannot add category under inactive parent")

            level = (parent.level or 0) + 1
            if level >= self.max_depth:
                raise ValueError(f"Maximum nesting depth ({self.max_depth}) exceeded")

            full_path = f"{parent.full_path or parent.name}/{category_data.name}"

        # Check for duplicate names at same level
        existing = (
            self.db.query(Category)
            .filter(
                Category.name == category_data.name,
                Category.parent_id == category_data.parent_id,
            )
            .first()
        )
        if existing:
            raise ValueError(
                f"Category '{category_data.name}' already exists at this level"
            )

        # Create category
        category = Category(
            **category_data.model_dump(),
            level=level,
            full_path=full_path,
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        logger.info(f"Created category: {category.id}")
        return category

    async def update_category(
        self, category_id: int, category_data: CategoryUpdate
    ) -> Category:
        """Update a category.

        Args:
            category_id: Category ID to update.
            category_data: Update data.

        Returns:
            Updated category.

        Raises:
            ValueError: If validation fails.
        """
        logger.info(f"Updating category: {category_id}")

        category = await self._get_category(category_id)

        # Handle parent change
        if (
            category_data.parent_id is not None
            and category_data.parent_id != category.parent_id
        ):
            await self._validate_move(category, category_data.parent_id)
            await self._move_category(category, category_data.parent_id)

        # Check for duplicate names at same level if name is changing
        if category_data.name and category_data.name != category.name:
            existing = (
                self.db.query(Category)
                .filter(
                    Category.name == category_data.name,
                    Category.parent_id == category.parent_id,
                    Category.id != category_id,
                )
                .first()
            )
            if existing:
                raise ValueError(
                    f"Category '{category_data.name}' already exists at this level"
                )

        # Update fields
        update_dict = category_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if field != "parent_id":  # Already handled
                setattr(category, field, value)

        # Update path if name changed
        if category_data.name and category_data.name != category.name:
            await self._update_paths(category)

        self.db.commit()
        self.db.refresh(category)

        logger.info(f"Updated category: {category.id}")
        return category

    async def delete_category(self, category_id: int, force: bool = False) -> bool:
        """Delete a category.

        Args:
            category_id: Category ID to delete.
            force: If True, performs hard delete. Otherwise, soft delete.

        Returns:
            True if successful.

        Raises:
            ValueError: If category has products or subcategories.
        """
        logger.info(f"Deleting category: {category_id} (force={force})")

        category = await self._get_category(category_id)

        # Check for products
        product_count = (
            self.db.query(Product).filter(Product.category_id == category_id).count()
        )
        if product_count > 0:
            raise ValueError(f"Cannot delete category with {product_count} products")

        # Check for subcategories
        subcat_count = (
            self.db.query(Category).filter(Category.parent_id == category_id).count()
        )
        if subcat_count > 0:
            raise ValueError(
                f"Cannot delete category with {subcat_count} subcategories"
            )

        if force:
            self.db.delete(category)
        else:
            category.is_active = False

        self.db.commit()

        logger.info(f"{'Hard' if force else 'Soft'} deleted category: {category_id}")
        return True

    async def reorder_categories(
        self, parent_id: Optional[int], order: list[int]
    ) -> bool:
        """Reorder categories within a parent.

        Args:
            parent_id: Parent category ID (None for root).
            order: List of category IDs in new order.

        Returns:
            True if successful.
        """
        logger.info(f"Reordering categories under parent: {parent_id}")

        # Update display_order for each category
        for position, category_id in enumerate(order):
            self.db.query(Category).filter(Category.id == category_id).update(
                {"display_order": position}
            )

        self.db.commit()
        return True

    async def get_category_stats(self) -> CategoryStats:
        """Get category statistics.

        Returns:
            Category statistics.
        """
        total_categories = self.db.query(Category).count()
        active_categories = (
            self.db.query(Category).filter(Category.is_active.is_(True)).count()
        )

        # Get product counts
        categories_with_products = (
            self.db.query(func.count(func.distinct(Product.category_id)))
            .select_from(Product)
            .scalar()
            or 0
        )

        total_products = self.db.query(Product).count()

        # Get max depth
        max_depth = (
            self.db.query(func.max(Category.level)).scalar() or 0
        ) + 1  # Level is 0-indexed

        empty_categories = active_categories - categories_with_products

        return CategoryStats(
            total_categories=total_categories,
            active_categories=active_categories,
            total_products=total_products,
            categories_with_products=categories_with_products,
            empty_categories=empty_categories,
            max_depth_used=max_depth,
        )

    async def search_categories(
        self, query: str, include_inactive: bool = False
    ) -> list[Category]:
        """Search categories by name or description.

        Args:
            query: Search query.
            include_inactive: Whether to include inactive categories.

        Returns:
            List of matching categories.
        """
        search_term = f"%{query}%"
        q = self.db.query(Category).filter(
            Category.name.ilike(search_term) | Category.description.ilike(search_term)
        )

        if not include_inactive:
            q = q.filter(Category.is_active.is_(True))

        return q.order_by(Category.full_path).all()

    async def _get_category(self, category_id: Optional[int]) -> Optional[Category]:
        """Get category by ID.

        Args:
            category_id: Category ID.

        Returns:
            Category if found.

        Raises:
            ValueError: If category not found.
        """
        if category_id is None:
            return None

        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise ValueError(f"Category {category_id} not found")
        return category

    async def _validate_move(self, category: Category, new_parent_id: Optional[int]):
        """Validate category move operation.

        Args:
            category: Category to move.
            new_parent_id: New parent ID.

        Raises:
            ValueError: If move is invalid.
        """
        if new_parent_id is None:
            return  # Moving to root is always valid

        # Check for circular reference
        current_id = new_parent_id
        while current_id:
            if current_id == category.id:
                raise ValueError("Circular reference detected")
            parent = await self._get_category(current_id)
            current_id = parent.parent_id if parent else None

        # Check depth
        new_parent = await self._get_category(new_parent_id)
        new_level = (new_parent.level or 0) + 1
        subtree_depth = self._get_subtree_depth(category)

        if new_level + subtree_depth > self.max_depth:
            raise ValueError(f"Move would exceed maximum depth ({self.max_depth})")

    async def _move_category(self, category: Category, new_parent_id: Optional[int]):
        """Move a category to a new parent.

        Args:
            category: Category to move.
            new_parent_id: New parent ID.
        """
        old_path = category.full_path or category.name
        old_level = category.level or 0

        if new_parent_id:
            new_parent = await self._get_category(new_parent_id)
            new_level = (new_parent.level or 0) + 1
            new_path = f"{new_parent.full_path or new_parent.name}/{category.name}"
        else:
            new_level = 0
            new_path = category.name

        level_diff = new_level - old_level

        # Update the category
        category.parent_id = new_parent_id
        category.level = new_level
        category.full_path = new_path

        # Update all descendants
        descendants = (
            self.db.query(Category)
            .filter(Category.full_path.like(f"{old_path}/%"))
            .all()
        )

        for desc in descendants:
            # Update level
            desc.level = (desc.level or 0) + level_diff
            # Update path
            if desc.full_path:
                desc.full_path = desc.full_path.replace(old_path, new_path, 1)

    async def _update_paths(self, category: Category):
        """Update paths after category name change.

        Args:
            category: Category with updated name.
        """
        if category.parent_id:
            parent = await self._get_category(category.parent_id)
            new_path = f"{parent.full_path or parent.name}/{category.name}"
        else:
            new_path = category.name

        old_path = category.full_path or category.name

        # Update the category
        category.full_path = new_path

        # Update all descendants
        descendants = (
            self.db.query(Category)
            .filter(Category.full_path.like(f"{old_path}/%"))
            .all()
        )

        for desc in descendants:
            if desc.full_path:
                desc.full_path = desc.full_path.replace(old_path, new_path, 1)

    def _get_subtree_depth(self, category: Category) -> int:
        """Get the maximum depth of a category's subtree.

        Args:
            category: Root category of subtree.

        Returns:
            Maximum depth of subtree.
        """
        max_depth = 0

        descendants = (
            self.db.query(Category)
            .filter(Category.full_path.like(f"{category.full_path}/%"))
            .all()
        )

        for desc in descendants:
            depth = (desc.level or 0) - (category.level or 0)
            max_depth = max(max_depth, depth)

        return max_depth

    def _calculate_total_products(self, node: CategoryNode) -> int:
        """Calculate total products including subcategories.

        Args:
            node: Category node.

        Returns:
            Total product count.
        """
        total = node.direct_product_count

        for child in node.children:
            total += self._calculate_total_products(child)

        node.total_product_count = total
        return total

    def _sort_tree(self, nodes: list[CategoryNode]):
        """Recursively sort tree nodes by display_order and name.

        Args:
            nodes: List of nodes to sort.
        """
        nodes.sort(key=lambda x: (x.display_order, x.name))
        for node in nodes:
            if node.children:
                self._sort_tree(node.children)
