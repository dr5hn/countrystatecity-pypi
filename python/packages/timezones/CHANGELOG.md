# Changelog

## [3.1.0] - 2026-11-04

### Added

- County-source checksum and record count in the shared release provenance; no public API changes in this distribution.

### Changed

- Advance the seven offline packages together; the API client remains independently versioned at 0.2.1.

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

All notable changes to `countrystatecity-timezones` will be documented in this file.

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
