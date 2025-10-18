# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
