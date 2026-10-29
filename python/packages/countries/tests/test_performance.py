"""Performance and caching tests."""

import time

from countrystatecity_countries import (
    get_cities_of_state,
    get_countries,
    get_states_of_country,
)
from countrystatecity_countries.loaders import DataLoader


def test_countries_load_time():
    """Test that countries load quickly."""
    start = time.time()
    countries = get_countries()
    elapsed = time.time() - start

    assert len(countries) > 0
    assert elapsed < 0.1  # Should load in less than 100ms


def test_caching_works():
    """The second country lookup reuses cached input without another disk read."""
    # Clear cache first
    DataLoader.clear_cache()

    # First load
    countries1 = get_countries()
    first = DataLoader.load_countries.cache_info()

    # Second load (should be cached)
    countries2 = get_countries()
    second = DataLoader.load_countries.cache_info()

    assert first.misses == 1
    assert second.misses == first.misses
    assert second.hits == first.hits + 1
    assert len(countries1) == len(countries2)


def test_lazy_loading_states():
    """Test that states are loaded lazily."""
    # Clear cache
    DataLoader.clear_cache()

    # Loading countries should not load states
    countries = get_countries()
    assert len(countries) > 0

    # Now load states
    states = get_states_of_country("US")
    assert len(states) > 0


def test_lazy_loading_cities():
    """Test that cities are loaded lazily."""
    # Clear cache
    DataLoader.clear_cache()

    # Loading countries and states should not load cities
    countries = get_countries()
    states = get_states_of_country("US")
    assert len(countries) > 0
    assert len(states) > 0

    # Now load cities
    cities = get_cities_of_state("US", "CA")
    assert len(cities) > 0


def test_cache_independence():
    """Test that different data is cached independently."""
    DataLoader.clear_cache()

    # Load data for different countries/states
    us_states = get_states_of_country("US")
    ca_cities = get_cities_of_state("US", "CA")

    assert len(us_states) > 0
    assert len(ca_cities) > 0
