# countrystatecity-postal-codes

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-postal-codes)](https://pypi.org/project/countrystatecity-postal-codes/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-postal-codes)](https://pypi.org/project/countrystatecity-postal-codes/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![postal-codes](https://static.pepy.tech/personalized-badge/countrystatecity-postal-codes?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=postal-codes)](https://pepy.tech/project/countrystatecity-postal-codes)
[![postal-codes](https://static.pepy.tech/personalized-badge/countrystatecity-postal-codes?period=week&units=international_system&left_color=grey&right_color=brightgreen&left_text=postal-codes)](https://pepy.tech/project/countrystatecity-postal-codes)

Official Python package for postal/ZIP code data — 844,248 postcode/locality records representing 672,370 distinct codes across 125 countries, plus format metadata for 250 countries and validation regexes for 189. Part of the [countrystatecity](https://github.com/dr5hn/countrystatecity-pypi) ecosystem.

Like the [countries](https://pypi.org/project/countrystatecity-countries/) package, postcode data is **lazy-loaded per country** — installing the package doesn't load anything into memory until you ask for a specific country's data.

## From offline prototype to production

This package provides a versioned offline snapshot. For regularly updated data,
server-side search and filtering, field-selected responses, or managed availability
and support, use the Country State City API through its official Python client:

```bash
pip install countrystatecity
```

```python
from countrystatecity import CountryStateCity

csc = CountryStateCity()          # reads CSC_API_KEY
```

[Get a free API key](https://app.countrystatecity.in/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=postal_codes) ·
[API docs](https://docs.countrystatecity.in/api/introduction) ·
[Pricing](https://countrystatecity.in/pricing/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=postal_codes) ·
[Migration guide](https://github.com/dr5hn/countrystatecity-pypi/blob/main/docs/MIGRATING_TO_API.md)

Keep API keys in server-side environment variables, never in client-side code or
source control.

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
    get_postcodes_by_code,
    search_postcodes,
    validate_postcode,
)

# Postal code format/regex for a country
us_info = get_postal_info_by_country("US")
# CountryPostalInfo(countryCode="US", postalCodeFormat="#####-####", postalCodeRegex="^\\d{5}(-\\d{4})?$", ...)

# Validate a postcode against the country's known format
validate_postcode("US", "10001")   # True
validate_postcode("US", "abcde")   # False

# All postcodes for a country (lazy loaded)
postcodes = get_postcodes_of_country("AD")
# [Postcode(code="AD100", localityName="Canillo", ...), ...]

# Look up the first entry for a postcode
pc = get_postcode_by_code("AD", "AD100")
print(pc.localityName)  # Canillo

# Get every locality when a postcode is shared
matches = get_postcodes_by_code("BB", "BB18000")
# [Postcode(localityName="Crane", ...), Postcode(localityName="Six Cross Roads", ...)]

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
| `get_postcode_by_code(code, postcode)` | Get the first entry for a postcode within a country |
| `get_postcodes_by_code(code, postcode)` | Get every entry when a postcode covers multiple localities |
| `search_postcodes(code, query)` | Search postcodes within a country by code or locality name |
| `validate_postcode(code, postcode)` | Validate a postcode against the country's known format |

## Coverage

Individual postcode listings are available for 125 countries with source data upstream: 844,248 postcode/locality records representing 672,370 distinct codes, with varying granularity per country. `get_postal_info_by_country()` returns format metadata for all 250 countries and validation regexes for the 189 countries where one is known, even if per-postcode listings aren't available. Check `postcodeCount` to see how many records are available for a given country.

## License

ODbL-1.0 — see [LICENSE](LICENSE).

## Other Packages in this Ecosystem

| Package | Description |
|---|---|
| [countrystatecity](https://pypi.org/project/countrystatecity/) | **Official API client** — live data, sync + async, typed |
| [countrystatecity-countries](https://pypi.org/project/countrystatecity-countries/) | 250 countries, 5,308 states, 171,938 cities |
| [countrystatecity-timezones](https://pypi.org/project/countrystatecity-timezones/) | 432 IANA timezones with country associations and time conversion |
| [countrystatecity-currencies](https://pypi.org/project/countrystatecity-currencies/) | 249 country/currency associations |
| [countrystatecity-translations](https://pypi.org/project/countrystatecity-translations/) | 4,724 translations in 19 languages |
| [countrystatecity-phonecodes](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250 countries |
| [countrystatecity-regions](https://pypi.org/project/countrystatecity-regions/) | Region and subregion associations for 250 countries |

Data sourced from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
