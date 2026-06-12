"""Official country name translations database with type hints and lazy loading.

This package provides access to country name translations across 19 languages
with country associations and language codes.

Example:
    >>> from countrystatecity_translations import (
    ...     get_translation,
    ...     get_translations_by_language,
    ... )
    >>> t = get_translation("DE", "fr")
    >>> french_countries = get_translations_by_language("fr")
"""

__version__ = "1.0.3"

from .api import (
    get_all_translations,
    get_translation,
    get_translations_by_country,
    get_translations_by_language,
    search_translations,
)
from .models import Translation

__all__ = [
    # Version
    "__version__",
    # Models
    "Translation",
    # API
    "get_all_translations",
    "get_translations_by_country",
    "get_translations_by_language",
    "get_translation",
    "search_translations",
]
