# Changelog

All notable changes to `countrystatecity-countries` (Python) will be documented in this file.

## [1.0.1] - 2026-03-28

### Changed
- Updated countries/states/cities data from upstream database
- Auto-bump patch version on data updates for automatic publishing
- Data download URL updated to use GitHub Releases

### Fixed
- Detect data changes without git add so version bump is included in PR

## [1.0.0] - 2025-10-22

### Added
- Initial release on PyPI
- 250+ countries, 5,000+ states, 150,000+ cities
- Pydantic v2 models with strict validation
- Lazy-loaded data organized by country
- 10 API functions: get, search, filter by region/subregion
- Python 3.8 - 3.12 support
- Full type annotations with mypy strict mode
- Automated weekly data updates from upstream database
- CI/CD with automated PyPI publishing
