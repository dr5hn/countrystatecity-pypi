# countrystatecity-currencies

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-currencies)](https://pypi.org/project/countrystatecity-currencies/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-currencies)](https://pypi.org/project/countrystatecity-currencies/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![currencies](https://static.pepy.tech/personalized-badge/countrystatecity-currencies?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=currencies)](https://pepy.tech/project/countrystatecity-currencies)
[![currencies](https://static.pepy.tech/personalized-badge/countrystatecity-currencies?period=week&units=international_system&left_color=grey&right_color=brightgreen&left_text=currencies)](https://pepy.tech/project/countrystatecity-currencies)

Official Python package for 249 country/currency associations, including currency codes, names, and symbols. Part of the [countrystatecity](https://github.com/dr5hn/countrystatecity-pypi) ecosystem.

## From offline prototype to production

This package provides a versioned offline snapshot. For regularly updated data,
server-side search and filtering, field-selected responses, or managed availability
and support, use the Country State City API.

[Get a free API key](https://app.countrystatecity.in/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=currencies) ·
[API docs](https://docs.countrystatecity.in/api/introduction) ·
[Pricing](https://countrystatecity.in/pricing/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=currencies) ·
[Migration guide](https://github.com/dr5hn/countrystatecity-pypi/blob/main/docs/MIGRATING_TO_API.md)

Keep API keys in server-side environment variables, never in client-side code or
source control.

## Installation

```bash
pip install countrystatecity-currencies
```

## Quick Start

```python
from countrystatecity_currencies import (
    get_all_currencies,
    get_currency_by_country,
    get_countries_by_currency,
    search_currencies,
)

# Get all currency entries
currencies = get_all_currencies()
# [Currency(code="AFN", name="Afghan afghani", symbol="؋", countryCode="AF", ...), ...]

# Get the currency for a country
usd = get_currency_by_country("US")
# Currency(code="USD", name="United States dollar", symbol="$", countryCode="US", ...)

# Get all countries using a currency
euro_countries = get_countries_by_currency("EUR")
# [Currency(code="EUR", countryCode="DE", ...), Currency(code="EUR", countryCode="FR", ...), ...]

# Search by code, name, or symbol
results = search_currencies("dollar")
# [Currency(code="USD", ...), Currency(code="CAD", ...), ...]
```

## Data Model

```python
class Currency(BaseModel):
    code: str         # ISO 4217 currency code (e.g., "USD")
    name: str         # Full currency name (e.g., "United States dollar")
    symbol: str       # Currency symbol (e.g., "$")
    countryCode: str  # ISO2 country code (e.g., "US")
    countryName: str  # Country name (e.g., "United States")
```

## API Reference

| Function | Description |
|---|---|
| `get_all_currencies()` | Get all currency entries (one per country) |
| `get_currency_by_country(code)` | Get the currency for an ISO2 country code |
| `get_countries_by_currency(code)` | Get all countries using an ISO 4217 currency code |
| `search_currencies(query)` | Search by currency code, name, or symbol |

## License

ODbL-1.0 — see [LICENSE](LICENSE).

## Other Packages in this Ecosystem

| Package | Description |
|---|---|
| [countrystatecity-countries](https://pypi.org/project/countrystatecity-countries/) | 250 countries, 5,308 states, 171,938 cities |
| [countrystatecity-timezones](https://pypi.org/project/countrystatecity-timezones/) | 432 IANA timezones with country associations and time conversion |
| [countrystatecity-translations](https://pypi.org/project/countrystatecity-translations/) | 4,724 translations in 19 languages |
| [countrystatecity-phonecodes](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250 countries |
| [countrystatecity-regions](https://pypi.org/project/countrystatecity-regions/) | Region and subregion associations for 250 countries |
| [countrystatecity-postal-codes](https://pypi.org/project/countrystatecity-postal-codes/) | Postal/ZIP records for 125 countries |

Data sourced from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
