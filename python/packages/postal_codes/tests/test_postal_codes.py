"""Tests for postal codes API functions."""

import pytest

from countrystatecity_postal_codes import (
    get_countries_with_postal_data,
    get_postal_info_by_country,
    get_postcode_by_code,
    get_postcodes_by_code,
    get_postcodes_of_country,
    search_postcodes,
    validate_postcode,
)
from countrystatecity_postal_codes.loaders import DataLoader
from countrystatecity_postal_codes.models import CountryPostalInfo, Postcode


def test_get_countries_with_postal_data():
    countries = get_countries_with_postal_data()
    assert isinstance(countries, list)
    assert len(countries) > 0
    assert all(isinstance(c, CountryPostalInfo) for c in countries)


def test_get_countries_with_postal_data_count():
    countries = get_countries_with_postal_data()
    assert len(countries) > 200


def test_get_postal_info_by_country_us():
    info = get_postal_info_by_country("US")
    assert info is not None
    assert isinstance(info, CountryPostalInfo)
    assert info.countryCode == "US"
    assert info.postalCodeRegex is not None


def test_get_postal_info_by_country_lowercase():
    upper = get_postal_info_by_country("US")
    lower = get_postal_info_by_country("us")
    assert upper is not None
    assert lower is not None
    assert upper.countryCode == lower.countryCode


def test_get_postal_info_by_country_not_found():
    info = get_postal_info_by_country("ZZ")
    assert info is None


def test_country_postal_info_model_immutable():
    info = get_postal_info_by_country("US")
    assert info is not None
    with pytest.raises(Exception):
        info.postalCodeFormat = "XXXXX"  # type: ignore[misc]


def test_get_postcodes_of_country_andorra():
    postcodes = get_postcodes_of_country("AD")
    assert isinstance(postcodes, list)
    assert len(postcodes) > 0
    assert all(isinstance(p, Postcode) for p in postcodes)
    assert all(p.countryCode == "AD" for p in postcodes)


def test_get_postcodes_of_country_lowercase():
    upper = get_postcodes_of_country("AD")
    lower = get_postcodes_of_country("ad")
    assert len(upper) == len(lower)


def test_get_postcodes_of_country_unknown():
    postcodes = get_postcodes_of_country("ZZ")
    assert postcodes == []


def test_get_postcode_by_code_andorra():
    pc = get_postcode_by_code("AD", "AD100")
    assert pc is not None
    assert isinstance(pc, Postcode)
    assert pc.code == "AD100"
    assert pc.countryCode == "AD"
    assert pc.localityName == "Canillo"


def test_get_postcode_by_code_not_found():
    pc = get_postcode_by_code("AD", "NOTREAL")
    assert pc is None


def test_get_postcodes_by_code_returns_every_locality():
    """Return all localities when a postcode is not unique."""
    matches = get_postcodes_by_code("BB", "BB18000")
    assert {match.localityName for match in matches} == {"Crane", "Six Cross Roads"}


def test_get_postcode_by_code_returns_first_match_for_compatibility():
    """Keep the singular lookup deterministic for existing callers."""
    first = get_postcode_by_code("BB", "BB18000")
    matches = get_postcodes_by_code("BB", "BB18000")
    assert first == matches[0]


def test_postcode_model_immutable():
    pc = get_postcode_by_code("AD", "AD100")
    assert pc is not None
    with pytest.raises(Exception):
        pc.code = "XXXXX"  # type: ignore[misc]


def test_search_postcodes_by_code():
    results = search_postcodes("AD", "AD1")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all("ad1" in p.code.lower() for p in results)


def test_search_postcodes_by_locality():
    results = search_postcodes("AD", "canillo")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(p.localityName is not None for p in results)


def test_search_postcodes_case_insensitive():
    lower = search_postcodes("AD", "canillo")
    upper = search_postcodes("AD", "CANILLO")
    assert len(lower) == len(upper)


def test_search_postcodes_no_results():
    results = search_postcodes("AD", "xyzxyzxyz_invalid")
    assert results == []


def test_validate_postcode_us_valid():
    assert validate_postcode("US", "10001") is True


def test_validate_postcode_us_invalid():
    assert validate_postcode("US", "not-a-zip") is False


def test_validate_postcode_unknown_country():
    assert validate_postcode("ZZ", "10001") is False


@pytest.mark.parametrize(
    ("country_code", "postcode"),
    [
        ("AS", "96799junk"),
        ("GI", "GX11 1AAjunk"),
        ("IE", "D02 X285junk"),
        ("WS", "AS 96799junk"),
    ],
)
def test_validate_postcode_rejects_trailing_garbage(
    country_code: str, postcode: str
) -> None:
    """Require the country's regex to match the complete input."""
    assert validate_postcode(country_code, postcode) is False


def test_country_code_cannot_traverse_data_directories():
    """Reject path-shaped country codes before filesystem access."""
    assert get_postcodes_of_country("AD/../AI") == []


def test_postcode_cache_is_bounded():
    """Do not retain the complete global postcode dataset in memory."""
    DataLoader.clear_cache()
    for country_code in ("AD", "AI", "AS", "BB", "BL", "BM", "CC", "CX", "FK"):
        DataLoader.load_postcodes(country_code)
    assert DataLoader.load_postcodes.cache_info().currsize == 8
