# Python Package Quick Start Guide

Step-by-step guide to implement the first Python package.

---

## 🚀 Phase 1: Setup (Day 1)

### Step 1: Create Directory Structure

```bash
cd /path/to/countries-states-cities-database

# Create Python directory structure
mkdir -p python/packages/countries/countrystatecity_countries/data
mkdir -p python/packages/countries/tests
mkdir -p python/packages/countries/scripts
mkdir -p python/shared
mkdir -p python/scripts
```

### Step 2: Install Poetry

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

### Step 3: Initialize Package

```bash
cd python/packages/countries

# Initialize Poetry project
poetry init --name countrystatecity-countries \
            --description "Official countries, states, and cities database" \
            --author "dr5hn <your.email@example.com>" \
            --python "^3.8" \
            --license "ODbL-1.0"

# Add dependencies
poetry add pydantic

# Add dev dependencies
poetry add --group dev pytest pytest-cov mypy black isort ruff

# Install dependencies
poetry install
```

---

## 📝 Phase 2: Core Implementation (Days 2-3)

### Step 1: Create Models (`countrystatecity_countries/models.py`)

```python
"""Pydantic models for countries, states, and cities."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class Country(BaseModel):
    """Country model with full metadata."""
    
    id: int
    name: str
    iso2: str = Field(..., min_length=2, max_length=2)
    iso3: str = Field(..., min_length=3, max_length=3)
    numeric_code: str
    phone_code: str
    capital: Optional[str] = None
    currency: Optional[str] = None
    currency_name: Optional[str] = None
    currency_symbol: Optional[str] = None
    tld: Optional[str] = None
    native: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    timezones: List[Dict[str, str]] = Field(default_factory=list)
    translations: Dict[str, str] = Field(default_factory=dict)
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    emoji: Optional[str] = None
    emojiU: Optional[str] = None
    
    class Config:
        frozen = True
        extra = "forbid"


class State(BaseModel):
    """State/Province model."""
    
    id: int
    name: str
    country_id: int
    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str
    state_code: str
    type: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    timezone: Optional[str] = None
    
    class Config:
        frozen = True
        extra = "forbid"


class City(BaseModel):
    """City model."""
    
    id: int
    name: str
    state_id: int
    state_code: str
    state_name: str
    country_id: int
    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str
    latitude: str
    longitude: str
    timezone: Optional[str] = None
    wikiDataId: Optional[str] = None
    
    class Config:
        frozen = True
        extra = "forbid"
```

### Step 2: Create Data Loader (`countrystatecity_countries/loaders.py`)

```python
"""Lazy data loading with caching."""

import json
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any, Optional


class DataLoader:
    """Lazy data loader with LRU caching."""
    
    _data_dir = Path(__file__).parent / "data"
    
    @classmethod
    @lru_cache(maxsize=1)
    def load_countries(cls) -> List[Dict[str, Any]]:
        """Load countries list (cached)."""
        countries_file = cls._data_dir / "countries.json"
        if not countries_file.exists():
            raise FileNotFoundError(f"Countries data not found: {countries_file}")
        
        with open(countries_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @classmethod
    @lru_cache(maxsize=250)
    def load_country_metadata(cls, country_code: str) -> Optional[Dict[str, Any]]:
        """Load full country metadata (cached per country)."""
        meta_file = cls._data_dir / "by-country" / country_code / "meta.json"
        if not meta_file.exists():
            return None
        
        with open(meta_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @classmethod
    @lru_cache(maxsize=250)
    def load_states(cls, country_code: str) -> List[Dict[str, Any]]:
        """Load states for country (cached per country)."""
        states_file = cls._data_dir / "by-country" / country_code / "states.json"
        if not states_file.exists():
            return []
        
        with open(states_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @classmethod
    @lru_cache(maxsize=5000)
    def load_cities(cls, country_code: str, state_code: str) -> List[Dict[str, Any]]:
        """Load cities for state (cached per state)."""
        cities_file = (
            cls._data_dir / "by-country" / country_code / 
            "states" / state_code / "cities.json"
        )
        if not cities_file.exists():
            return []
        
        with open(cities_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached data (useful for testing)."""
        cls.load_countries.cache_clear()
        cls.load_country_metadata.cache_clear()
        cls.load_states.cache_clear()
        cls.load_cities.cache_clear()
```

### Step 3: Create API Functions (`countrystatecity_countries/api.py`)

