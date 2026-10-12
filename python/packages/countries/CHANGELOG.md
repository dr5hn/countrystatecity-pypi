# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-13

### Breaking changes
- Updated to upstream v4.0-export.50 (12 October 2026): 250 countries, 5,328
  states and 152,152 cities. The upstream v3.2 to v4.0 transition removed 4,486
  city ids (1,377 merged duplicates, 3,081 US counties moved to the counties
  dataset with new ids, and 28 non-places), reassigned 7,527 cities to states,
  added 27 states and retired 6. Names, coordinates and other metadata changed.
- Migrate stored ids with
  [`removed_ids_v3.2_to_v4.0.csv`](https://github.com/dr5hn/countries-states-cities-database/releases/download/v4.0/removed_ids_v3.2_to_v4.0.csv)
  attached to the [upstream v4.0 release](https://github.com/dr5hn/countries-states-cities-database/releases/tag/v4.0).
  County replacements belong to the counties dataset; they are not city ids.
  This mapping covers v3.2 to v4.0, before subsequent export .50 changes.
- Upstream city `type` now uses standard terms in the migrated countries and
  `type_local` holds official terms. This package's reduced combined export
  omits city `type`, city/state `type_local`, `level`, `parent_id`, city
  translations and Wikidata ids. They remain deliberately outside its models;
  `wikiDataId` remains `None`. Use standalone upstream exports for those fields.

### Added
- Optional `City.county_id` from the combined export. The counties dataset is
  available upstream and is not bundled in this package.

### Fixed
- Removed obsolete city/state files during regeneration, preventing duplicate
  city ids and stale records from surviving changes to the upstream hierarchy.

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

## [1.0.0] - 2025-10-18

### Added
- Initial release of countrystatecity-countries package
- Pydantic models for Country, State, and City
- Lazy loading with LRU cache for optimal performance
- Comprehensive API for countries, states, and cities
- Full type hints and mypy support
- 250+ countries with full metadata
- 5,000+ states/provinces
- 151,000+ cities
- Translations in 18+ languages
- Timezone data per location
- Complete test suite with pytest
- Comprehensive documentation

### Features
- `get_countries()` - Get all countries
- `get_country_by_code()` - Get country by ISO2/ISO3 code
- `get_country_by_id()` - Get country by ID
- `search_countries()` - Search countries by name
- `get_countries_by_region()` - Get countries by region
- `get_countries_by_subregion()` - Get countries by subregion
- `get_states_of_country()` - Get states of a country
- `get_state_by_code()` - Get specific state
- `search_states()` - Search states
- `get_cities_of_state()` - Get cities of a state
- `get_cities_of_country()` - Get cities of a country
- `search_cities()` - Search cities

[1.0.0]: https://github.com/dr5hn/countrystatecity-pypi/releases/tag/v1.0.0
