"""Public API functions for regions."""

from typing import List, Optional

from .loaders import DataLoader
from .models import CountryRegion


def get_all_regions() -> List[CountryRegion]:
    """Get all country region/subregion entries.

    Returns:
        List[CountryRegion]: List of all country-region entries.

    Example:
        >>> regions = get_all_regions()
        >>> len(regions) > 0
        True
    """
    data = DataLoader.load_regions()
    return [CountryRegion(**r) for r in data]


def get_region_by_country(country_code: str) -> Optional[CountryRegion]:
    """Get the region/subregion for a specific country.

    Args:
        country_code: ISO2 country code (e.g., "US").

    Returns:
        Optional[CountryRegion]: The entry if found, None otherwise.

    Example:
        >>> r = get_region_by_country("US")
        >>> r.region
        'Americas'
    """
    code_upper = country_code.upper()
    data = DataLoader.load_regions()
    for r in data:
        if r["countryCode"] == code_upper:
            return CountryRegion(**r)
    return None


def get_countries_by_region(region: str) -> List[CountryRegion]:
    """Get all countries in a region.

    Args:
        region: Region name (e.g., "Asia", "Europe").

    Returns:
        List[CountryRegion]: List of entries for countries in the region.

    Example:
        >>> entries = get_countries_by_region("Asia")
        >>> len(entries) > 1
        True
    """
    region_lower = region.lower()
    data = DataLoader.load_regions()
    return [
        CountryRegion(**r)
        for r in data
        if (r.get("region") or "").lower() == region_lower
    ]


def get_countries_by_subregion(subregion: str) -> List[CountryRegion]:
    """Get all countries in a subregion.

    Args:
        subregion: Subregion name (e.g., "Southern Asia").

    Returns:
        List[CountryRegion]: List of entries for countries in the subregion.

    Example:
        >>> entries = get_countries_by_subregion("Southern Asia")
        >>> len(entries) > 1
        True
    """
    subregion_lower = subregion.lower()
    data = DataLoader.load_regions()
    return [
        CountryRegion(**r)
        for r in data
        if (r.get("subregion") or "").lower() == subregion_lower
    ]


def get_all_region_names() -> List[str]:
    """Get all distinct region names, sorted alphabetically.

    Returns:
        List[str]: Sorted list of unique region names.

    Example:
        >>> names = get_all_region_names()
        >>> "Asia" in names
        True
    """
    data = DataLoader.load_regions()
    names = {r["region"] for r in data if r.get("region")}
    return sorted(names)


def get_all_subregion_names(region: Optional[str] = None) -> List[str]:
    """Get all distinct subregion names, sorted alphabetically.

    Args:
        region: Optional region name to filter subregions by.

    Returns:
        List[str]: Sorted list of unique subregion names.

    Example:
        >>> names = get_all_subregion_names("Asia")
        >>> "Southern Asia" in names
        True
    """
    data = DataLoader.load_regions()
    if region is not None:
        region_lower = region.lower()
        data = [r for r in data if (r.get("region") or "").lower() == region_lower]
    names = {r["subregion"] for r in data if r.get("subregion")}
    return sorted(names)


def search_regions(query: str) -> List[CountryRegion]:
    """Search by country name, country code, region, or subregion.

    Args:
        query: Search query (case-insensitive).

    Returns:
        List[CountryRegion]: List of entries matching the query.

    Example:
        >>> results = search_regions("asia")
        >>> len(results) > 0
        True
    """
    query_lower = query.lower()
    data = DataLoader.load_regions()
    results = []

    for r in data:
        if (
            query_lower in r["countryCode"].lower()
            or query_lower in r["countryName"].lower()
            or query_lower in (r.get("region") or "").lower()
            or query_lower in (r.get("subregion") or "").lower()
        ):
            results.append(CountryRegion(**r))

    return results