```python
"""Public API functions."""

from typing import List, Optional
from .models import Country, State, City
from .loaders import DataLoader


def get_countries() -> List[Country]:
    """Get all countries (lightweight list)."""
    data = DataLoader.load_countries()
    return [Country(**country) for country in data]


def get_country_by_code(country_code: str) -> Optional[Country]:
    """Get country by ISO2 or ISO3 code."""
    country_code = country_code.upper()
    
    # Try ISO2 first
    metadata = DataLoader.load_country_metadata(country_code)
    if metadata:
        return Country(**metadata)
    
    # Try ISO3
    countries = DataLoader.load_countries()
    for country_data in countries:
        if country_data.get("iso3") == country_code:
            metadata = DataLoader.load_country_metadata(country_data["iso2"])
            if metadata:
                return Country(**metadata)
    
    return None


def get_country_by_id(country_id: int) -> Optional[Country]:
    """Get country by ID."""
    countries = DataLoader.load_countries()
    for country_data in countries:
        if country_data["id"] == country_id:
            return Country(**country_data)
    return None


def search_countries(query: str) -> List[Country]:
    """Search countries by name."""
    query = query.lower()
    countries = DataLoader.load_countries()
    results = [
        Country(**country)
        for country in countries
        if query in country["name"].lower()
    ]
    return results


def get_states_of_country(country_code: str) -> List[State]:
    """Get all states in a country (lazy loaded)."""
    country_code = country_code.upper()
    data = DataLoader.load_states(country_code)
    return [State(**state) for state in data]


def get_state_by_code(country_code: str, state_code: str) -> Optional[State]:
    """Get specific state."""
    states = get_states_of_country(country_code)
    for state in states:
        if state.state_code == state_code:
            return state
    return None


def get_cities_of_state(country_code: str, state_code: str) -> List[City]:
    """Get all cities in a state (lazy loaded)."""
    country_code = country_code.upper()
    state_code = state_code.upper()
    data = DataLoader.load_cities(country_code, state_code)
    return [City(**city) for city in data]


def get_cities_of_country(country_code: str) -> List[City]:
    """Get all cities in a country (warning: may be large)."""
    country_code = country_code.upper()
    states = get_states_of_country(country_code)
    
    all_cities = []
    for state in states:
        cities = get_cities_of_state(country_code, state.state_code)
        all_cities.extend(cities)
    
    return all_cities
```

### Step 4: Create Package Init (`countrystatecity_countries/__init__.py`)

```python
"""Official countries, states, and cities database."""

from .models import Country, State, City
from .api import (
    get_countries,
    get_country_by_code,
    get_country_by_id,
    search_countries,
    get_states_of_country,
    get_state_by_code,
    get_cities_of_state,
    get_cities_of_country,
)

__version__ = "1.0.0"

__all__ = [
    # Models
    "Country",
    "State",
    "City",
    # Countries API
    "get_countries",
    "get_country_by_code",
    "get_country_by_id",
    "search_countries",
    # States API
    "get_states_of_country",
    "get_state_by_code",
    # Cities API
    "get_cities_of_state",
    "get_cities_of_country",
]
```

### Step 5: Add Type Marker (`countrystatecity_countries/py.typed`)

```bash
# Create empty py.typed file for PEP 561 compliance
touch countrystatecity_countries/py.typed
```

---

## 🧪 Phase 3: Testing (Day 4)

### Create Test File (`tests/test_countries.py`)

```python
"""Tests for countries API."""

import pytest
from countrystatecity_countries import (
    get_countries,
    get_country_by_code,
    get_country_by_id,
    search_countries,
    Country,
)


def test_get_countries():
    """Test getting all countries."""
    countries = get_countries()
    assert len(countries) >= 250
    assert all(isinstance(c, Country) for c in countries)
    assert all(c.iso2 for c in countries)
    assert all(c.name for c in countries)


def test_get_country_by_code_iso2():
    """Test getting country by ISO2 code."""
    usa = get_country_by_code("US")
    assert usa is not None
    assert usa.name == "United States"
    assert usa.iso2 == "US"
    assert usa.iso3 == "USA"
    assert usa.capital == "Washington"


def test_get_country_by_code_iso3():
    """Test getting country by ISO3 code."""
    usa = get_country_by_code("USA")
    assert usa is not None
    assert usa.name == "United States"


def test_get_country_by_code_not_found():
    """Test getting non-existent country."""
    country = get_country_by_code("XX")
    assert country is None


def test_search_countries():
    """Test searching countries."""
    results = search_countries("united")
    assert len(results) >= 2
    names = [c.name for c in results]
    assert "United States" in names
    assert "United Kingdom" in names


def test_country_immutability():
    """Test that Country objects are immutable."""
    usa = get_country_by_code("US")
    with pytest.raises(Exception):
        usa.name = "Changed"


def test_country_fields():
    """Test country has expected fields."""
    usa = get_country_by_code("US")
    assert hasattr(usa, 'id')
    assert hasattr(usa, 'name')
    assert hasattr(usa, 'iso2')
    assert hasattr(usa, 'iso3')
    assert hasattr(usa, 'phone_code')
```

### Run Tests

```bash
poetry run pytest -v
poetry run pytest --cov=countrystatecity_countries --cov-report=html
```

---

## 📊 Phase 4: Data Generation (Day 5)

### Create Data Generation Script (`scripts/generate_data.py`)

