"""Tests for city API functions."""

import pytest

from countrystatecity_countries import (
    get_cities_of_country,
    get_cities_of_state,
    search_cities,
)
from countrystatecity_countries.models import City


def test_get_cities_of_state():
    """Test getting cities of a state."""
    cities = get_cities_of_state("US", "CA")
    assert isinstance(cities, list)
    assert len(cities) > 0
    assert all(isinstance(c, City) for c in cities)


def test_get_cities_of_state_lowercase():
    """Test getting cities with lowercase codes."""
    cities = get_cities_of_state("us", "ca")
    assert isinstance(cities, list)
    assert len(cities) > 0


def test_get_cities_of_state_invalid():
    """Test getting cities of invalid state."""
    cities = get_cities_of_state("US", "ZZ")
    assert cities == []


def test_get_cities_of_country():
    """Test getting all cities of a country."""
    cities = get_cities_of_country("US")
    assert isinstance(cities, list)
    assert len(cities) > 0
    assert all(isinstance(c, City) for c in cities)


def test_search_cities_with_state():
    """Test searching cities within a state."""
    results = search_cities("US", "CA", "los")
    assert isinstance(results, list)
    assert len(results) > 0
    assert any("Los Angeles" in c.name for c in results)


def test_search_cities_without_state():
    """Test searching cities within entire country."""
    results = search_cities("US", None, "san")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_cities_case_insensitive():
    """Test that city search is case-insensitive."""
    results_lower = search_cities("US", "CA", "los angeles")
    results_upper = search_cities("US", "CA", "LOS ANGELES")
    assert len(results_lower) == len(results_upper)


def test_search_cities_no_results():
    """Test searching cities with no results."""
    results = search_cities("US", "CA", "xyzxyzxyz")
    assert results == []


def test_city_model_immutable():
    """Test that City model is immutable."""
    cities = get_cities_of_state("US", "CA")
    assert len(cities) > 0
    city = cities[0]

    with pytest.raises(Exception):  # Pydantic raises ValidationError or similar
        city.name = "Changed"


def test_city_has_required_fields():
    """Test that cities have all required fields."""
    cities = get_cities_of_state("US", "CA")
    assert len(cities) > 0
    city = cities[0]

    assert city.id is not None
    assert city.name is not None
    assert city.state_id is not None
    assert city.state_code is not None
    assert city.country_id is not None
    assert city.country_code is not None
    assert city.latitude is not None
    assert city.longitude is not None


def test_city_belongs_to_state():
    """Test that city belongs to the correct state."""
    cities = get_cities_of_state("US", "CA")
    assert len(cities) > 0
    assert all(c.state_code == "CA" for c in cities)
    assert all(c.country_code == "US" for c in cities)


def test_city_coordinates():
    """Test that cities have valid coordinates."""
    cities = get_cities_of_state("US", "CA")
    assert len(cities) > 0

    for city in cities:
        assert city.latitude is not None
        assert city.longitude is not None
