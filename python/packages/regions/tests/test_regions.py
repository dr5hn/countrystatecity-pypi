"""Tests for regions API functions."""

import pytest

from countrystatecity_regions import (
    get_all_region_names,
    get_all_regions,
    get_all_subregion_names,
    get_countries_by_region,
    get_countries_by_subregion,
    get_region_by_country,
    search_regions,
)
from countrystatecity_regions.models import CountryRegion


def test_get_all_regions():
    regions = get_all_regions()
    assert isinstance(regions, list)
    assert len(regions) > 0
    assert all(isinstance(r, CountryRegion) for r in regions)


def test_get_all_regions_count():
    regions = get_all_regions()
    assert len(regions) > 200


def test_get_region_by_country_us():
    r = get_region_by_country("US")
    assert r is not None
    assert isinstance(r, CountryRegion)
    assert r.region == "Americas"
    assert r.subregion == "Northern America"


def test_get_region_by_country_india():
    r = get_region_by_country("IN")
    assert r is not None
    assert r.region == "Asia"
    assert r.subregion == "Southern Asia"
    assert r.countryName == "India"


def test_get_region_by_country_lowercase():
    upper = get_region_by_country("US")
    lower = get_region_by_country("us")
    assert upper is not None
    assert lower is not None
    assert upper.region == lower.region


def test_get_region_by_country_not_found():
    r = get_region_by_country("ZZ")
    assert r is None


def test_get_countries_by_region_asia():
    entries = get_countries_by_region("Asia")
    assert isinstance(entries, list)
    assert len(entries) > 1
    assert all(e.region == "Asia" for e in entries)


def test_get_countries_by_region_lowercase():
    upper = get_countries_by_region("Asia")
    lower = get_countries_by_region("asia")
    assert len(upper) == len(lower)


def test_get_countries_by_region_not_found():
    entries = get_countries_by_region("Narnia")
    assert entries == []


def test_get_countries_by_subregion_southern_asia():
    entries = get_countries_by_subregion("Southern Asia")
    assert isinstance(entries, list)
    assert len(entries) > 1
    assert all(e.subregion == "Southern Asia" for e in entries)
    country_codes = [e.countryCode for e in entries]
    assert "IN" in country_codes


def test_get_countries_by_subregion_not_found():
    entries = get_countries_by_subregion("Nowhere")
    assert entries == []


def test_region_model_fields():
    r = get_region_by_country("US")
    assert r is not None
    assert isinstance(r.countryCode, str)
    assert isinstance(r.countryName, str)
    assert isinstance(r.region, str)
    assert isinstance(r.subregion, str)


def test_region_model_immutable():
    r = get_region_by_country("US")
    assert r is not None
    with pytest.raises(Exception):
        r.region = "Nowhere"  # type: ignore[misc]


def test_get_all_region_names():
    names = get_all_region_names()
    assert isinstance(names, list)
    assert names == sorted(names)
    assert "Asia" in names
    assert "Europe" in names
    assert "Americas" in names


def test_get_all_subregion_names():
    names = get_all_subregion_names()
    assert isinstance(names, list)
    assert names == sorted(names)
    assert "Southern Asia" in names


def test_get_all_subregion_names_filtered_by_region():
    names = get_all_subregion_names("Asia")
    assert "Southern Asia" in names
    assert "Western Europe" not in names


def test_search_regions_by_region_name():
    results = search_regions("asia")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(r, CountryRegion) for r in results)


def test_search_regions_by_country_name():
    results = search_regions("United States")
    assert isinstance(results, list)
    country_codes = [r.countryCode for r in results]
    assert "US" in country_codes


def test_search_regions_by_country_code():
    results = search_regions("IN")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_regions_by_subregion():
    results = search_regions("southern asia")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(r.subregion == "Southern Asia" for r in results)


def test_search_regions_case_insensitive():
    lower = search_regions("asia")
    upper = search_regions("ASIA")
    assert len(lower) == len(upper)


def test_search_regions_no_results():
    results = search_regions("xyzxyzxyz_invalid")
    assert results == []


def test_europe_has_multiple_countries():
    entries = get_countries_by_region("Europe")
    country_codes = [e.countryCode for e in entries]
    assert "DE" in country_codes
    assert "FR" in country_codes
