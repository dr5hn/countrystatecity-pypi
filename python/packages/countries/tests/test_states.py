"""Tests for state API functions."""

import pytest

from countrystatecity_countries import (
    get_state_by_code,
    get_states_of_country,
    search_states,
)
from countrystatecity_countries.models import State


def test_get_states_of_country():
    """Test getting states of a country."""
    states = get_states_of_country("US")
    assert isinstance(states, list)
    assert len(states) > 0
    assert all(isinstance(s, State) for s in states)


def test_get_states_of_country_lowercase():
    """Test getting states with lowercase country code."""
    states = get_states_of_country("us")
    assert isinstance(states, list)
    assert len(states) > 0


def test_get_states_of_country_invalid():
    """Test getting states of invalid country."""
    states = get_states_of_country("ZZ")
    assert states == []


def test_get_state_by_code():
    """Test getting state by code."""
    california = get_state_by_code("US", "CA")
    assert california is not None
    assert isinstance(california, State)
    assert california.state_code == "CA"
    assert california.name == "California"


def test_get_state_by_code_lowercase():
    """Test getting state with lowercase codes."""
    california = get_state_by_code("us", "ca")
    assert california is not None
    assert california.state_code == "CA"


def test_get_state_by_code_not_found():
    """Test getting state by non-existent code."""
    state = get_state_by_code("US", "ZZ")
    assert state is None


def test_search_states():
    """Test searching states."""
    results = search_states("US", "cali")
    assert isinstance(results, list)
    assert len(results) > 0
    assert any("California" in s.name for s in results)


def test_search_states_case_insensitive():
    """Test that state search is case-insensitive."""
    results_lower = search_states("US", "california")
    results_upper = search_states("US", "CALIFORNIA")
    assert len(results_lower) == len(results_upper)


def test_search_states_no_results():
    """Test searching states with no results."""
    results = search_states("US", "xyzxyzxyz")
    assert results == []


def test_state_model_immutable():
    """Test that State model is immutable."""
    state = get_state_by_code("US", "CA")
    assert state is not None

    with pytest.raises(Exception):  # Pydantic raises ValidationError or similar
        state.name = "Changed"


def test_state_has_required_fields():
    """Test that states have all required fields."""
    california = get_state_by_code("US", "CA")
    assert california is not None
    assert california.id is not None
    assert california.name is not None
    assert california.country_id is not None
    assert california.country_code is not None
    assert california.state_code is not None


def test_state_belongs_to_country():
    """Test that state belongs to the correct country."""
    california = get_state_by_code("US", "CA")
    assert california is not None
    assert california.country_code == "US"
    assert california.country_id == 1


def test_all_states_have_same_country():
    """Test that all states from a country have the same country code."""
    states = get_states_of_country("US")
    assert all(s.country_code == "US" for s in states)
