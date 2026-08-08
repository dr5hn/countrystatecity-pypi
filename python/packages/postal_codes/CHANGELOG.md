# Changelog

All notable changes to `countrystatecity-postal-codes` will be documented in this file.

## [1.0.0] - 2026-08-08

### Added
- Initial release
- 844,248 postcodes across 125 countries, plus format/regex metadata for all 250+ countries
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
