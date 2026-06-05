"""Official timezones database with type hints and lazy loading.

This package provides access to a comprehensive database of timezones
with country associations, GMT offsets, and time conversion utilities.

Example:
    >>> from countrystatecity_timezones import get_timezones_by_country, convert_time
    >>> us_timezones = get_timezones_by_country("US")
    >>> from datetime import datetime
    >>> result = convert_time(datetime(2024, 1, 1, 12, 0), "America/New_York", "Asia/Kolkata")
"""

__version__ = "1.0.0"

from .api import (
    convert_time,
    get_all_timezones,
    get_timezone_by_zone_name,
    get_timezones_by_country,
    get_timezones_by_offset,
    search_timezones,
)
from .models import Timezone

__all__ = [
    # Version
    "__version__",
    # Models
    "Timezone",
    # API
    "get_all_timezones",
    "get_timezones_by_country",
    "get_timezone_by_zone_name",
    "get_timezones_by_offset",
    "search_timezones",
    "convert_time",
]
