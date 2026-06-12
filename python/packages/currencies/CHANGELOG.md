# Changelog

All notable changes to `countrystatecity-currencies` will be documented in this file.

## [1.0.3] - 2026-06-12

### Changed
- Updated data from upstream database (PR #11)

## [1.0.0] - 2026-06-05

### Added
- Initial release
- `Currency` Pydantic model with ISO 4217 code, name, symbol, and country association
- `get_all_currencies()` — retrieve all 150+ currency entries
- `get_currency_by_country(country_code)` — lookup currency by ISO2 country code
- `get_countries_by_currency(currency_code)` — get all countries using a currency
- `search_currencies(query)` — case-insensitive search across code, name, and symbol
- Python 3.8–3.12 support
- Full type hints and mypy strict mode compliance
- PEP 561 `py.typed` marker
