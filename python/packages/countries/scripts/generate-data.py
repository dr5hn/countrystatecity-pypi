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
        country_data = {k: v for k, v in country.items() if k not in ['states']}
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
        iso2 = country.get("iso2")
        if not iso2:
            continue
        
        states = country.get("states", [])
        if not states:
            continue
        
        # Create country directory
        country_dir = output_dir / "by-country" / iso2
        country_dir.mkdir(parents=True, exist_ok=True)
        
        # Create states list (without cities)
        states_list = []
        for state in states:
            state_data = {k: v for k, v in state.items() if k not in ['cities']}
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
            state_code = state.get("state_code")
            cities = state.get("cities", [])
            
            if not state_code or not cities:
                continue
            
            # Create state directory
            state_dir = states_dir / state_code
            state_dir.mkdir(exist_ok=True)
            
            # Save cities.json
            cities_file = state_dir / "cities.json"
            with open(cities_file, "w", encoding="utf-8") as f:
                json.dump(cities, f, ensure_ascii=False, indent=2)
            
            total_cities += len(cities)
    
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
