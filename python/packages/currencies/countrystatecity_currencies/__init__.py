"""Official currencies database with type hints and lazy loading.

This package provides access to a comprehensive database of currencies
with country associations, ISO 4217 codes, names, and symbols.

Example:
    >>> from countrystatecity_currencies import (
    ...     get_currency_by_country,
    ...     get_countries_by_currency,
    ... )
    >>> usd = get_currency_by_country("US")
    >>> euro_countries = get_countries_by_currency("EUR")
"""

__version__ = "1.0.5"

from .api import (
    get_all_currencies,
    get_countries_by_currency,
    get_currency_by_country,
    search_currencies,
)
from .models import Currency

__all__ = [
    # Version
    "__version__",
    # Models
    "Currency",
    # API
    "get_all_currencies",
    "get_currency_by_country",
    "get_countries_by_currency",
    "search_currencies",
]
