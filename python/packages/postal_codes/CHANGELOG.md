# Changelog

All notable changes to `countrystatecity-postal-codes` will be documented in this file.

## [1.0.2] - 2026-08-11

### Documentation
- Added a tracked path from the offline package to the freemium production API
- Added a migration guide and secure API-key guidance
- Corrected broken default-branch project links

## [1.0.1] - 2026-08-11

### Added
- `get_postcodes_by_code()` for postal codes shared by multiple localities

### Fixed
- Reject invalid country-code paths before reading package data
- Validate the complete postcode instead of accepting prefix matches
- Bound the per-country data cache to prevent retaining the full dataset
- Remove stale generated country files when upstream data disappears

### Documentation
- Distinguish 844,248 postcode/locality records from 672,370 distinct codes
- Correct validation-regex coverage to 189 of 250 countries

## [1.0.0] - 2026-08-08

### Added
- Initial release
- 844,248 postcode/locality records across 125 countries, plus format metadata for 250 countries and validation regexes for 189
- `CountryPostalInfo` model — postal code format/regex metadata per country
- `Postcode` model — individual postcode entries with locality and coordinates
- `get_countries_with_postal_data()` — retrieve postal format metadata for all countries
- `get_postal_info_by_country(country_code)` — lookup format/regex by ISO2 country code
- `get_postcodes_of_country(country_code)` — lazy-loaded postcodes for a country
- `get_postcode_by_code(country_code, code)` — lookup a specific postcode
- `search_postcodes(country_code, query)` — search by code or locality name within a country
- `validate_postcode(country_code, code)` — validate a code against the country's postal regex
- Lazy per-country data loading to keep memory footprint low despite the large dataset
- Python 3.8–3.12 support
- Full type hints and mypy strict mode compliance
- PEP 561 `py.typed` marker
