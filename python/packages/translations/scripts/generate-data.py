"""Generate translations.json from the countries data source.

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
    / "countrystatecity_translations"
    / "data"
    / "translations.json"
)


def generate(source: Path, output: Path) -> None:
    with open(source, encoding="utf-8") as f:
        countries = json.load(f)

    translations = []
    for country in countries:
        for lang, translated_name in country.get("translations", {}).items():
            if translated_name:
                translations.append(
                    {
                        "countryCode": country["iso2"],
                        "countryName": country["name"],
                        "lang": lang,
                        "translation": translated_name,
                    }
                )

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(translations)} translation entries → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate translations.json")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    generate(args.source, OUTPUT)
