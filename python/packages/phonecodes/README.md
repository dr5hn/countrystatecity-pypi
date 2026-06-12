# countrystatecity-phonecodes

Type-safe Python package for international phone/dialing codes with 250+ country associations.

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-phonecodes)](https://pypi.org/project/countrystatecity-phonecodes/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-phonecodes)](https://pypi.org/project/countrystatecity-phonecodes/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)

## Installation

```bash
pip install countrystatecity-phonecodes
```

## Usage

```python
from countrystatecity_phonecodes import (
    get_all_phonecodes,
    get_phonecode_by_country,
    get_countries_by_phonecode,
    search_phonecodes,
)

# Get phone code for a country
us = get_phonecode_by_country("US")
print(f"+{us.phoneCode} — {us.countryName}")  # +1 — United States

# Get all countries sharing a dialing code
plus1 = get_countries_by_phonecode("1")
print(f"{len(plus1)} countries use +1")  # 25 countries use +1

# Works with or without + prefix
plus44 = get_countries_by_phonecode("+44")

# Search by country name, code, or phone code
results = search_phonecodes("united")
results = search_phonecodes("44")

# All phone codes
all_codes = get_all_phonecodes()
print(f"Total entries: {len(all_codes)}")
```

## API Reference

### `get_all_phonecodes() -> List[PhoneCode]`
Returns all phone code entries (one per country).

### `get_phonecode_by_country(country_code: str) -> Optional[PhoneCode]`
Returns the phone code for a country by ISO2 code (e.g., `"US"`).

### `get_countries_by_phonecode(phone_code: str) -> List[PhoneCode]`
Returns all countries sharing a dialing code (e.g., `"1"` or `"+1"`).

### `search_phonecodes(query: str) -> List[PhoneCode]`
Search by country name, ISO2 code, or phone code (case-insensitive).

## PhoneCode Model

```python
class PhoneCode:
    phoneCode: str      # e.g. "1", "44", "91"
    countryCode: str    # ISO2 e.g. "US", "GB", "IN"
    countryName: str    # e.g. "United States"
```

## License

[Open Database License (ODbL-1.0)](LICENSE)
