"""County coverage, source relationships and public lookup regressions."""

import json
import runpy
from pathlib import Path

import pytest
from pydantic import ValidationError

from countrystatecity_countries import (
    County,
    get_counties_of_country,
    get_counties_of_state,
    get_countries,
    get_county_by_id,
    get_states_of_country,
)
from countrystatecity_countries.loaders import DataLoader


def test_all_counties_and_state_relationships() -> None:
    """Every county has unique identity and real same-country state references."""
    ids = set()
    multi = []
    coverage = 0
    for country in get_countries():
        counties = get_counties_of_country(country.iso2)
        coverage += bool(counties)
        states = {
            state.id: state.state_code for state in get_states_of_country(country.iso2)
        }
        for county in counties:
            assert county.id not in ids
            ids.add(county.id)
            assert (county.country_id, county.country_code) == (
                country.id,
                country.iso2,
            )
            links = [(link.state_id, link.state_code) for link in county.states or []]
            if county.state_id is not None:
                links.append((county.state_id, county.state_code))
            for state_id, state_code in links:
                assert states[state_id] == state_code
            if len(county.states or []) > 1:
                multi.append(county)
                assert county.state_id is None and county.state_code is None
    counts = json.loads((DataLoader._data_dir / "release.json").read_text())["counts"]
    assert len(ids) == counts["counties"]
    assert coverage > 0
    assert multi


def test_multi_state_lookup_and_id() -> None:
    """Waitomo retains both memberships and appears once in each state's results."""
    county = get_county_by_id(14023)
    assert county is not None and county.name == "Waitomo District"
    assert county.state_id is None
    assert {link.state_code for link in county.states or []} == {"MWT", "WKO"}
    for state in ("MWT", "wko"):
        assert [row.id for row in get_counties_of_state("nz", state)].count(
            county.id
        ) == 1
    assert get_county_by_id(999999999) is None
    assert get_counties_of_country("EH") == []


@pytest.mark.parametrize("code", ["../US", "USA", "", "/x", 12, None])
def test_county_country_validation(code: str) -> None:
    """Reject invalid path components before opening a county file."""
    with pytest.raises(ValueError, match="ISO2"):
        get_counties_of_country(code)


@pytest.mark.parametrize("county_id", [0, -1, True, "1", None])
def test_county_id_validation(county_id: int) -> None:
    """Do not coerce invalid public lookup identifiers."""
    with pytest.raises(ValueError, match="positive integer"):
        get_county_by_id(county_id)


def test_county_state_validation() -> None:
    """State lookup rejects malformed codes without using them as paths."""
    with pytest.raises(ValueError, match="state code"):
        get_counties_of_state("NZ", "../WKO")


def test_county_model_preserves_nulls_and_rejects_bad_pairs() -> None:
    """A cross-state county cannot masquerade as a single-state county."""
    county = get_county_by_id(14023)
    assert county is not None and county.translations is None
    row = county.model_dump()
    assert County(**dict(row, translations=[])).translations == {}
    with pytest.raises(ValidationError, match="Duplicate county state"):
        County(**dict(row, states=[row["states"][0], row["states"][0]]))
    with pytest.raises(ValidationError, match="both be present or null"):
        County(**dict(row, state_id=4060))
    with pytest.raises(ValidationError, match="null primary"):
        County(**dict(row, state_id=4060, state_code="MWT"))


def test_county_generator_is_preflighted_and_removes_only_stale_counties(
    tmp_path: Path,
) -> None:
    """Invalid county inputs cannot overwrite existing generated files."""
    save = runpy.run_path(str(Path(__file__).parents[1] / "scripts/generate-data.py"))[
        "save_counties"
    ]
    country = {"id": 1, "iso2": "ZZ", "states": [{"id": 2, "iso2": "AA"}]}
    county = {
        "id": 3,
        "name": "County",
        "country_id": 1,
        "country_code": "ZZ",
        "state_id": 2,
        "state_code": "AA",
    }
    save([county], [country], tmp_path)
    generated = tmp_path / "by-country/ZZ/counties.json"
    before = generated.read_bytes()
    with pytest.raises(ValueError, match="state mismatch"):
        save([dict(county, state_id=9)], [country], tmp_path)
    assert generated.read_bytes() == before
    with pytest.raises(ValueError, match="Duplicate county"):
        save([county, county], [country], tmp_path)
    assert generated.read_bytes() == before
    sentinel = tmp_path / "by-country/ZZ/states.json"
    sentinel.write_text("[]")
    save([], [country], tmp_path)
    assert not generated.exists()
    assert sentinel.read_text() == "[]"
