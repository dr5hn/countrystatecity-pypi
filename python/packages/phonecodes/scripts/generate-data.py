"""Generate phonecodes.json from the countries data source.

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
    / "countrystatecity_phonecodes"
    / "data"
    / "phonecodes.json"
)


def generate(source: Path, output: Path) -> None:
    with open(source, encoding="utf-8") as f:
        countries = json.load(f)

    phonecodes = []
    for country in countries:
        phone_code = country.get("phone_code")
        if not phone_code:
            continue
        phonecodes.append(
            {
                "phoneCode": str(phone_code),
                "countryCode": country["iso2"],
                "countryName": country["name"],
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(phonecodes, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(phonecodes)} phone code entries → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate phonecodes.json")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    generate(args.source, OUTPUT)
