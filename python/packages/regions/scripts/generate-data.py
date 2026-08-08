"""Generate regions.json from the countries data source.

Usage:
    python scripts/generate-data.py [--source PATH]

The source defaults to the countries package data alongside this repo.
"""

import argparse
import json
from pathlib import Path

DEFAULT_SOURCE = (
    Path(__file__).parent.parent.parent
    / "countries"
    / "countrystatecity_countries"
    / "data"
    / "countries.json"
)

OUTPUT = (
    Path(__file__).parent.parent
    / "countrystatecity_regions"
    / "data"
    / "regions.json"
)


def generate(source: Path, output: Path) -> None:
    with open(source, encoding="utf-8") as f:
        countries = json.load(f)

    regions = []
    for country in countries:
        regions.append(
            {
                "countryCode": country["iso2"],
                "countryName": country["name"],
                "region": country.get("region"),
                "subregion": country.get("subregion"),
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(regions, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(regions)} region entries → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate regions.json")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    generate(args.source, OUTPUT)
