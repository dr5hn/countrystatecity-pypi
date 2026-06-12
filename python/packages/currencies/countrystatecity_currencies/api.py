"""Public API functions for currencies."""

from typing import List, Optional

from .loaders import DataLoader
from .models import Currency


def get_all_currencies() -> List[Currency]:
    """Get all currency entries (one per country).

    Returns:
        List[Currency]: List of all currency entries.

    Example:
        >>> currencies = get_all_currencies()
        >>> len(currencies) > 0
        True
    """
    data = DataLoader.load_currencies()
    return [Currency(**c) for c in data]


def get_currency_by_country(country_code: str) -> Optional[Currency]:
    """Get the currency for a specific country.

    Args:
        country_code: ISO2 country code (e.g., "US").

    Returns:
        Optional[Currency]: The currency if found, None otherwise.

    Example:
        >>> c = get_currency_by_country("US")
        >>> c.code
        'USD'
    """
    code_upper = country_code.upper()
    data = DataLoader.load_currencies()
    for c in data:
        if c["countryCode"] == code_upper:
            return Currency(**c)
    return None


def get_countries_by_currency(currency_code: str) -> List[Currency]:
    """Get all countries that use a specific currency code.

    Args:
        currency_code: ISO 4217 currency code (e.g., "EUR").

    Returns:
        List[Currency]: List of entries for countries using this currency.

    Example:
        >>> entries = get_countries_by_currency("EUR")
        >>> len(entries) > 1
        True
    """
    code_upper = currency_code.upper()
    data = DataLoader.load_currencies()
    return [Currency(**c) for c in data if c["code"] == code_upper]


def search_currencies(query: str) -> List[Currency]:
    """Search currencies by code, name, symbol, or country name.

    Args:
        query: Search query (case-insensitive).

    Returns:
        List[Currency]: List of currencies matching the query.

    Example:
        >>> results = search_currencies("dollar")
        >>> len(results) > 0
        True
    """
    query_lower = query.lower()
    data = DataLoader.load_currencies()
    results = []

    for c in data:
        if (
            query_lower in c["code"].lower()
            or query_lower in c["name"].lower()
            or query_lower in c["symbol"].lower()
            or query_lower in c["countryName"].lower()
            or query_lower in c["countryCode"].lower()
        ):
            results.append(Currency(**c))

    return results
