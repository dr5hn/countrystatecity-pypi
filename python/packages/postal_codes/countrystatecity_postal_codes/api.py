"""Public API functions for postal codes."""

import re
from typing import List, Optional

from .loaders import DataLoader
from .models import CountryPostalInfo, Postcode


def get_countries_with_postal_data() -> List[CountryPostalInfo]:
    """Get postal code format metadata for all countries.

    Returns:
        List[CountryPostalInfo]: List of all countries with postal metadata.

    Example:
        >>> countries = get_countries_with_postal_data()
        >>> len(countries) > 0
        True
    """
    data = DataLoader.load_countries()
    return [CountryPostalInfo(**c) for c in data]


def get_postal_info_by_country(country_code: str) -> Optional[CountryPostalInfo]:
    """Get postal code format metadata for a specific country.

    Args:
        country_code: ISO2 country code (e.g., "US").

    Returns:
        Optional[CountryPostalInfo]: The entry if found, None otherwise.

    Example:
        >>> info = get_postal_info_by_country("US")
        >>> info.postalCodeFormat
        '#####'
    """
    code_upper = country_code.upper()
    data = DataLoader.load_countries()
    for c in data:
        if c["countryCode"] == code_upper:
            return CountryPostalInfo(**c)
    return None


def get_postcodes_of_country(country_code: str) -> List[Postcode]:
    """Get all postcodes for a country (lazy loaded).

    Args:
        country_code: ISO2 country code (e.g., "AD").

    Returns:
        List[Postcode]: List of postcodes in the country. Empty if the
            country has no postcode data available.

    Example:
        >>> postcodes = get_postcodes_of_country("AD")
        >>> len(postcodes) > 0
        True
    """
    data = DataLoader.load_postcodes(country_code.upper())
    return [Postcode(**p) for p in data]


def get_postcode_by_code(country_code: str, code: str) -> Optional[Postcode]:
    """Get the first matching postcode entry within a country.

    Some postal codes cover multiple localities. Use ``get_postcodes_by_code``
    when every matching entry is required.

    Args:
        country_code: ISO2 country code (e.g., "AD").
        code: The postal code value (e.g., "AD100").

    Returns:
        Optional[Postcode]: The first matching postcode if found, None otherwise.

    Example:
        >>> pc = get_postcode_by_code("AD", "AD100")
        >>> pc is not None
        True
    """
    matches = get_postcodes_by_code(country_code, code)
    return matches[0] if matches else None


def get_postcodes_by_code(country_code: str, code: str) -> List[Postcode]:
    """Get every postcode entry matching a code within a country.

    Args:
        country_code: ISO2 country code (e.g., "BB").
        code: The postal code value (e.g., "BB18000").

    Returns:
        List[Postcode]: Every matching entry, including multiple localities
            that share the same code.

    Example:
        >>> matches = get_postcodes_by_code("BB", "BB18000")
        >>> len(matches) > 1
        True
    """
    code_upper = code.upper()
    postcodes = DataLoader.load_postcodes(country_code.upper())
    return [Postcode(**p) for p in postcodes if p["code"].upper() == code_upper]


def search_postcodes(country_code: str, query: str) -> List[Postcode]:
    """Search postcodes within a country by code or locality name.

    Args:
        country_code: ISO2 country code (e.g., "AD").
        query: Search query (case-insensitive).

    Returns:
        List[Postcode]: List of postcodes matching the query.

    Example:
        >>> results = search_postcodes("AD", "canillo")
        >>> len(results) > 0
        True
    """
    query_lower = query.lower()
    postcodes = DataLoader.load_postcodes(country_code.upper())
    results = []

    for p in postcodes:
        if (
            query_lower in p["code"].lower()
            or query_lower in (p.get("localityName") or "").lower()
        ):
            results.append(Postcode(**p))

    return results


def validate_postcode(country_code: str, code: str) -> bool:
    """Validate a postcode's format against the country's postal code regex.

    Args:
        country_code: ISO2 country code (e.g., "US").
        code: The postal code value to validate.

    Returns:
        bool: True if the code matches the country's known format. False if
            it doesn't match, or the country has no known format.

    Example:
        >>> validate_postcode("US", "10001")
        True
        >>> validate_postcode("US", "invalid")
        False
    """
    info = get_postal_info_by_country(country_code)
    if info is None or not info.postalCodeRegex:
        return False
    try:
        return re.fullmatch(info.postalCodeRegex, code) is not None
    except re.error:
        return False
