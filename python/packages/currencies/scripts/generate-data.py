"""Generate currencies.json from the countries data source.

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
    / "countrystatecity_currencies"
    / "data"
    / "currencies.json"
)


def generate(source: Path, output: Path) -> None:
    with open(source, encoding="utf-8") as f:
        countries = json.load(f)

    currencies = []
    for country in countries:
        code = country.get("currency")
        name = country.get("currency_name")
        symbol = country.get("currency_symbol")
        if not code or not name or not symbol:
            continue
        # Skip codes that don't meet ISO 4217 format (3 uppercase letters)
        if not (len(code) == 3 and code.isupper() and code.isalpha()):
            continue
        # Skip known non-registered codes present in the upstream database
        if code in {"AAD"}:
            continue
        currencies.append(
            {
                "code": code,
                "name": name,
                "symbol": symbol,
                "countryCode": country["iso2"],
                "countryName": country["name"],
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(currencies, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(currencies)} currency entries → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate currencies.json")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    generate(args.source, OUTPUT)
