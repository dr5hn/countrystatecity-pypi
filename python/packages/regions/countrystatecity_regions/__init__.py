"""Official regions and subregions database with type hints and lazy loading.

This package provides access to country-to-region and country-to-subregion
associations (continents and geographic subregions) for 250+ countries.

Example:
    >>> from countrystatecity_regions import (
    ...     get_region_by_country,
    ...     get_countries_by_region,
    ... )
    >>> us = get_region_by_country("US")
    >>> asian_countries = get_countries_by_region("Asia")
"""

__version__ = "1.0.0"

from .api import (
    get_all_region_names,
    get_all_regions,
    get_all_subregion_names,
    get_countries_by_region,
    get_countries_by_subregion,
    get_region_by_country,
    search_regions,
)
from .models import CountryRegion

__all__ = [
    # Version
    "__version__",
    # Models
    "CountryRegion",
    # API
    "get_all_regions",
    "get_region_by_country",
    "get_countries_by_region",
    "get_countries_by_subregion",
    "get_all_region_names",
    "get_all_subregion_names",
    "search_regions",
]
