# Changelog

All notable changes to `countrystatecity-timezones` will be documented in this file.

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

## [1.0.0] - 2026-06-04

### Added
- Initial release
- `Timezone` Pydantic model with full timezone metadata and country association
- `get_all_timezones()` — retrieve all 400+ timezone entries
- `get_timezones_by_country(country_code)` — filter timezones by ISO2 country code
- `get_timezone_by_zone_name(zone_name)` — lookup by IANA zone name
- `get_timezones_by_offset(gmt_offset)` — filter by GMT offset in seconds
- `search_timezones(query)` — case-insensitive search across zone name, timezone name, and abbreviation
- `convert_time(dt, from_tz, to_tz)` — convert datetime between IANA timezones
- Python 3.8–3.12 support
- Full type hints and mypy strict mode compliance
- PEP 561 `py.typed` marker
