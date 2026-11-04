# Changelog

## [3.0.1] - 2026-11-04

### Changed

- Refresh the offline snapshot from immutable upstream v5.2.0-export.1, including updated source notices and checksummed release provenance.
- Snapshot totals: 250 countries, 5,327 states, 156,169 cities and 728,556 postcode/locality records across 117 countries.
- Publish using isolated builds, PyPI Trusted Publishing and attestations; API client version remains unchanged.

## [3.0.0] - 2026-10-29

### Changed

- Update the offline package set to pinned upstream v5.0.0-export.1, with source notices and release provenance.
- This is a major data migration: upstream removes or repairs IDs. Review the upstream v5 migration files before updating stored references.
- Countries supports cities with null state links and retains population reference years. Postal codes are refreshed from the same export.

All notable changes to `countrystatecity-currencies` will be documented in this file.

## [2.0.1] - 2026-10-12

### Changed
- Updated data from upstream database (PR #23)

## [1.0.5] - 2026-08-11

### Documentation
- Added a tracked path from the offline package to the freemium production API
- Added a migration guide and secure API-key guidance
- Corrected packaged data counts and broken default-branch project links

## [1.0.4] - 2026-08-08

### Changed
- Updated data from upstream database (PR #13)

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
