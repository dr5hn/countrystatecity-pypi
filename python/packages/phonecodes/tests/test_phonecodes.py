"""Tests for phonecodes API functions."""

import pytest

from countrystatecity_phonecodes import (
    get_all_phonecodes,
    get_countries_by_phonecode,
    get_phonecode_by_country,
    search_phonecodes,
)
from countrystatecity_phonecodes.models import PhoneCode


def test_get_all_phonecodes():
    phonecodes = get_all_phonecodes()
    assert isinstance(phonecodes, list)
    assert len(phonecodes) > 0
    assert all(isinstance(p, PhoneCode) for p in phonecodes)


def test_get_all_phonecodes_count():
    phonecodes = get_all_phonecodes()
    assert len(phonecodes) > 200


def test_get_phonecode_by_country_us():
    p = get_phonecode_by_country("US")
    assert p is not None
    assert isinstance(p, PhoneCode)
    assert p.phoneCode == "1"
    assert p.countryCode == "US"


def test_get_phonecode_by_country_india():
    p = get_phonecode_by_country("IN")
    assert p is not None
    assert p.phoneCode == "91"
    assert p.countryName == "India"


def test_get_phonecode_by_country_uk():
    p = get_phonecode_by_country("GB")
    assert p is not None
    assert p.phoneCode == "44"


def test_get_phonecode_by_country_lowercase():
    upper = get_phonecode_by_country("US")
    lower = get_phonecode_by_country("us")
    assert upper is not None
    assert lower is not None
    assert upper.phoneCode == lower.phoneCode


def test_get_phonecode_by_country_not_found():
    p = get_phonecode_by_country("ZZ")
    assert p is None


def test_get_countries_by_phonecode_1():
    entries = get_countries_by_phonecode("1")
    assert isinstance(entries, list)
    assert len(entries) > 1
    assert all(e.phoneCode == "1" for e in entries)
    country_codes = [e.countryCode for e in entries]
    assert "US" in country_codes
    assert "CA" in country_codes


def test_get_countries_by_phonecode_with_plus():
    without = get_countries_by_phonecode("44")
    with_plus = get_countries_by_phonecode("+44")
    assert len(without) == len(with_plus)


def test_get_countries_by_phonecode_unique():
    entries = get_countries_by_phonecode("91")
    assert len(entries) == 1
    assert entries[0].countryCode == "IN"


def test_get_countries_by_phonecode_not_found():
    entries = get_countries_by_phonecode("9999")
    assert entries == []


def test_phonecode_model_fields():
    p = get_phonecode_by_country("US")
    assert p is not None
    assert isinstance(p.phoneCode, str)
    assert isinstance(p.countryCode, str)
    assert isinstance(p.countryName, str)


def test_phonecode_model_immutable():
    p = get_phonecode_by_country("US")
    assert p is not None
    with pytest.raises(Exception):
        p.phoneCode = "999"  # type: ignore[misc]


def test_search_phonecodes_by_country_name():
    results = search_phonecodes("united")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(p, PhoneCode) for p in results)


def test_search_phonecodes_by_phone_code():
    results = search_phonecodes("44")
    assert isinstance(results, list)
    assert len(results) > 0
    assert any(p.phoneCode == "44" for p in results)


def test_search_phonecodes_by_country_code():
    results = search_phonecodes("US")
    assert isinstance(results, list)
    assert len(results) > 0
    assert any(p.countryCode == "US" for p in results)


def test_search_phonecodes_case_insensitive():
    lower = search_phonecodes("india")
    upper = search_phonecodes("INDIA")
    assert len(lower) == len(upper)


def test_search_phonecodes_with_plus():
    with_plus = search_phonecodes("+44")
    without_plus = search_phonecodes("44")
    assert len(with_plus) == len(without_plus)


def test_search_phonecodes_no_results():
    results = search_phonecodes("xyzxyzxyz_invalid")
    assert results == []


def test_all_entries_have_required_fields():
    phonecodes = get_all_phonecodes()
    for p in phonecodes:
        assert p.phoneCode
        assert p.countryCode
        assert p.countryName


def test_phone_codes_are_numeric_strings():
    phonecodes = get_all_phonecodes()
    for p in phonecodes:
        assert (
            p.phoneCode.isdigit()
        ), f"{p.countryCode} has non-numeric code: {p.phoneCode}"
