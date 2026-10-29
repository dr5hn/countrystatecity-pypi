# Changelog

## [3.0.0] - 2026-10-29

### Changed

- Update the offline package set to pinned upstream v5.0.0-export.1, with source notices and release provenance.
- This is a major data migration: upstream removes or repairs IDs. Review the upstream v5 migration files before updating stored references.
- Countries supports cities with null state links and retains population reference years. Postal codes are refreshed from the same export.

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
- Sync version with all other countrystatecity packages (countries, timezones, currencies, translations)

## [1.0.0] - 2026-06-12

### Added
- Initial release of countrystatecity-phonecodes
- `get_all_phonecodes()` — all 250+ phone code entries
- `get_phonecode_by_country(country_code)` — lookup by ISO2 country code
- `get_countries_by_phonecode(phone_code)` — all countries sharing a dialing code
- `search_phonecodes(query)` — search by country name, code, or phone code
- Full type safety with Pydantic models and mypy strict mode
- Lazy loading with LRU cache
- Python 3.8–3.12 support
