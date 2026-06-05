"""Tests for timezone API functions."""

from datetime import datetime

import pytest

from countrystatecity_timezones import (
    convert_time,
    get_all_timezones,
    get_timezone_by_zone_name,
    get_timezones_by_country,
    get_timezones_by_offset,
    search_timezones,
)
from countrystatecity_timezones.models import Timezone


def test_get_all_timezones():
    """Test getting all timezones."""
    timezones = get_all_timezones()
    assert isinstance(timezones, list)
    assert len(timezones) > 0
    assert all(isinstance(tz, Timezone) for tz in timezones)


def test_get_all_timezones_count():
    """Test that we have a reasonable number of timezone entries."""
    timezones = get_all_timezones()
    assert len(timezones) > 400


def test_get_timezones_by_country_us():
    """Test getting US timezones."""
    timezones = get_timezones_by_country("US")
    assert isinstance(timezones, list)
    assert len(timezones) > 0
    assert all(tz.countryCode == "US" for tz in timezones)


def test_get_timezones_by_country_lowercase():
    """Test that country code lookup is case-insensitive."""
    upper = get_timezones_by_country("US")
    lower = get_timezones_by_country("us")
    assert len(upper) == len(lower)


def test_get_timezones_by_country_not_found():
    """Test getting timezones for non-existent country."""
    timezones = get_timezones_by_country("ZZ")
    assert timezones == []


def test_get_timezone_by_zone_name():
    """Test getting timezone by IANA zone name."""
    tz = get_timezone_by_zone_name("America/New_York")
    assert tz is not None
    assert isinstance(tz, Timezone)
    assert tz.zoneName == "America/New_York"
    assert tz.countryCode == "US"


def test_get_timezone_by_zone_name_not_found():
    """Test getting non-existent timezone."""
    tz = get_timezone_by_zone_name("Invalid/Zone")
    assert tz is None


def test_timezone_model_fields():
    """Test that timezone model has all expected fields."""
    tz = get_timezone_by_zone_name("America/New_York")
    assert tz is not None
    assert tz.zoneName == "America/New_York"
    assert isinstance(tz.gmtOffset, int)
    assert isinstance(tz.gmtOffsetName, str)
    assert isinstance(tz.abbreviation, str)
    assert isinstance(tz.tzName, str)
    assert isinstance(tz.countryCode, str)
    assert isinstance(tz.countryName, str)


def test_timezone_model_immutable():
    """Test that Timezone model is immutable."""
    tz = get_timezone_by_zone_name("America/New_York")
    assert tz is not None
    with pytest.raises(Exception):
        tz.zoneName = "Changed"  # type: ignore[misc]


def test_get_timezones_by_offset():
    """Test getting timezones by GMT offset."""
    # UTC-05:00 = -18000 seconds
    timezones = get_timezones_by_offset(-18000)
    assert isinstance(timezones, list)
    assert len(timezones) > 0
    assert all(tz.gmtOffset == -18000 for tz in timezones)


def test_get_timezones_by_offset_utc():
    """Test getting UTC timezones."""
    timezones = get_timezones_by_offset(0)
    assert isinstance(timezones, list)
    assert len(timezones) > 0


def test_get_timezones_by_offset_not_found():
    """Test getting timezones with non-existent offset."""
    timezones = get_timezones_by_offset(99999999)
    assert timezones == []


def test_search_timezones_by_zone_name():
    """Test searching timezones by zone name."""
    results = search_timezones("America")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(tz, Timezone) for tz in results)


def test_search_timezones_by_tz_name():
    """Test searching timezones by timezone full name."""
    results = search_timezones("Eastern")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_timezones_by_abbreviation():
    """Test searching timezones by abbreviation."""
    results = search_timezones("EST")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_timezones_case_insensitive():
    """Test that timezone search is case-insensitive."""
    lower = search_timezones("eastern")
    upper = search_timezones("EASTERN")
    assert len(lower) == len(upper)


def test_search_timezones_no_results():
    """Test searching timezones with no results."""
    results = search_timezones("xyzxyzxyz_invalid")
    assert results == []


def test_convert_time_basic():
    """Test basic time conversion."""
    dt = datetime(2024, 1, 1, 12, 0, 0)
    result = convert_time(dt, "America/New_York", "UTC")
    assert result.hour == 17


def test_convert_time_ny_to_kolkata():
    """Test New York to Kolkata conversion (UTC-5 to UTC+5:30 = +10:30 hours)."""
    dt = datetime(2024, 1, 1, 0, 0, 0)
    result = convert_time(dt, "America/New_York", "Asia/Kolkata")
    assert result.hour == 10
    assert result.minute == 30


def test_convert_time_aware_datetime():
    """Test converting an already timezone-aware datetime."""
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        from backports.zoneinfo import ZoneInfo  # type: ignore[no-reuse]

    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
    result = convert_time(dt, "UTC", "America/New_York")
    assert result.hour == 7


def test_us_has_multiple_timezones():
    """Test that US has multiple timezones."""
    timezones = get_timezones_by_country("US")
    assert len(timezones) > 5


def test_timezone_country_name_present():
    """Test that timezone entries include country name."""
    tz = get_timezone_by_zone_name("America/New_York")
    assert tz is not None
    assert tz.countryName == "United States"
