"""Verify generated package counts against the pinned export before release."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    """Reject omitted cities, mixed source tags, and incomplete postcode refreshes."""
    record = json.loads((ROOT / "python/data/release.json").read_text())
    countries_data = ROOT / "python/packages/countries/countrystatecity_countries/data"
    postal_data = (
        ROOT / "python/packages/postal_codes/countrystatecity_postal_codes/data"
    )
    countries = json.loads((countries_data / "countries.json").read_text())
    city_files = list(countries_data.glob("by-country/*/states/*/cities.json")) + list(
        countries_data.glob("by-country/*/cities.json")
    )
    city_ids = [
        city["id"] for file in city_files for city in json.loads(file.read_text())
    ]
    postcode_count = sum(
        len(json.loads(file.read_text()))
        for file in postal_data.glob("by-country/*/postcodes.json")
    )
    actual = {
        "countries": len(countries),
        "cities": len(city_ids),
        "postcodes": postcode_count,
    }
    if actual != record["counts"] or len(set(city_ids)) != len(city_ids):
        raise ValueError(
            f"Generated snapshot does not match export: {actual} != {record['counts']}"
        )
    for package_dir in (ROOT / "python/packages").iterdir():
        if package_dir.name == "api" or not package_dir.is_dir():
            continue
        provenance = (
            package_dir / f"countrystatecity_{package_dir.name}" / "data/release.json"
        )
        if json.loads(provenance.read_text()) != record:
            raise ValueError(f"Mixed snapshot in {package_dir.name}")
    print(f"Verified {record['sourceRelease']}: {actual}")


if __name__ == "__main__":
    main()
