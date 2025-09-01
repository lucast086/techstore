"""Timezone utilities for handling local dates and times."""

from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo

from app.config import settings


def get_local_timezone() -> ZoneInfo:
    """Get the configured local timezone.

    Returns:
        ZoneInfo object for the configured timezone.
    """
    return ZoneInfo(settings.TIMEZONE)


def get_local_datetime() -> datetime:
    """Get current datetime in local timezone.

    Returns:
        Current datetime in configured local timezone.
    """
    return datetime.now(get_local_timezone())


def get_local_date() -> date:
    """Get current date in local timezone.

    Returns:
        Current date in configured local timezone.
    """
    return get_local_datetime().date()


def utc_to_local(dt: datetime) -> datetime:
    """Convert UTC datetime to local timezone.

    Args:
        dt: Datetime in UTC (can be naive or aware).

    Returns:
        Datetime in local timezone.
    """
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(get_local_timezone())


def local_to_utc(dt: datetime) -> datetime:
    """Convert local datetime to UTC.

    Args:
        dt: Datetime in local timezone (can be naive or aware).

    Returns:
        Datetime in UTC.
    """
    if dt.tzinfo is None:
        # Assume naive datetime is in local timezone
        dt = dt.replace(tzinfo=get_local_timezone())
    return dt.astimezone(ZoneInfo("UTC"))


def format_local_datetime(
    dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """Format datetime in local timezone.

    Args:
        dt: Datetime to format (assumed UTC if naive).
        format_str: Format string for strftime.

    Returns:
        Formatted datetime string in local timezone, or empty string if dt is None.
    """
    if dt is None:
        return ""

    local_dt = utc_to_local(dt) if dt else None
    return local_dt.strftime(format_str) if local_dt else ""


def parse_local_date(date_str: str) -> date:
    """Parse a date string assuming local timezone.

    Args:
        date_str: Date string in ISO format (YYYY-MM-DD).

    Returns:
        Date object.

    Raises:
        ValueError: If date string is invalid.
    """
    return date.fromisoformat(date_str)


def is_today_local(check_date: date) -> bool:
    """Check if a date is today in local timezone.

    Args:
        check_date: Date to check.

    Returns:
        True if the date is today in local timezone.
    """
    return check_date == get_local_date()
