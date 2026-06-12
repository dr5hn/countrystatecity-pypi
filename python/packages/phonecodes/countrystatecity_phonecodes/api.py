"""Public API functions for phonecodes."""

from typing import List, Optional

from .loaders import DataLoader
from .models import PhoneCode


def get_all_phonecodes() -> List[PhoneCode]:
    """Get all phone code entries (one per country).

    Returns:
        List[PhoneCode]: List of all phone code entries.

    Example:
        >>> phonecodes = get_all_phonecodes()
        >>> len(phonecodes) > 0
        True
    """
    data = DataLoader.load_phonecodes()
    return [PhoneCode(**p) for p in data]


def get_phonecode_by_country(country_code: str) -> Optional[PhoneCode]:
    """Get the phone code for a specific country.

    Args:
        country_code: ISO2 country code (e.g., "US").

    Returns:
        Optional[PhoneCode]: The phone code entry if found, None otherwise.

    Example:
        >>> p = get_phonecode_by_country("US")
        >>> p.phoneCode
        '1'
    """
    code_upper = country_code.upper()
    data = DataLoader.load_phonecodes()
    for p in data:
        if p["countryCode"] == code_upper:
            return PhoneCode(**p)
    return None


def get_countries_by_phonecode(phone_code: str) -> List[PhoneCode]:
    """Get all countries that share a specific phone code.

    Args:
        phone_code: International dialing code without + (e.g., "1").

    Returns:
        List[PhoneCode]: List of entries for countries using this phone code.

    Example:
        >>> entries = get_countries_by_phonecode("1")
        >>> len(entries) > 1
        True
    """
    code = phone_code.lstrip("+")
    data = DataLoader.load_phonecodes()
    return [PhoneCode(**p) for p in data if p["phoneCode"] == code]


def search_phonecodes(query: str) -> List[PhoneCode]:
    """Search phone codes by country name, country code, or phone code.

    Args:
        query: Search query (case-insensitive).

    Returns:
        List[PhoneCode]: List of phone code entries matching the query.

    Example:
        >>> results = search_phonecodes("united")
        >>> len(results) > 0
        True
    """
    query_lower = query.lower().lstrip("+")
    data = DataLoader.load_phonecodes()
    results = []

    for p in data:
        if (
            query_lower in p["phoneCode"].lower()
            or query_lower in p["countryCode"].lower()
            or query_lower in p["countryName"].lower()
        ):
            results.append(PhoneCode(**p))

    return results
