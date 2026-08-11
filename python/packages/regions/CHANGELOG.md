# Changelog

All notable changes to `countrystatecity-regions` will be documented in this file.

## [1.0.1] - 2026-08-11

### Documentation
- Added a tracked path from the offline package to the freemium production API
- Added a migration guide and secure API-key guidance
- Corrected packaged data counts and broken default-branch project links

## [1.0.0] - 2026-08-08

### Added
- Initial release
- `CountryRegion` Pydantic model with region, subregion, and country association
- `get_all_regions()` — retrieve all 250+ country-region entries
- `get_region_by_country(country_code)` — lookup region/subregion by ISO2 country code
- `get_countries_by_region(region)` — get all countries in a region (e.g., "Asia")
- `get_countries_by_subregion(subregion)` — get all countries in a subregion (e.g., "Southern Asia")
- `get_all_region_names()` — list distinct region names
- `get_all_subregion_names(region=None)` — list distinct subregion names, optionally filtered by region
- `search_regions(query)` — case-insensitive search across country name, code, region, and subregion
- Python 3.8–3.12 support
- Full type hints and mypy strict mode compliance
- PEP 561 `py.typed` marker
