"""Official countries, states, and cities database with type hints and lazy loading.

This package provides access to a comprehensive database of countries, states/provinces,
and cities with full metadata including timezones, currencies, translations, and more.

Example:
    >>> from countrystatecity_countries import get_countries, get_country_by_code
    >>> countries = get_countries()
    >>> usa = get_country_by_code("US")
    >>> print(usa.name)
    'United States'
"""

__version__ = "1.0.0"

from .api import (  # Countries API; States API; Cities API
    get_cities_of_country,
    get_cities_of_state,
    get_countries,
    get_countries_by_region,
    get_countries_by_subregion,
    get_country_by_code,
    get_country_by_id,
    get_state_by_code,
    get_states_of_country,
    search_cities,
    search_countries,
    search_states,
)
from .models import City, Country, State

__all__ = [
    # Version
    "__version__",
    # Models
    "Country",
    "State",
    "City",
    # Countries API
    "get_countries",
    "get_country_by_id",
    "get_country_by_code",
    "search_countries",
    "get_countries_by_region",
    "get_countries_by_subregion",
    # States API
    "get_states_of_country",
    "get_state_by_code",
    "search_states",
    # Cities API
    "get_cities_of_state",
    "get_cities_of_country",
    "search_cities",
]
