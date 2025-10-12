"""Template utilities for the application."""

from fastapi.templating import Jinja2Templates

from app.utils.template_filters import register_filters


def create_templates(directory: str = "src/app/templates") -> Jinja2Templates:
    """Create Jinja2Templates instance with custom filters registered.

    Args:
        directory: Template directory path.

    Returns:
        Configured Jinja2Templates instance with custom filters.
    """
    templates = Jinja2Templates(directory=directory)
    register_filters(templates)
    return templates
