# countrystatecity-currencies

[![PyPI version](https://badge.fury.io/py/countrystatecity-currencies.svg)](https://badge.fury.io/py/countrystatecity-currencies)
[![Python versions](https://img.shields.io/pypi/pyversions/countrystatecity-currencies.svg)](https://pypi.org/project/countrystatecity-currencies/)

Official Python package for currency data — 150+ currencies with ISO 4217 codes, symbols, and country associations. Part of the [countrystatecity](https://github.com/dr5hn/countrystatecity-pypi) ecosystem.

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
