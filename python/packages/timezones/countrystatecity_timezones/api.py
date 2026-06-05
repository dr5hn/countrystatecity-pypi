"""Public API functions for timezones."""

import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
else:
    from backports.zoneinfo import ZoneInfo  # type: ignore[import-not-found,no-redef]

from .loaders import DataLoader
from .models import Timezone


def get_all_timezones() -> List[Timezone]:
    """Get all timezones.

    Returns:
        List[Timezone]: List of all timezone entries.

    Example:
        >>> timezones = get_all_timezones()
        >>> len(timezones) > 0
        True
    """
    data = DataLoader.load_timezones()
    return [Timezone(**tz) for tz in data]


def get_timezones_by_country(country_code: str) -> List[Timezone]:
    """Get all timezones for a country.

    Args:
        country_code: ISO2 country code (e.g., "US").

    Returns:
        List[Timezone]: List of timezones for the country.

    Example:
        >>> us_timezones = get_timezones_by_country("US")
        >>> len(us_timezones) > 0
        True
    """
    code_upper = country_code.upper()
    data = DataLoader.load_timezones()
    return [Timezone(**tz) for tz in data if tz["countryCode"] == code_upper]


def get_timezone_by_zone_name(zone_name: str) -> Optional[Timezone]:
    """Get a timezone by its IANA zone name.

    Args:
        zone_name: IANA timezone name (e.g., "America/New_York").

    Returns:
        Optional[Timezone]: The timezone if found, None otherwise.

    Example:
        >>> tz = get_timezone_by_zone_name("America/New_York")
        >>> tz is not None
        True
    """
    data = DataLoader.load_timezones()
    for tz in data:
        if tz["zoneName"] == zone_name:
            return Timezone(**tz)
    return None


def get_timezones_by_offset(gmt_offset: int) -> List[Timezone]:
    """Get all timezones with a specific GMT offset (in seconds).

    Args:
        gmt_offset: GMT offset in seconds (e.g., -18000 for UTC-05:00).

    Returns:
        List[Timezone]: List of timezones with the given offset.

    Example:
        >>> tzs = get_timezones_by_offset(-18000)
        >>> len(tzs) > 0
        True
    """
    data = DataLoader.load_timezones()
    return [Timezone(**tz) for tz in data if tz["gmtOffset"] == gmt_offset]


def search_timezones(query: str) -> List[Timezone]:
    """Search timezones by zone name, timezone name, or abbreviation.

    Args:
        query: Search query (case-insensitive).

    Returns:
        List[Timezone]: List of timezones matching the query.

    Example:
        >>> results = search_timezones("eastern")
        >>> len(results) > 0
        True
    """
    query_lower = query.lower()
    data = DataLoader.load_timezones()
    results = []

    for tz in data:
        if (
            query_lower in tz["zoneName"].lower()
            or query_lower in tz["tzName"].lower()
            or query_lower in tz["abbreviation"].lower()
        ):
            results.append(Timezone(**tz))

    return results


def convert_time(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert a datetime from one timezone to another.

    Args:
        dt: The datetime to convert (naive datetimes are assumed to be in from_tz).
        from_tz: IANA timezone name for the source (e.g., "America/New_York").
        to_tz: IANA timezone name for the target (e.g., "Asia/Kolkata").

    Returns:
        datetime: The converted datetime in the target timezone.

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 1, 12, 0, 0)
        >>> result = convert_time(dt, "America/New_York", "Asia/Kolkata")
        >>> result.hour
        22
    """
    source_tz = ZoneInfo(from_tz)  # type: ignore[abstract]
    target_tz = ZoneInfo(to_tz)  # type: ignore[abstract]

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=source_tz)
    else:
        dt = dt.astimezone(source_tz)

    return dt.astimezone(target_tz)
