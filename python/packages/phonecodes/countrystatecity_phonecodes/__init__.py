"""Official phonecodes database with type hints and lazy loading.

This package provides access to a comprehensive database of international
phone/dialing codes with country associations.

Example:
    >>> from countrystatecity_phonecodes import (
    ...     get_phonecode_by_country,
    ...     get_countries_by_phonecode,
    ... )
    >>> us = get_phonecode_by_country("US")
    >>> plus1_countries = get_countries_by_phonecode("1")
"""

__version__ = "1.0.0"

from .api import (
    get_all_phonecodes,
    get_countries_by_phonecode,
    get_phonecode_by_country,
    search_phonecodes,
)
from .models import PhoneCode

__all__ = [
    # Version
    "__version__",
    # Models
    "PhoneCode",
    # API
    "get_all_phonecodes",
    "get_phonecode_by_country",
    "get_countries_by_phonecode",
    "search_phonecodes",
]
