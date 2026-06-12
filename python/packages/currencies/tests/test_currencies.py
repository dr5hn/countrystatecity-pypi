"""Tests for currency API functions."""

import pytest

from countrystatecity_currencies import (
    get_all_currencies,
    get_countries_by_currency,
    get_currency_by_country,
    search_currencies,
)
from countrystatecity_currencies.models import Currency


def test_get_all_currencies():
    currencies = get_all_currencies()
    assert isinstance(currencies, list)
    assert len(currencies) > 0
    assert all(isinstance(c, Currency) for c in currencies)


def test_get_all_currencies_count():
    currencies = get_all_currencies()
    assert len(currencies) > 200


def test_get_currency_by_country_us():
    c = get_currency_by_country("US")
    assert c is not None
    assert isinstance(c, Currency)
    assert c.code == "USD"
    assert c.countryCode == "US"


def test_get_currency_by_country_india():
    c = get_currency_by_country("IN")
    assert c is not None
    assert c.code == "INR"
    assert c.symbol == "₹"
    assert c.countryName == "India"


def test_get_currency_by_country_lowercase():
    upper = get_currency_by_country("US")
    lower = get_currency_by_country("us")
    assert upper is not None
    assert lower is not None
    assert upper.code == lower.code


def test_get_currency_by_country_not_found():
    c = get_currency_by_country("ZZ")
    assert c is None


def test_get_countries_by_currency_eur():
    entries = get_countries_by_currency("EUR")
    assert isinstance(entries, list)
    assert len(entries) > 1
    assert all(e.code == "EUR" for e in entries)


def test_get_countries_by_currency_usd():
    entries = get_countries_by_currency("USD")
    assert isinstance(entries, list)
    assert len(entries) > 0


def test_get_countries_by_currency_lowercase():
    upper = get_countries_by_currency("EUR")
    lower = get_countries_by_currency("eur")
    assert len(upper) == len(lower)


def test_get_countries_by_currency_not_found():
    entries = get_countries_by_currency("ZZZ")
    assert entries == []


def test_currency_model_fields():
    c = get_currency_by_country("US")
    assert c is not None
    assert isinstance(c.code, str)
    assert isinstance(c.name, str)
    assert isinstance(c.symbol, str)
    assert isinstance(c.countryCode, str)
    assert isinstance(c.countryName, str)


def test_currency_model_immutable():
    c = get_currency_by_country("US")
    assert c is not None
    with pytest.raises(Exception):
        c.code = "XXX"  # type: ignore[misc]


def test_search_currencies_by_name():
    results = search_currencies("dollar")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(c, Currency) for c in results)


def test_search_currencies_by_code():
    results = search_currencies("USD")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_currencies_by_symbol():
    results = search_currencies("€")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(c.symbol == "€" for c in results)


def test_search_currencies_case_insensitive():
    lower = search_currencies("dollar")
    upper = search_currencies("DOLLAR")
    assert len(lower) == len(upper)


def test_search_currencies_by_country_name():
    results = search_currencies("United States")
    assert isinstance(results, list)
    assert len(results) > 0
    country_codes = [c.countryCode for c in results]
    assert "US" in country_codes


def test_search_currencies_by_country_code():
    results = search_currencies("IN")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_currencies_no_results():
    results = search_currencies("xyzxyzxyz_invalid")
    assert results == []


def test_eur_used_by_multiple_countries():
    entries = get_countries_by_currency("EUR")
    country_codes = [e.countryCode for e in entries]
    assert "DE" in country_codes
    assert "FR" in country_codes


def test_currency_name_present():
    c = get_currency_by_country("US")
    assert c is not None
    assert c.name == "United States dollar"
