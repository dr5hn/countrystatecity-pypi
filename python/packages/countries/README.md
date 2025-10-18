# countrystatecity-countries

Official Python package for accessing comprehensive countries, states, and cities database with type hints and lazy loading.

[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-countries)](https://pypi.org/project/countrystatecity-countries/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)

## Features

- ✅ **Type-safe** with Pydantic models and mypy support
- ✅ **Lazy loading** for minimal memory footprint
- ✅ **250+ countries** with full metadata
- ✅ **5,000+ states/provinces**
- ✅ **151,000+ cities**
- ✅ **Translations** in 18+ languages
- ✅ **Timezone data** per location
- ✅ **Zero external dependencies** (except Pydantic)
- ✅ **Full test coverage** with pytest

## Installation

```bash
pip install countrystatecity-countries
```

## Quick Start

```python
from countrystatecity_countries import (
    get_countries,
    get_country_by_code,
    get_states_of_country,
    get_cities_of_state,
)

# Get all countries (lightweight)
countries = get_countries()
print(f"Total countries: {len(countries)}")

# Get specific country
usa = get_country_by_code("US")
print(f"Country: {usa.name}")
print(f"Capital: {usa.capital}")
print(f"Currency: {usa.currency_symbol} {usa.currency_name}")

# Get states (lazy loaded)
states = get_states_of_country("US")
print(f"Total states: {len(states)}")

# Get cities (lazy loaded)
cities = get_cities_of_state("US", "CA")
print(f"Cities in California: {len(cities)}")
```

## API Reference

### Countries API

#### `get_countries() -> List[Country]`

Get all countries with basic metadata.

```python
countries = get_countries()
for country in countries:
    print(f"{country.emoji} {country.name} ({country.iso2})")
```

#### `get_country_by_code(country_code: str) -> Optional[Country]`

Get country by ISO2 or ISO3 code.

```python
usa = get_country_by_code("US")  # or "USA"
print(usa.name)  # "United States"
```

#### `get_country_by_id(country_id: int) -> Optional[Country]`

Get country by ID.

```python
country = get_country_by_id(1)
```

#### `search_countries(query: str) -> List[Country]`

Search countries by name (case-insensitive).

```python
results = search_countries("united")
# Returns: [United States, United Kingdom, United Arab Emirates]
```

#### `get_countries_by_region(region: str) -> List[Country]`

Get countries in a region.

```python
asian_countries = get_countries_by_region("Asia")
```

#### `get_countries_by_subregion(subregion: str) -> List[Country]`

Get countries in a subregion.

```python
countries = get_countries_by_subregion("Southern Asia")
```

### States API

#### `get_states_of_country(country_code: str) -> List[State]`

Get all states in a country (lazy loaded).

```python
states = get_states_of_country("US")
```

#### `get_state_by_code(country_code: str, state_code: str) -> Optional[State]`

Get specific state.

```python
california = get_state_by_code("US", "CA")
print(california.name)  # "California"
```

#### `search_states(country_code: str, query: str) -> List[State]`

Search states within a country.

```python
results = search_states("US", "New")
# Returns: [New York, New Jersey, New Mexico, New Hampshire]
```

### Cities API

#### `get_cities_of_state(country_code: str, state_code: str) -> List[City]`

Get all cities in a state (lazy loaded).

```python
cities = get_cities_of_state("US", "CA")
```

#### `get_cities_of_country(country_code: str) -> List[City]`

Get all cities in a country (warning: may return a large list).

```python
cities = get_cities_of_country("US")
```

#### `search_cities(country_code: str, state_code: Optional[str], query: str) -> List[City]`

Search cities.

```python
# Search within a state
results = search_cities("US", "CA", "Los")

# Search entire country
results = search_cities("US", None, "Springfield")
```

## Data Models

### Country

```python
class Country(BaseModel):
    id: int
    name: str
    iso2: str
    iso3: str
    numeric_code: str
    phone_code: str
    capital: Optional[str]
    currency: Optional[str]
    currency_name: Optional[str]
    currency_symbol: Optional[str]
    tld: Optional[str]
    native: Optional[str]
    region: Optional[str]
    subregion: Optional[str]
    timezones: List[Dict[str, str]]
    translations: Dict[str, str]
    latitude: Optional[str]
    longitude: Optional[str]
    emoji: Optional[str]
    emojiU: Optional[str]
```

### State

```python
class State(BaseModel):
    id: int
    name: str
    country_id: int
    country_code: str
    state_code: str
    type: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
```

### City

```python
class City(BaseModel):
    id: int
    name: str
    state_id: int
    state_code: str
    country_id: int
    country_code: str
    latitude: str
    longitude: str
    wikiDataId: Optional[str]
```

## Examples

### Flask Integration

```python
from flask import Flask, jsonify
from countrystatecity_countries import get_countries, get_states_of_country

app = Flask(__name__)

@app.route('/api/countries')
def api_countries():
    countries = get_countries()
    return jsonify([c.dict() for c in countries])

@app.route('/api/countries/<code>/states')
def api_states(code: str):
    states = get_states_of_country(code.upper())
    return jsonify([s.dict() for s in states])
```

### Django Integration

```python
from countrystatecity_countries import get_countries

def get_country_choices():
    """Generate choices for Django ChoiceField."""
    countries = get_countries()
    return [(c.iso2, c.name) for c in countries]

# In your model
from django.db import models

class UserProfile(models.Model):
    country = models.CharField(
        max_length=2,
        choices=get_country_choices()
    )
```

### Command Line Tool

```python
#!/usr/bin/env python3
import sys
from countrystatecity_countries import get_country_by_code, get_states_of_country

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <country_code>")
        sys.exit(1)
    
    country_code = sys.argv[1]
    country = get_country_by_code(country_code)
    
    if not country:
        print(f"Country {country_code} not found")
        sys.exit(1)
    
    print(f"\n{country.emoji} {country.name}")
    print(f"Capital: {country.capital}")
    print(f"Region: {country.region}")
    print(f"Currency: {country.currency_symbol} {country.currency_name}")
    
    states = get_states_of_country(country_code)
    print(f"\nTotal states/provinces: {len(states)}")

if __name__ == "__main__":
    main()
```

## Performance

The package uses LRU caching and lazy loading for optimal performance:

- **Countries list**: <50ms load time
- **States data**: Loaded only when requested
- **Cities data**: Loaded only when requested
- **Memory footprint**: <10MB base, grows with usage

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/dr5hn/countrystatecity-pypi.git
cd countrystatecity-pypi/python/packages/countries

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=countrystatecity_countries --cov-report=html

# Run specific test file
pytest tests/test_countries.py
```

### Type Checking

```bash
mypy countrystatecity_countries/
```

### Code Formatting

```bash
# Format code
black countrystatecity_countries/ tests/
isort countrystatecity_countries/ tests/

# Lint code
ruff countrystatecity_countries/ tests/
```

## License

This package is licensed under the [Open Database License (ODbL-1.0)](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Support

- **Documentation**: [GitHub Repository](https://github.com/dr5hn/countrystatecity-pypi)
- **Issues**: [GitHub Issues](https://github.com/dr5hn/countrystatecity-pypi/issues)
- **Website**: [countrystatecity.in](https://countrystatecity.in)

## Related Packages

- `countrystatecity-timezones` (Coming soon)
- `countrystatecity-currencies` (Coming soon)
- `countrystatecity-languages` (Coming soon)
- `countrystatecity-phonecodes` (Coming soon)

## Acknowledgments

This package is part of the [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) project.

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
