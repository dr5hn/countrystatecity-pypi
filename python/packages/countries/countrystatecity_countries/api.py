"""Public API functions for countries, states, and cities."""

from typing import List, Optional

from .loaders import DataLoader
from .models import City, Country, State

# Countries API


def get_countries() -> List[Country]:
    """Get all countries (lightweight list).

    Returns:
        List[Country]: List of all countries with basic metadata.

    Example:
        >>> countries = get_countries()
        >>> len(countries) > 0
        True
    """
    data = DataLoader.load_countries()
    return [Country(**country) for country in data]


def get_country_by_id(country_id: int) -> Optional[Country]:
    """Get country by ID.

    Args:
        country_id: The country ID.

    Returns:
        Optional[Country]: The country if found, None otherwise.

    Example:
        >>> country = get_country_by_id(1)
        >>> country is not None
        True
    """
    countries = DataLoader.load_countries()
    for country_data in countries:
        if country_data.get("id") == country_id:
            return Country(**country_data)
    return None


def get_country_by_code(country_code: str) -> Optional[Country]:
    """Get country by ISO2 or ISO3 code.

    Args:
        country_code: ISO2 (e.g., "US") or ISO3 (e.g., "USA") country code.

    Returns:
        Optional[Country]: The country if found, None otherwise.

    Example:
        >>> usa = get_country_by_code("US")
        >>> usa.name
        'United States'
    """
    country_code_upper = country_code.upper()
    countries = DataLoader.load_countries()

    for country_data in countries:
        if (
            country_data.get("iso2") == country_code_upper
            or country_data.get("iso3") == country_code_upper
        ):
            return Country(**country_data)
    return None


def search_countries(query: str) -> List[Country]:
    """Search countries by name.

    Args:
        query: Search query (case-insensitive).

    Returns:
        List[Country]: List of countries matching the query.

    Example:
        >>> results = search_countries("united")
        >>> len(results) > 0
        True
    """
    query_lower = query.lower()
    countries = DataLoader.load_countries()
    results = []

    for country_data in countries:
        if query_lower in country_data.get("name", "").lower():
            results.append(Country(**country_data))

    return results


def get_countries_by_region(region: str) -> List[Country]:
    """Get countries in a region.

    Args:
        region: Region name (e.g., "Asia", "Europe").

    Returns:
        List[Country]: List of countries in the region.

    Example:
        >>> asian_countries = get_countries_by_region("Asia")
        >>> len(asian_countries) > 0
        True
    """
    countries = DataLoader.load_countries()
    results = []

    for country_data in countries:
        if country_data.get("region", "").lower() == region.lower():
            results.append(Country(**country_data))

    return results


def get_countries_by_subregion(subregion: str) -> List[Country]:
    """Get countries in a subregion.

    Args:
        subregion: Subregion name (e.g., "Southern Asia", "Western Europe").

    Returns:
        List[Country]: List of countries in the subregion.

    Example:
        >>> countries = get_countries_by_subregion("Southern Asia")
        >>> len(countries) > 0
        True
    """
    countries = DataLoader.load_countries()
    results = []

    for country_data in countries:
        if country_data.get("subregion", "").lower() == subregion.lower():
            results.append(Country(**country_data))

    return results


# States API


def get_states_of_country(country_code: str) -> List[State]:
    """Get all states in a country (lazy loaded).

    Args:
        country_code: ISO2 country code (e.g., "US").

    Returns:
        List[State]: List of states in the country.

    Example:
        >>> states = get_states_of_country("US")
        >>> len(states) > 0
        True
    """
    states_data = DataLoader.load_states(country_code.upper())
    return [State(**state) for state in states_data]


def get_state_by_code(country_code: str, state_code: str) -> Optional[State]:
    """Get specific state.

    Args:
        country_code: ISO2 country code (e.g., "US").
        state_code: State code (e.g., "CA").

    Returns:
        Optional[State]: The state if found, None otherwise.

    Example:
        >>> california = get_state_by_code("US", "CA")
        >>> california.name
        'California'
    """
    states = get_states_of_country(country_code)
    state_code_upper = state_code.upper()

    for state in states:
        if state.state_code.upper() == state_code_upper:
            return state

    return None


def search_states(country_code: str, query: str) -> List[State]:
    """Search states within a country.

    Args:
        country_code: ISO2 country code (e.g., "US").
        query: Search query (case-insensitive).

    Returns:
        List[State]: List of states matching the query.

    Example:
        >>> results = search_states("US", "cali")
        >>> len(results) > 0
        True
    """
    states = get_states_of_country(country_code)
    query_lower = query.lower()

    return [state for state in states if query_lower in state.name.lower()]


# Cities API


def get_cities_of_state(country_code: str, state_code: str) -> List[City]:
    """Get all cities in a state (lazy loaded).

    Args:
        country_code: ISO2 country code (e.g., "US").
        state_code: State code (e.g., "CA").

    Returns:
        List[City]: List of cities in the state.

    Example:
        >>> cities = get_cities_of_state("US", "CA")
        >>> len(cities) > 0
        True
    """
    cities_data = DataLoader.load_cities(country_code.upper(), state_code.upper())
    return [City(**city) for city in cities_data]


def get_cities_of_country(country_code: str) -> List[City]:
    """Get all cities in a country (warning: may be large).

    Args:
        country_code: ISO2 country code (e.g., "US").

    Returns:
        List[City]: List of all cities in the country.

    Example:
        >>> cities = get_cities_of_country("US")
        >>> len(cities) > 0
        True
    """
    states = get_states_of_country(country_code)
    all_cities = []

    for state in states:
        cities = get_cities_of_state(country_code, state.state_code)
        all_cities.extend(cities)

    return all_cities


def search_cities(
    country_code: str, state_code: Optional[str], query: str
) -> List[City]:
    """Search cities.

    Args:
        country_code: ISO2 country code (e.g., "US").
        state_code: Optional state code (e.g., "CA"). If None, searches all states.
        query: Search query (case-insensitive).

    Returns:
        List[City]: List of cities matching the query.

    Example:
        >>> results = search_cities("US", "CA", "los")
        >>> len(results) > 0
        True
    """
    query_lower = query.lower()

    if state_code:
        cities = get_cities_of_state(country_code, state_code)
    else:
        cities = get_cities_of_country(country_code)

    return [city for city in cities if query_lower in city.name.lower()]
