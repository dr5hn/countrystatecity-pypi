"""Validate the entire shipped snapshot through the public models and API."""

import json

from countrystatecity_countries import (
    get_cities_of_state,
    get_countries,
    get_states_of_country,
)
from countrystatecity_countries.loaders import DataLoader, _safe_dirname
from countrystatecity_countries.models import City


def test_snapshot_has_unique_ids_and_no_obsolete_files() -> None:
    """Every row must load once, belong to its parent and have a reachable file."""
    country_ids = set()
    state_ids = set()
    city_ids = set()
    expected_files = {
        DataLoader._data_dir / "countries.json",
        DataLoader._data_dir / "release.json",
    }
    for country in get_countries():
        assert country.id not in country_ids
        country_ids.add(country.id)
        country_dir = DataLoader._data_dir / "by-country" / country.iso2
        states = get_states_of_country(country.iso2)
        country_cities = [
            City(**row) for row in DataLoader.load_country_cities(country.iso2)
        ]
        if states or country_cities:
            expected_files.add(country_dir / "states.json")
        if country_cities:
            expected_files.add(country_dir / "cities.json")
        for city in country_cities:
            assert city.id not in city_ids
            city_ids.add(city.id)
            assert (city.country_id, city.country_code) == (country.id, country.iso2)
            assert city.state_id is None and city.state_code is None
        state_codes = set()
        for state in states:
            assert state.id not in state_ids
            assert state.state_code.upper() not in state_codes
            state_ids.add(state.id)
            state_codes.add(state.state_code.upper())
            assert (state.country_id, state.country_code) == (country.id, country.iso2)
            cities = get_cities_of_state(country.iso2, state.state_code)
            if cities:
                expected_files.add(
                    country_dir
                    / "states"
                    / _safe_dirname(state.state_code)
                    / "cities.json"
                )
            for city in cities:
                assert city.id not in city_ids
                city_ids.add(city.id)
                assert (city.country_id, city.country_code) == (
                    country.id,
                    country.iso2,
                )
                assert (city.state_id, city.state_code) == (state.id, state.state_code)
                assert -90 <= float(city.latitude) <= 90
                assert -180 <= float(city.longitude) <= 180
                assert city.county_id is None or city.county_id > 0
    assert set(DataLoader._data_dir.rglob("*.json")) == expected_files
    counts = json.loads((DataLoader._data_dir / "release.json").read_text())["counts"]
    assert len(country_ids) == counts["countries"]
    assert len(city_ids) == counts["cities"]
