"""Official postal codes database with type hints and lazy loading.

This package provides access to postal/ZIP codes for 100+ countries,
along with per-country postal code format and validation regex.

Example:
    >>> from countrystatecity_postal_codes import (
    ...     get_postcodes_of_country,
    ...     validate_postcode,
    ... )
    >>> postcodes = get_postcodes_of_country("US")
    >>> validate_postcode("US", "10001")
"""

__version__ = "1.0.2"

from .api import (
    get_countries_with_postal_data,
    get_postal_info_by_country,
    get_postcode_by_code,
    get_postcodes_by_code,
    get_postcodes_of_country,
    search_postcodes,
    validate_postcode,
)
from .models import CountryPostalInfo, Postcode

__all__ = [
    # Version
    "__version__",
    # Models
    "CountryPostalInfo",
    "Postcode",
    # API
    "get_countries_with_postal_data",
    "get_postal_info_by_country",
    "get_postcodes_of_country",
    "get_postcode_by_code",
    "get_postcodes_by_code",
    "search_postcodes",
    "validate_postcode",
]
