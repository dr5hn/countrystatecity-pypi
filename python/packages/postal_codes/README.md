# countrystatecity-postal-codes

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-postal-codes)](https://pypi.org/project/countrystatecity-postal-codes/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-postal-codes)](https://pypi.org/project/countrystatecity-postal-codes/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![postal-codes](https://static.pepy.tech/personalized-badge/countrystatecity-postal-codes?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=postal-codes)](https://pepy.tech/project/countrystatecity-postal-codes)
[![postal-codes](https://static.pepy.tech/personalized-badge/countrystatecity-postal-codes?period=week&units=international_system&left_color=grey&right_color=brightgreen&left_text=postal-codes)](https://pepy.tech/project/countrystatecity-postal-codes)

Official Python package for postal/ZIP code data — 844,000+ postcodes with localities and coordinates across 125 countries, plus format/validation regex for all 250+ countries. Part of the [countrystatecity](https://github.com/dr5hn/countrystatecity-pypi) ecosystem.

Like the [countries](https://pypi.org/project/countrystatecity-countries/) package, postcode data is **lazy-loaded per country** — installing the package doesn't load anything into memory until you ask for a specific country's data.

## Installation

```bash
pip install countrystatecity-postal-codes
```

## Quick Start

```python
from countrystatecity_postal_codes import (
    get_countries_with_postal_data,
    get_postal_info_by_country,
    get_postcodes_of_country,
    get_postcode_by_code,
    search_postcodes,
    validate_postcode,
)

# Postal code format/regex for a country
us_info = get_postal_info_by_country("US")
# CountryPostalInfo(countryCode="US", postalCodeFormat="#####", postalCodeRegex="^\\d{5}$", ...)

# Validate a postcode against the country's known format
validate_postcode("US", "10001")   # True
validate_postcode("US", "abcde")   # False

# All postcodes for a country (lazy loaded)
postcodes = get_postcodes_of_country("AD")
# [Postcode(code="AD100", localityName="Canillo", ...), ...]

# Look up a specific postcode
pc = get_postcode_by_code("AD", "AD100")
print(pc.localityName)  # Canillo

# Search by code or locality name within a country
results = search_postcodes("AD", "canillo")

# List postal-format metadata for every country
all_countries = get_countries_with_postal_data()
```

## Data Model

```python
class CountryPostalInfo(BaseModel):
    countryCode: str               # ISO2 country code (e.g., "US")
    countryName: str                # Country name (e.g., "United States")
    postalCodeFormat: Optional[str] # Format pattern (e.g., "#####")
    postalCodeRegex: Optional[str]  # Validation regex (e.g., "^\\d{5}$")
    postcodeCount: int              # Number of individual postcodes available for this country

class Postcode(BaseModel):
    code: str                       # The postal code value (e.g., "10001")
    countryCode: str                # ISO2 country code (e.g., "US")
    stateCode: Optional[str]        # State/province code, if known
    localityName: Optional[str]     # Human-readable place name
    type: Optional[str]             # Granularity: full | outward | sector | district | area
    latitude: Optional[float]
    longitude: Optional[float]
```

## API Reference

| Function | Description |
|---|---|
| `get_countries_with_postal_data()` | Get postal format/regex metadata for all countries |
| `get_postal_info_by_country(code)` | Get postal format/regex metadata for an ISO2 country code |
| `get_postcodes_of_country(code)` | Get all postcodes for a country (lazy loaded) |
| `get_postcode_by_code(code, postcode)` | Look up a specific postcode within a country |
| `search_postcodes(code, query)` | Search postcodes within a country by code or locality name |
| `validate_postcode(code, postcode)` | Validate a postcode against the country's known format |

## Coverage

Individual postcode listings are available for 125 countries with source data upstream (844,248 postcodes total, varying granularity per country). `get_postal_info_by_country()` returns format/regex metadata for all 250+ countries where known, even if per-postcode listings aren't available — check `postcodeCount` to see how many individual postcodes are available for a given country.

## License

ODbL-1.0 — see [LICENSE](LICENSE).

## Other Packages in this Ecosystem

| Package | Description |
|---|---|
| [countrystatecity-countries](https://pypi.org/project/countrystatecity-countries/) | 250+ countries, 5,000+ states, 150,000+ cities |
| [countrystatecity-timezones](https://pypi.org/project/countrystatecity-timezones/) | 400+ IANA timezones with country associations and time conversion |
| [countrystatecity-currencies](https://pypi.org/project/countrystatecity-currencies/) | Currency codes, names, and symbols |
| [countrystatecity-translations](https://pypi.org/project/countrystatecity-translations/) | Country name translations in 18+ languages |
| [countrystatecity-phonecodes](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250+ countries |
| [countrystatecity-regions](https://pypi.org/project/countrystatecity-regions/) | Continents and geographic subregions for 250+ countries |

Data sourced from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
