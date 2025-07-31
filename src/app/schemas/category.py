"""Category schemas for hierarchical product organization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    """Base category schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = Field(None, max_length=50)
    display_order: int = Field(default=0)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryNode(CategoryBase):
    """Category node for tree representation."""

    id: int
    level: int
    full_path: str
    direct_product_count: int = 0
    total_product_count: int = 0
    children: list["CategoryNode"] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# For recursive model
CategoryNode.model_rebuild()


class CategoryMove(BaseModel):
    """Schema for moving a category."""

    category_id: int
    new_parent_id: Optional[int] = None
    new_position: int = 0


class CategoryBulkUpdate(BaseModel):
    """Schema for bulk category updates."""

    category_ids: list[int]
    is_active: Optional[bool] = None


class CategoryTree(BaseModel):
    """Full category tree response."""

    categories: list[CategoryNode]
    total_count: int
    max_depth: int = 3


class CategoryImport(BaseModel):
    """Schema for importing categories."""

    name: str = Field(..., min_length=1, max_length=100)
    parent_path: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    display_order: int = Field(default=0)
    is_active: bool = True

    @field_validator("parent_path")
    @classmethod
    def validate_parent_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate parent path format."""
        if v and not v.strip():
            return None
        return v


class CategoryStats(BaseModel):
    """Category statistics."""

    total_categories: int
    active_categories: int
    total_products: int
    categories_with_products: int
    empty_categories: int
    max_depth_used: int
