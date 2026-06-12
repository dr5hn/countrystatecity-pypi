"""Public API functions for translations."""

from typing import List, Optional

from .loaders import DataLoader
from .models import Translation


def get_all_translations() -> List[Translation]:
    """Get all translation entries.

    Returns:
        List[Translation]: List of all translation entries.

    Example:
        >>> translations = get_all_translations()
        >>> len(translations) > 0
        True
    """
    data = DataLoader.load_translations()
    return [Translation(**t) for t in data]


def get_translations_by_country(country_code: str) -> List[Translation]:
    """Get all translations for a specific country.

    Args:
        country_code: ISO2 country code (e.g., "DE").

    Returns:
        List[Translation]: All language translations for the country.

    Example:
        >>> translations = get_translations_by_country("DE")
        >>> len(translations) > 0
        True
    """
    code_upper = country_code.upper()
    data = DataLoader.load_translations()
    return [Translation(**t) for t in data if t["countryCode"] == code_upper]


def get_translations_by_language(lang: str) -> List[Translation]:
    """Get all country translations for a specific language.

    Args:
        lang: Language code (e.g., "fr", "zh-CN").

    Returns:
        List[Translation]: All country translations in that language.

    Example:
        >>> translations = get_translations_by_language("fr")
        >>> len(translations) > 0
        True
    """
    data = DataLoader.load_translations()
    return [Translation(**t) for t in data if t["lang"].lower() == lang.lower()]


def get_translation(country_code: str, lang: str) -> Optional[Translation]:
    """Get a specific translation for a country in a given language.

    Args:
        country_code: ISO2 country code (e.g., "US").
        lang: Language code (e.g., "fr").

    Returns:
        Optional[Translation]: The translation if found, None otherwise.

    Example:
        >>> t = get_translation("US", "fr")
        >>> t.translation
        'États-Unis'
    """
    code_upper = country_code.upper()
    data = DataLoader.load_translations()
    for t in data:
        if t["countryCode"] == code_upper and t["lang"].lower() == lang.lower():
            return Translation(**t)
    return None


def search_translations(query: str) -> List[Translation]:
    """Search translations by translated name or country name.

    Args:
        query: Search query (case-insensitive).

    Returns:
        List[Translation]: List of translations matching the query.

    Example:
        >>> results = search_translations("Allemagne")
        >>> len(results) > 0
        True
    """
    query_lower = query.lower()
    data = DataLoader.load_translations()
    return [
        Translation(**t)
        for t in data
        if query_lower in t["translation"].lower()
        or query_lower in t["countryName"].lower()
    ]
