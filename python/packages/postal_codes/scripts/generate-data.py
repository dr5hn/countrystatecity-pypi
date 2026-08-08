"""Generate postal-codes package data from upstream sources.

This script builds:
- countrystatecity_postal_codes/data/countries.json — postal format/regex
  metadata for every country, plus a postcode count.
- countrystatecity_postal_codes/data/by-country/{ISO2}/postcodes.json — the
  individual postcodes for each country that has contribution data.

Usage:
    python scripts/generate-data.py --countries-source PATH --postcodes-dir DIR

The upstream project publishes postal_code_format/postal_code_regex on the
countries table (see json/countries.json), and per-country postcode
contributions as separate JSON files under contributions/postcodes/ — there
is no single combined export for postcodes. See scripts/README.md for how
to fetch both.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

OUTPUT_DIR = Path(__file__).parent.parent / "countrystatecity_postal_codes" / "data"


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_countries(source: Path) -> List[Dict[str, Any]]:
    with open(source, encoding="utf-8") as f:
        return json.load(f)


def load_country_postcodes(postcodes_dir: Path, iso2: str) -> List[Dict[str, Any]]:
    file_path = postcodes_dir / f"{iso2}.json"
    if not file_path.exists():
        return []
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def transform_postcode(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "code": record["code"],
        "countryCode": record["country_code"],
        "stateCode": record.get("state_code"),
        "localityName": record.get("locality_name"),
        "type": record.get("type"),
        "latitude": _to_float(record.get("latitude")),
        "longitude": _to_float(record.get("longitude")),
    }


def generate(countries_source: Path, postcodes_dir: Path, output_dir: Path) -> None:
    countries = load_countries(countries_source)

    country_entries = []
    total_postcodes = 0
    countries_with_data = 0

    for country in countries:
        iso2 = country.get("iso2")
        if not iso2:
            continue

        raw_postcodes = load_country_postcodes(postcodes_dir, iso2)

        if raw_postcodes:
            country_dir = output_dir / "by-country" / iso2
            country_dir.mkdir(parents=True, exist_ok=True)
            transformed = [transform_postcode(r) for r in raw_postcodes]
            with open(country_dir / "postcodes.json", "w", encoding="utf-8") as f:
                json.dump(transformed, f, ensure_ascii=False, indent=2)
            total_postcodes += len(transformed)
            countries_with_data += 1

        country_entries.append(
            {
                "countryCode": iso2,
                "countryName": country.get("name"),
                "postalCodeFormat": country.get("postal_code_format"),
                "postalCodeRegex": country.get("postal_code_regex"),
                "postcodeCount": len(raw_postcodes),
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "countries.json", "w", encoding="utf-8") as f:
        json.dump(country_entries, f, ensure_ascii=False, indent=2)

    print(
        f"Generated {len(country_entries)} country entries "
        f"→ {output_dir / 'countries.json'}"
    )
    print(
        f"Generated {total_postcodes} postcodes across {countries_with_data} "
        f"countries → {output_dir / 'by-country'}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate postal-codes package data")
    parser.add_argument("--countries-source", type=Path, required=True)
    parser.add_argument("--postcodes-dir", type=Path, required=True)
    args = parser.parse_args()
    generate(args.countries_source, args.postcodes_dir, OUTPUT_DIR)
