"""Tests for the postal-code data generator."""

import json
import runpy
from pathlib import Path


def test_generate_removes_stale_country_data(tmp_path: Path) -> None:
    """Remove generated files whose upstream country data disappeared."""
    countries_source = tmp_path / "countries.json"
    postcodes_dir = tmp_path / "source-postcodes"
    output_dir = tmp_path / "output"
    stale_dir = output_dir / "by-country" / "ZZ"

    postcodes_dir.mkdir()
    stale_dir.mkdir(parents=True)
    countries_source.write_text(
        json.dumps(
            [
                {
                    "iso2": "ZZ",
                    "name": "Test Country",
                    "postal_code_format": None,
                    "postal_code_regex": None,
                }
            ]
        ),
        encoding="utf-8",
    )
    (stale_dir / "postcodes.json").write_text("[]", encoding="utf-8")

    script = Path(__file__).parents[1] / "scripts" / "generate-data.py"
    generate = runpy.run_path(str(script))["generate"]
    generate(countries_source, postcodes_dir, output_dir)

    assert not stale_dir.exists()
    metadata = json.loads((output_dir / "countries.json").read_text(encoding="utf-8"))
    assert metadata[0]["postcodeCount"] == 0
