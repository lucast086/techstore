"""Jinja2 template filters for the application."""

from datetime import date, datetime
from typing import Optional

from app.utils.timezone import format_local_date, format_local_datetime, utc_to_local


def register_filters(templates):
    """Register custom Jinja2 filters for templates.

    Args:
        templates: Jinja2Templates instance to register filters with.
    """
    # Timezone conversion filters
    templates.env.filters["local_datetime"] = local_datetime_filter
    templates.env.filters["local_date"] = local_date_filter
    templates.env.filters["local_time"] = local_time_filter
    templates.env.filters["utc_to_local"] = utc_to_local_filter


def local_datetime_filter(
    dt: Optional[datetime], format_str: str = "%d/%m/%Y %H:%M"
) -> str:
    """Format UTC datetime to local timezone string.

    Args:
        dt: UTC datetime to format.
        format_str: strftime format string.

    Returns:
        Formatted datetime string in local timezone or empty string if None.

    Usage in templates:
        {{ sale.sale_date | local_datetime }}
        {{ sale.sale_date | local_datetime('%B %d, %Y at %I:%M %p') }}
    """
    if dt is None:
        return ""
    return format_local_datetime(dt, format_str)


def local_date_filter(
    dt: Optional[datetime | date], format_str: str = "%d/%m/%Y"
) -> str:
    """Format UTC datetime or date object as date in local timezone.

    Args:
        dt: UTC datetime or date object to format.
        format_str: strftime format string.

    Returns:
        Formatted date string in local timezone or empty string if None.

    Usage in templates:
        {{ sale.sale_date | local_date }}
        {{ sale.sale_date | local_date('%B %d, %Y') }}
        {{ closing.closing_date | local_date }}
    """
    if dt is None:
        return ""
    return format_local_date(dt, format_str)


def local_time_filter(dt: Optional[datetime], format_str: str = "%H:%M") -> str:
    """Format UTC datetime as time in local timezone.

    Args:
        dt: UTC datetime to format.
        format_str: strftime format string.

    Returns:
        Formatted time string in local timezone or empty string if None.

    Usage in templates:
        {{ sale.sale_date | local_time }}
        {{ sale.sale_date | local_time('%I:%M %p') }}
    """
    if dt is None:
        return ""

    local_dt = utc_to_local(dt)
    if local_dt is None:
        return ""
    return local_dt.strftime(format_str)


def utc_to_local_filter(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert UTC datetime to local timezone datetime object.

    Args:
        dt: UTC datetime to convert.

    Returns:
        Datetime in local timezone or None if input is None.

    Usage in templates:
        {% set local_dt = sale.sale_date | utc_to_local %}
    """
    return utc_to_local(dt)
