#!/usr/bin/env python3
"""
Generate split data structure from countries-states-cities-database JSON.

This script takes the combined JSON file from countries-states-cities-database
and generates the split data structure used by the countrystatecity-countries package:
- countries.json (lightweight list)
- by-country/{ISO2}/states.json (states for each country)
- by-country/{ISO2}/states/{STATE_CODE}/cities.json (cities for each state)

Usage:
    python generate-data.py <path-to-combined-json>

Example:
    python generate-data.py /tmp/countries-data.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_combined_data(filepath: str) -> List[Dict[str, Any]]:
    """Load the combined countries+states+cities JSON file."""
    print(f"Loading data from {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✓ Loaded {len(data)} countries")
    return data


def create_countries_list(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create lightweight countries list (without states/cities)."""
    countries = []
    for country in data:
        # Convert timezone gmtOffset from int to str for Pydantic validation
        timezones = []
        for tz in country.get("timezones", []):
            tz_copy = tz.copy()
            if "gmtOffset" in tz_copy and isinstance(tz_copy["gmtOffset"], int):
                tz_copy["gmtOffset"] = str(tz_copy["gmtOffset"])
            timezones.append(tz_copy)

        # Transform country data to match our model
        country_data = {
            "id": country.get("id"),
            "name": country.get("name"),
            "iso2": country.get("iso2"),
            "iso3": country.get("iso3"),
            "numeric_code": country.get("numeric_code"),
            "phone_code": country.get("phonecode", ""),  # Map phonecode -> phone_code
            "capital": country.get("capital"),
            "currency": country.get("currency"),
            "currency_name": country.get("currency_name"),
            "currency_symbol": country.get("currency_symbol"),
            "tld": country.get("tld"),
            "native": country.get("native"),
            "region": country.get("region"),
            "subregion": country.get("subregion"),
            "timezones": timezones,
            "translations": country.get("translations", {}),
            "latitude": country.get("latitude"),
            "longitude": country.get("longitude"),
            "emoji": country.get("emoji"),
            "emojiU": country.get("emojiU")
        }
        countries.append(country_data)
    return countries


def save_countries(countries: List[Dict[str, Any]], output_dir: Path) -> None:
    """Save countries list to countries.json."""
    output_file = output_dir / "countries.json"
    print(f"Saving {len(countries)} countries to {output_file}...")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved countries.json")


def save_states_and_cities(data: List[Dict[str, Any]], output_dir: Path) -> None:
    """Save states and cities in split structure."""
    total_states = 0
    total_cities = 0

    for country in data:
        country_iso2 = country.get("iso2")
        country_id = country.get("id")
        if not country_iso2 or not country_id:
            continue

        states = country.get("states", [])
        if not states:
            continue

        # Create country directory
        country_dir = output_dir / "by-country" / country_iso2
        country_dir.mkdir(parents=True, exist_ok=True)

        # Create states list (without cities) and transform field names
        states_list = []
        for state in states:
            # Transform state data to match our model
            state_data = {
                "id": state.get("id"),
                "name": state.get("name"),
                "country_id": country_id,
                "country_code": country_iso2,
                "state_code": state.get("iso2", ""),  # Map iso2 -> state_code
                "type": state.get("type"),
                "latitude": state.get("latitude"),
                "longitude": state.get("longitude"),
                "iso3166_2": state.get("iso3166_2"),
                "native": state.get("native"),
                "timezone": state.get("timezone")
            }
            states_list.append(state_data)

        # Save states.json
        states_file = country_dir / "states.json"
        with open(states_file, "w", encoding="utf-8") as f:
            json.dump(states_list, f, ensure_ascii=False, indent=2)

        total_states += len(states_list)

        # Save cities for each state
        states_dir = country_dir / "states"
        states_dir.mkdir(exist_ok=True)

        for state in states:
            state_id = state.get("id")
            state_code = state.get("iso2", "")  # Map iso2 -> state_code
            cities = state.get("cities", [])

            if not state_code or not cities or not state_id:
                continue

            # Create state directory
            state_dir = states_dir / state_code
            state_dir.mkdir(exist_ok=True)

            # Transform city data to match our model
            cities_list = []
            for city in cities:
                city_data = {
                    "id": city.get("id"),
                    "name": city.get("name"),
                    "state_id": state_id,
                    "state_code": state_code,
                    "country_id": country_id,
                    "country_code": country_iso2,
                    "latitude": city.get("latitude", ""),
                    "longitude": city.get("longitude", ""),
                    "wikiDataId": None  # Not available in new format
                }
                cities_list.append(city_data)

            # Save cities.json
            cities_file = state_dir / "cities.json"
            with open(cities_file, "w", encoding="utf-8") as f:
                json.dump(cities_list, f, ensure_ascii=False, indent=2)

            total_cities += len(cities_list)

    print(f"✓ Saved {total_states} states across {len(data)} countries")
    print(f"✓ Saved {total_cities} cities")


def main():
    """Main function to generate split data structure."""
    if len(sys.argv) < 2:
        print("Usage: python generate-data.py <path-to-combined-json>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Determine output directory (data directory in the package)
    script_dir = Path(__file__).parent
    package_dir = script_dir.parent
    output_dir = package_dir / "countrystatecity_countries" / "data"

    print(f"Output directory: {output_dir}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load combined data
    data = load_combined_data(input_file)

    # Generate countries list
    countries = create_countries_list(data)
    save_countries(countries, output_dir)

    # Generate states and cities
    save_states_and_cities(data, output_dir)

    print("\n" + "=" * 60)
    print("✅ Data generation completed successfully!")
    print("=" * 60)
    print(f"\nGenerated files in: {output_dir}")
    print(f"  - countries.json ({len(countries)} countries)")
    print(f"  - by-country/*/states.json")
    print(f"  - by-country/*/states/*/cities.json")


if __name__ == "__main__":
    main()