```python
"""Generate JSON data from MySQL database."""

import json
import mysql.connector
from pathlib import Path
from typing import List, Dict, Any


def connect_to_db():
    """Connect to MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="world"
    )


def generate_countries_list(cursor) -> List[Dict[str, Any]]:
    """Generate lightweight countries list."""
    cursor.execute("""
        SELECT 
            id, name, iso2, iso3, numeric_code, phone_code,
            capital, currency, currency_name, currency_symbol,
            tld, native, region, subregion,
            latitude, longitude, emoji, emojiU
        FROM countries
        ORDER BY name
    """)
    
    columns = [
        'id', 'name', 'iso2', 'iso3', 'numeric_code', 'phone_code',
        'capital', 'currency', 'currency_name', 'currency_symbol',
        'tld', 'native', 'region', 'subregion',
        'latitude', 'longitude', 'emoji', 'emojiU'
    ]
    
    countries = []
    for row in cursor.fetchall():
        country = dict(zip(columns, row))
        countries.append(country)
    
    return countries


def main():
    """Generate all data files."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Generate countries list
    print("Generating countries list...")
    countries = generate_countries_list(cursor)
    
    # Create output directory
    output_dir = Path("../countrystatecity_countries/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write countries.json
    with open(output_dir / "countries.json", "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Generated {len(countries)} countries")
    
    # TODO: Generate per-country data structure
    # TODO: Generate states and cities
    
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
```

---

## 📦 Phase 5: Package Configuration (Day 6)

### Create `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "countrystatecity-countries"
version = "1.0.0"
description = "Official countries, states, and cities database with type hints and lazy loading"
readme = "README.md"
authors = [
    {name = "dr5hn", email = "your.email@example.com"}
]
license = {text = "ODbL-1.0"}
keywords = [
    "countries", "states", "cities", "geography", "geolocation",
    "timezone", "translations", "iso", "lazy-loading", "type-hints"
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed"
]
requires-python = ">=3.8"
dependencies = [
    "pydantic>=2.0.0,<3.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "mypy>=1.0.0",
    "black>=23.0.0",
    "isort>=5.0.0",
    "ruff>=0.1.0"
]

[project.urls]
Homepage = "https://github.com/dr5hn/countries-states-cities-database"
Repository = "https://github.com/dr5hn/countries-states-cities-database"
Issues = "https://github.com/dr5hn/countries-states-cities-database/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["countrystatecity_countries*"]

[tool.setuptools.package-data]
countrystatecity_countries = ["data/**/*.json", "py.typed"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=countrystatecity_countries"

[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
```

---

## 🚀 Phase 6: Build and Test (Day 7)

### Build Package

```bash
# Format code
poetry run black countrystatecity_countries/ tests/
poetry run isort countrystatecity_countries/ tests/

# Type check
poetry run mypy countrystatecity_countries/

# Run tests
poetry run pytest

# Build package
poetry build
```

### Test Installation

```bash
# Install locally
pip install dist/countrystatecity_countries-1.0.0-py3-none-any.whl

# Test in Python
python3 -c "
from countrystatecity_countries import get_countries
countries = get_countries()
print(f'✓ Loaded {len(countries)} countries')
"
```

---

## 📤 Phase 7: Publish (Day 8)

### Publish to TestPyPI

```bash
# Configure Poetry for TestPyPI
poetry config repositories.testpypi https://test.pypi.org/legacy/

# Publish to TestPyPI
poetry publish -r testpypi --username __token__ --password YOUR_TESTPYPI_TOKEN

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ countrystatecity-countries
```

### Publish to PyPI

```bash
# Publish to PyPI
poetry publish --username __token__ --password YOUR_PYPI_TOKEN
```

---

## ✅ Checklist

### Pre-Launch
- [ ] All tests passing (80%+ coverage)
- [ ] Type checking with mypy (strict mode)
- [ ] Code formatted with black and isort
- [ ] README.md written with examples
- [ ] CHANGELOG.md created
- [ ] LICENSE file included
- [ ] Data files generated and validated
- [ ] Package built successfully
- [ ] Tested on Python 3.8, 3.9, 3.10, 3.11, 3.12

### Launch
- [ ] Published to TestPyPI
- [ ] Tested installation from TestPyPI
- [ ] Published to PyPI
- [ ] GitHub release created
- [ ] Announcement posted

### Post-Launch
- [ ] Monitor PyPI downloads
- [ ] Respond to issues
- [ ] Collect feedback
- [ ] Plan next package

---

## 🎯 Next Steps

After launching `countrystatecity-countries`:

1. **Week 2-3:** Implement `countrystatecity-timezones`
2. **Week 4-5:** Implement `countrystatecity-currencies`
3. **Week 6-7:** Implement `countrystatecity-languages`
4. **Week 8:** Implement `countrystatecity-phonecodes`

---

## 💡 Tips

1. **Start Small:** Focus on countries package first
2. **Test Early:** Write tests alongside code
3. **Use Type Hints:** Leverage Pydantic for validation
4. **Cache Aggressively:** Use LRU cache for performance
5. **Document Well:** Clear docstrings and README
6. **Version Carefully:** Follow semantic versioning
7. **Monitor Usage:** Track downloads and issues

---

## 🆘 Troubleshooting

### Poetry Installation Issues
```bash
# If Poetry not in PATH
export PATH="$HOME/.local/bin:$PATH"
```

### MySQL Connection Issues
```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM countries;"
```

### Import Errors
```bash
# Ensure package is installed in editable mode
poetry install
```

---

**Ready to start? Begin with Phase 1! 🚀**
