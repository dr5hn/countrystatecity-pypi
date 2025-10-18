"""Tests for country API functions."""

import pytest

from countrystatecity_countries import (
    get_countries,
    get_countries_by_region,
    get_countries_by_subregion,
    get_country_by_code,
    get_country_by_id,
    search_countries,
)
from countrystatecity_countries.models import Country


def test_get_countries():
    """Test getting all countries."""
    countries = get_countries()
    assert isinstance(countries, list)
    assert len(countries) > 0
    assert all(isinstance(c, Country) for c in countries)


def test_get_countries_has_us():
    """Test that US is in the countries list."""
    countries = get_countries()
    us_codes = [c.iso2 for c in countries]
    assert "US" in us_codes


def test_get_country_by_id():
    """Test getting country by ID."""
    country = get_country_by_id(1)
    assert country is not None
    assert isinstance(country, Country)
    assert country.id == 1


def test_get_country_by_id_not_found():
    """Test getting country by non-existent ID."""
    country = get_country_by_id(99999)
    assert country is None


def test_get_country_by_code_iso2():
    """Test getting country by ISO2 code."""
    usa = get_country_by_code("US")
    assert usa is not None
    assert usa.iso2 == "US"
    assert usa.name == "United States"


def test_get_country_by_code_iso3():
    """Test getting country by ISO3 code."""
    usa = get_country_by_code("USA")
    assert usa is not None
    assert usa.iso3 == "USA"
    assert usa.name == "United States"


def test_get_country_by_code_lowercase():
    """Test getting country by lowercase code."""
    usa = get_country_by_code("us")
    assert usa is not None
    assert usa.iso2 == "US"


def test_get_country_by_code_not_found():
    """Test getting country by non-existent code."""
    country = get_country_by_code("ZZ")
    assert country is None


def test_search_countries():
    """Test searching countries by name."""
    results = search_countries("united")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(c, Country) for c in results)
    assert any("United" in c.name for c in results)


def test_search_countries_case_insensitive():
    """Test that country search is case-insensitive."""
    results_lower = search_countries("united")
    results_upper = search_countries("UNITED")
    assert len(results_lower) == len(results_upper)


def test_search_countries_no_results():
    """Test searching countries with no results."""
    results = search_countries("xyzxyzxyz")
    assert results == []


def test_get_countries_by_region():
    """Test getting countries by region."""
    american_countries = get_countries_by_region("Americas")
    assert isinstance(american_countries, list)
    assert len(american_countries) > 0
    assert all(c.region == "Americas" for c in american_countries)


def test_get_countries_by_region_case_insensitive():
    """Test that region search is case-insensitive."""
    results_lower = get_countries_by_region("americas")
    results_upper = get_countries_by_region("AMERICAS")
    assert len(results_lower) == len(results_upper)


def test_get_countries_by_subregion():
    """Test getting countries by subregion."""
    countries = get_countries_by_subregion("Northern America")
    assert isinstance(countries, list)
    assert len(countries) > 0
    assert all(c.subregion == "Northern America" for c in countries)


def test_country_model_immutable():
    """Test that Country model is immutable."""
    country = get_country_by_code("US")
    assert country is not None

    with pytest.raises(Exception):  # Pydantic raises ValidationError or similar
        country.name = "Changed"


def test_country_has_required_fields():
    """Test that countries have all required fields."""
    usa = get_country_by_code("US")
    assert usa is not None
    assert usa.id is not None
    assert usa.name is not None
    assert usa.iso2 is not None
    assert usa.iso3 is not None
    assert usa.numeric_code is not None
    assert usa.phone_code is not None


def test_country_has_optional_fields():
    """Test that countries can have optional fields."""
    usa = get_country_by_code("US")
    assert usa is not None
    assert usa.capital is not None
    assert usa.currency is not None
    assert usa.region is not None


def test_country_translations():
    """Test that country has translations."""
    usa = get_country_by_code("US")
    assert usa is not None
    assert isinstance(usa.translations, dict)
    assert len(usa.translations) > 0


def test_country_timezones():
    """Test that country has timezones."""
    usa = get_country_by_code("US")
    assert usa is not None
    assert isinstance(usa.timezones, list)
    assert len(usa.timezones) > 0
