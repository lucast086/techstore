"""Timezone utilities for handling UTC/local time conversions."""

from datetime import date, datetime, time
from typing import Optional
from zoneinfo import ZoneInfo

from app.config import settings


def get_local_timezone() -> ZoneInfo:
    """Get the configured local timezone.

    Returns:
        ZoneInfo object for the configured timezone.
    """
    return ZoneInfo(settings.TIMEZONE)


def utc_to_local(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert UTC datetime to local timezone.

    Args:
        dt: UTC datetime to convert.

    Returns:
        Datetime in local timezone or None if input is None.
    """
    if dt is None:
        return None

    # Ensure datetime is UTC aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    # Convert to local timezone
    local_tz = get_local_timezone()
    return dt.astimezone(local_tz)


def local_to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert local datetime to UTC.

    Args:
        dt: Local datetime to convert.

    Returns:
        Datetime in UTC or None if input is None.
    """
    if dt is None:
        return None

    local_tz = get_local_timezone()

    # If datetime is naive, assume it's in local timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)

    # Convert to UTC
    return dt.astimezone(ZoneInfo("UTC"))


def get_local_now() -> datetime:
    """Get current time in local timezone.

    Returns:
        Current datetime in local timezone.
    """
    utc_now = datetime.now(ZoneInfo("UTC"))
    return utc_to_local(utc_now)


def get_local_today() -> date:
    """Get today's date in local timezone.

    Returns:
        Today's date in local timezone.
    """
    local_now = get_local_now()
    return local_now.date()


# Alias for backwards compatibility
get_local_date = get_local_today


def get_cash_register_business_day() -> date:
    """Get current business day for cash register operations.

    Business day uses a 4 AM cutoff: transactions before 4 AM are considered
    part of the previous calendar day.

    Examples:
        - 2025-11-12 23:50 → Business day: 2025-11-12
        - 2025-11-13 01:30 → Business day: 2025-11-12 (before 4 AM cutoff)
        - 2025-11-13 04:30 → Business day: 2025-11-13 (after 4 AM cutoff)

    This allows for:
    - Night shifts to complete without day change issues
    - Sales after midnight to be counted in the previous day's register
    - Consistent cash register closing regardless of exact closing time

    Returns:
        Business day date for cash register operations.
    """
    from datetime import timedelta

    CUTOFF_HOUR = 4  # 4 AM cutoff

    local_now = get_local_now()

    # If before cutoff hour, consider it previous calendar day
    if local_now.hour < CUTOFF_HOUR:
        return (local_now - timedelta(days=1)).date()

    return local_now.date()


def get_utc_now() -> datetime:
    """Get current time in UTC.

    Returns:
        Current datetime in UTC.
    """
    return datetime.now(ZoneInfo("UTC"))


def get_utc_today() -> date:
    """Get today's date in UTC.

    Returns:
        Today's date in UTC.
    """
    utc_now = get_utc_now()
    return utc_now.date()


def local_date_to_utc_range(local_date: date) -> tuple[datetime, datetime]:
    """Convert a local date to UTC datetime range for database queries.

    This is useful when querying database records for a specific local date,
    as the database stores timestamps in UTC.

    Args:
        local_date: Date in local timezone.

    Returns:
        Tuple of (start_utc, end_utc) representing the UTC datetime range
        for the given local date.
    """
    local_tz = get_local_timezone()

    # Create start of day in local timezone
    local_start = datetime.combine(local_date, time.min).replace(tzinfo=local_tz)

    # Create end of day in local timezone
    local_end = datetime.combine(local_date, time.max).replace(tzinfo=local_tz)

    # Convert to UTC
    utc_start = local_start.astimezone(ZoneInfo("UTC"))
    utc_end = local_end.astimezone(ZoneInfo("UTC"))

    return utc_start, utc_end


def format_local_datetime(
    dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """Format datetime in local timezone.

    Args:
        dt: UTC datetime to format.
        format_str: strftime format string.

    Returns:
        Formatted datetime string in local timezone or empty string if None.
    """
    if dt is None:
        return ""

    local_dt = utc_to_local(dt)
    return local_dt.strftime(format_str)


def format_local_date(
    dt: Optional[datetime | date], format_str: str = "%Y-%m-%d"
) -> str:
    """Format datetime or date as date in local timezone.

    Args:
        dt: UTC datetime or date object to format.
        format_str: strftime format string.

    Returns:
        Formatted date string in local timezone or empty string if None.
    """
    if dt is None:
        return ""

    # If it's already a date object (not datetime), just format it directly
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt.strftime(format_str)

    # Otherwise, convert datetime to local timezone and format
    local_dt = utc_to_local(dt)
    if local_dt is None:
        return ""
    return local_dt.strftime(format_str)
