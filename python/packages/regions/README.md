# countrystatecity-regions

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-regions)](https://pypi.org/project/countrystatecity-regions/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-regions)](https://pypi.org/project/countrystatecity-regions/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![regions](https://static.pepy.tech/personalized-badge/countrystatecity-regions?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=regions)](https://pepy.tech/project/countrystatecity-regions)
[![regions](https://static.pepy.tech/personalized-badge/countrystatecity-regions?period=week&units=international_system&left_color=grey&right_color=brightgreen&left_text=regions)](https://pepy.tech/project/countrystatecity-regions)

Official Python package for region and subregion associations across 250 countries. Part of the [countrystatecity](https://github.com/dr5hn/countrystatecity-pypi) ecosystem.

## From offline prototype to production

This package provides a versioned offline snapshot. For regularly updated data,
server-side search and filtering, field-selected responses, or managed availability
and support, use the Country State City API through its official Python client:

```bash
pip install countrystatecity-api
```

```python
from countrystatecity import CountryStateCity

csc = CountryStateCity()          # reads CSC_API_KEY
```

[Get a free API key](https://app.countrystatecity.in/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=regions) ·
[API docs](https://docs.countrystatecity.in/api/introduction) ·
[Pricing](https://countrystatecity.in/pricing/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=regions) ·
[Migration guide](https://github.com/dr5hn/countrystatecity-pypi/blob/main/docs/MIGRATING_TO_API.md)

Keep API keys in server-side environment variables, never in client-side code or
source control.

## Installation

```bash
pip install countrystatecity-regions
```

## Quick Start

```python
from countrystatecity_regions import (
    get_all_regions,
    get_region_by_country,
    get_countries_by_region,
    get_countries_by_subregion,
    get_all_region_names,
    get_all_subregion_names,
    search_regions,
)

# Get all country-region entries
regions = get_all_regions()
# [CountryRegion(countryCode="AF", countryName="Afghanistan", region="Asia", subregion="Southern Asia"), ...]

# Get the region/subregion for a country
us = get_region_by_country("US")
# CountryRegion(countryCode="US", countryName="United States", region="Americas", subregion="Northern America")

# Get all countries in a region
asian_countries = get_countries_by_region("Asia")
# [CountryRegion(countryCode="AF", ...), CountryRegion(countryCode="CN", ...), ...]

# Get all countries in a subregion
south_asia = get_countries_by_subregion("Southern Asia")
# [CountryRegion(countryCode="AF", ...), CountryRegion(countryCode="IN", ...), ...]

# List distinct region/subregion names
regions_list = get_all_region_names()
# ["Africa", "Americas", "Asia", "Europe", "Oceania", "Polar"]

asia_subregions = get_all_subregion_names("Asia")
# ["Central Asia", "Eastern Asia", "South-eastern Asia", "Southern Asia", "Western Asia"]

# Search by country name, code, region, or subregion
results = search_regions("southern asia")
```

## Data Model

```python
class CountryRegion(BaseModel):
    countryCode: str          # ISO2 country code (e.g., "US")
    countryName: str          # Country name (e.g., "United States")
    region: Optional[str]     # Continent/region (e.g., "Americas")
    subregion: Optional[str]  # Geographic subregion (e.g., "Northern America")
```

## API Reference

| Function | Description |
|---|---|
| `get_all_regions()` | Get all country-region entries |
| `get_region_by_country(code)` | Get the region/subregion for an ISO2 country code |
| `get_countries_by_region(region)` | Get all countries in a region (e.g., "Asia") |
| `get_countries_by_subregion(subregion)` | Get all countries in a subregion (e.g., "Southern Asia") |
| `get_all_region_names()` | Get all distinct region names, sorted |
| `get_all_subregion_names(region=None)` | Get all distinct subregion names, optionally filtered by region |
| `search_regions(query)` | Search by country name, code, region, or subregion |

## License

ODbL-1.0 — see [LICENSE](LICENSE).

## Other Packages in this Ecosystem

| Package | Description |
|---|---|
| [countrystatecity-api](https://pypi.org/project/countrystatecity-api/) | **Official API client** — live data, sync + async, typed |
| [countrystatecity-countries](https://pypi.org/project/countrystatecity-countries/) | 250 countries, 5,308 states, 171,938 cities |
| [countrystatecity-timezones](https://pypi.org/project/countrystatecity-timezones/) | 432 IANA timezones with country associations and time conversion |
| [countrystatecity-currencies](https://pypi.org/project/countrystatecity-currencies/) | 249 country/currency associations |
| [countrystatecity-translations](https://pypi.org/project/countrystatecity-translations/) | 4,724 translations in 19 languages |
| [countrystatecity-phonecodes](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250 countries |
| [countrystatecity-postal-codes](https://pypi.org/project/countrystatecity-postal-codes/) | Postal/ZIP records for 125 countries |

Data sourced from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
