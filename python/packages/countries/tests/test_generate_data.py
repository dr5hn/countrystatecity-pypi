"""Regression tests for replacing an upstream data snapshot."""

import json
import runpy
from pathlib import Path

import pytest

from countrystatecity_countries.models import City


def test_generate_replaces_retired_and_empty_state_data(tmp_path: Path) -> None:
    """Remove old city locations and preserve the new county link on a second run."""
    script = Path(__file__).parents[1] / "scripts" / "generate-data.py"
    save = runpy.run_path(str(script))["save_states_and_cities"]
    city = {"id": 1, "name": "Test", "latitude": "0", "longitude": "0"}
    old = [
        {
            "id": 1,
            "iso2": "ZZ",
            "states": [
                {"id": 1, "iso2": "OLD", "cities": [city]},
                {"id": 2, "iso2": "EMPTY", "cities": [dict(city, id=2)]},
            ],
        },
        {"id": 2, "iso2": "YY", "states": [{"id": 3, "iso2": "OLD"}]},
    ]
    save(old, tmp_path)
    new = [
        {
            "id": 1,
            "iso2": "ZZ",
            "states": [
                {"id": 2, "iso2": "EMPTY", "cities": []},
                {
                    "id": 4,
                    "iso2": "CON",
                    "cities": [dict(city, county_id=42)],
                },
            ],
        },
        {"id": 2, "iso2": "YY", "states": []},
    ]
    save(new, tmp_path)
    city_file = tmp_path / "by-country" / "ZZ" / "states" / "_CON" / "cities.json"
    assert list(tmp_path.glob("by-country/*/states/*/cities.json")) == [city_file]
    assert not (tmp_path / "by-country" / "YY" / "states.json").exists()
    generated = City(**json.loads(city_file.read_text(encoding="utf-8"))[0])
    assert generated.id == 1
    assert generated.state_id == 4
    assert generated.county_id == 42


def test_generate_rejects_empty_snapshot(tmp_path: Path) -> None:
    """An empty source must not erase the previous snapshot."""
    script = Path(__file__).parents[1] / "scripts" / "generate-data.py"
    save = runpy.run_path(str(script))["save_states_and_cities"]
    existing = tmp_path / "by-country" / "ZZ" / "states.json"
    existing.parent.mkdir(parents=True)
    existing.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="empty country list"):
        save([], tmp_path)
    assert existing.read_text(encoding="utf-8") == "[]"


def test_generate_rejects_unsafe_path_before_writing(tmp_path: Path) -> None:
    """An upstream state code cannot escape the generated data directory."""
    script = Path(__file__).parents[1] / "scripts" / "generate-data.py"
    save = runpy.run_path(str(script))["save_states_and_cities"]
    source = [{"id": 1, "iso2": "ZZ", "states": [{"id": 1, "iso2": "../OLD"}]}]
    with pytest.raises(ValueError, match="Invalid state code"):
        save(source, tmp_path)
    assert not list(tmp_path.iterdir())
