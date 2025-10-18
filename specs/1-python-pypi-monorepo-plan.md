# Python PyPI Package Ecosystem - Complete Specifications

**Document Purpose:** Comprehensive specifications for building the Python PyPI package ecosystem mirroring the npm @countrystatecity packages, adapted for Python best practices and the existing countries-states-cities-database repository.

---

## 📋 Executive Summary

### **Business Context**
- **Existing Assets:** 
  - Popular API at countrystatecity.in
  - MySQL database with 250+ countries, 5000+ states, 151K+ cities
  - Successful npm packages (@countrystatecity/*)
  - PHP export tooling
- **Problem:** No official Python package, developers using outdated/incomplete alternatives
- **Solution:** Build official Python package ecosystem with lazy loading, type hints, and seamless integration

### **Technical Approach**
- **Repository:** Extend existing countries-states-cities-database repo with Python packages
- **Package Structure:** Single monorepo with multiple PyPI packages
- **Package Naming:** `countrystatecity` namespace (e.g., `countrystatecity-countries`)
- **Architecture:** Lazy-loading, split data files, dynamic imports
- **Data Source:** Existing MySQL database and JSON exports

---

## 🏗️ Repository Architecture

### **Extended Directory Structure**

```
countries-states-cities-database/        [Existing repo]
├── bin/                                 [Existing PHP tools]
├── contributions/                       [Existing JSON source]
├── json/                                [Existing exports]
├── sql/                                 [Existing SQL dumps]
├── csv/, xml/, yml/, mongodb/, etc.    [Existing exports]
│
├── python/                              [NEW: Python packages root]
│   ├── packages/                        [All publishable PyPI packages]
│   │   ├── countries/                   [Priority 1]
│   │   │   ├── countrystatecity_countries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py           [Pydantic models]
│   │   │   │   ├── loaders.py          [Lazy data loading]
│   │   │   │   ├── api.py              [Public API functions]
│   │   │   │   ├── utils.py            [Utilities]
│   │   │   │   ├── py.typed            [PEP 561 marker]
│   │   │   │   └── data/               [JSON data - split structure]
│   │   │   │       ├── countries.json
│   │   │   │       └── by-country/
│   │   │   │           ├── US/
│   │   │   │           │   ├── meta.json
│   │   │   │           │   ├── states.json
│   │   │   │           │   └── states/
│   │   │   │           │       └── CA/
│   │   │   │           │           └── cities.json
│   │   │   │           └── IN/
│   │   │   │               └── ...
│   │   │   ├── tests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_countries.py
│   │   │   │   ├── test_states.py
│   │   │   │   ├── test_cities.py
│   │   │   │   └── test_performance.py
│   │   │   ├── scripts/
│   │   │   │   ├── generate_data.py    [Generate from MySQL]
│   │   │   │   └── validate_data.py    [Validate structure]
│   │   │   ├── pyproject.toml          [Modern Python packaging]
│   │   │   ├── README.md
│   │   │   ├── LICENSE
│   │   │   └── CHANGELOG.md
│   │   │
│   │   ├── timezones/                   [Priority 2]
│   │   ├── currencies/                  [Priority 3]
│   │   ├── languages/                   [Priority 4]
│   │   ├── phone-codes/                 [Priority 5]
│   │   ├── airports/                    [Future]
│   │   ├── postal-codes/                [Future]
│   │   ├── validate/                    [Future]
│   │   ├── format/                      [Future]
│   │   └── flask/                       [Future: Flask extension]
│   │
│   ├── shared/                          [Shared utilities - not published]
│   │   ├── __init__.py
│   │   ├── types.py                     [Common type definitions]
│   │   ├── base_loader.py              [Base data loader class]
│   │   └── validators.py               [Shared validators]
│   │
│   ├── scripts/                         [Root-level Python scripts]
│   │   ├── generate_all_data.py        [Generate data for all packages]
│   │   ├── validate_all_packages.py    [Validate all packages]
│   │   ├── sync_from_mysql.py          [Sync from MySQL]
│   │   └── publish_workflow.py         [Publishing automation]
│   │
│   ├── tests/                           [Integration tests]
│   │   └── test_integration.py
│   │
│   ├── .github/
│   │   └── workflows/
│   │       ├── python-ci.yml           [Python CI/CD]
│   │       ├── python-publish.yml      [PyPI publishing]
│   │       └── python-test.yml         [Python testing]
│   │
│   ├── pyproject.toml                   [Root project config]
│   ├── poetry.lock                      [Dependency lock file]
│   ├── requirements-dev.txt             [Dev dependencies]
│   └── README.md                        [Python packages docs]
│
└── [All existing files remain unchanged]
```

---

## 📦 Package #1: countrystatecity-countries (PRIORITY 1)

### **Package Information**
- **Package name:** `countrystatecity-countries`
- **Import name:** `countrystatecity_countries`
- **PyPI URL:** `https://pypi.org/project/countrystatecity-countries/`
- **Version:** 1.0.0
- **License:** ODbL-1.0 (same as database)
- **Python versions:** 3.8+ (with type hints)

### **Key Features**
- ✅ Type-safe with Pydantic models and mypy support
- ✅ Lazy loading for minimal memory footprint
- ✅ 250+ countries with full metadata
- ✅ 5,000+ states/provinces
- ✅ 151,000+ cities
- ✅ Translations in 18+ languages
- ✅ Timezone data per location
- ✅ Zero external dependencies (except Pydantic)
- ✅ Full test coverage with pytest

### **Installation**
```bash
pip install countrystatecity-countries
```

### **Basic Usage**
```python
from countrystatecity_countries import (
    get_countries,
    get_country_by_code,
    get_states_of_country,
    get_cities_of_state,
    search_countries
)

# Get all countries (lightweight)
countries = get_countries()
# [Country(name="United States", iso2="US", iso3="USA", ...)]

# Get specific country with full details
usa = get_country_by_code("US")
# Country(name="United States", capital="Washington", currency="USD", ...)

# Get states (lazy loaded)
states = get_states_of_country("US")
# [State(name="California", state_code="CA", ...)]

# Get cities (lazy loaded)
cities = get_cities_of_state("US", "CA")
# [City(name="Los Angeles", latitude=34.05, longitude=-118.24, ...)]

# Search
results = search_countries("united")
# [Country(name="United States", ...), Country(name="United Kingdom", ...)]
```

### **Pydantic Models**
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class Country(BaseModel):
    """Country model with full metadata"""
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
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emoji: Optional[str] = None
    emojiU: Optional[str] = None
    
    class Config:
        frozen = True  # Immutable


class State(BaseModel):
    """State/Province model"""
    id: int
    name: str
    country_id: int
    country_code: str = Field(..., min_length=2, max_length=2)
    state_code: str
    type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    
    class Config:
        frozen = True


class City(BaseModel):
    """City model"""
    id: int
    name: str
    state_id: int
    state_code: str
    country_id: int
    country_code: str = Field(..., min_length=2, max_length=2)
    latitude: float
    longitude: float
    timezone: Optional[str] = None
    wikiDataId: Optional[str] = None
    
    class Config:
        frozen = True
```

### **Complete API Reference**

#### **Countries API**
```python
def get_countries() -> List[Country]:
    """Get all countries (lightweight list)"""
    
def get_country_by_id(country_id: int) -> Optional[Country]:
    """Get country by ID"""
    
def get_country_by_code(country_code: str) -> Optional[Country]:
    """Get country by ISO2 or ISO3 code"""
    
def search_countries(query: str) -> List[Country]:
    """Search countries by name"""
    
def get_countries_by_region(region: str) -> List[Country]:
    """Get countries in a region"""
    
def get_countries_by_subregion(subregion: str) -> List[Country]:
    """Get countries in a subregion"""
```

#### **States API**
```python
def get_states_of_country(country_code: str) -> List[State]:
    """Get all states in a country (lazy loaded)"""
    
def get_state_by_code(country_code: str, state_code: str) -> Optional[State]:
    """Get specific state"""
    
def search_states(country_code: str, query: str) -> List[State]:
    """Search states within a country"""
```

#### **Cities API**
```python
def get_cities_of_state(
    country_code: str, 
    state_code: str
) -> List[City]:
    """Get all cities in a state (lazy loaded)"""
    
def get_cities_of_country(country_code: str) -> List[City]:
    """Get all cities in a country (warning: may be large)"""
    
def get_city_by_id(city_id: int) -> Optional[City]:
    """Get city by ID"""
    
def search_cities(
    country_code: str, 
    state_code: Optional[str], 
    query: str
) -> List[City]:
    """Search cities"""
    
def get_cities_near(
    latitude: float, 
    longitude: float, 
    radius_km: float = 50
) -> List[City]:
    """Get cities near coordinates"""
```

### **Data Loading Strategy**

```python
# countrystatecity_countries/loaders.py

import json
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any

class DataLoader:
    """Lazy data loader with caching"""
    
    _data_dir = Path(__file__).parent / "data"
    
    @classmethod
    @lru_cache(maxsize=1)
    def load_countries(cls) -> List[Dict[str, Any]]:
        """Load countries list (cached)"""
        with open(cls._data_dir / "countries.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    @classmethod
    @lru_cache(maxsize=250)  # Cache per country
    def load_country_metadata(cls, country_code: str) -> Dict[str, Any]:
        """Load full country metadata (cached per country)"""
        file_path = cls._data_dir / "by-country" / country_code / "meta.json"
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @classmethod
    @lru_cache(maxsize=250)
    def load_states(cls, country_code: str) -> List[Dict[str, Any]]:
        """Load states for country (cached per country)"""
        file_path = cls._data_dir / "by-country" / country_code / "states.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    @classmethod
    @lru_cache(maxsize=5000)
    def load_cities(cls, country_code: str, state_code: str) -> List[Dict[str, Any]]:
        """Load cities for state (cached per state)"""
        file_path = (
            cls._data_dir / "by-country" / country_code / 
            "states" / state_code / "cities.json"
        )
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
```

### **pyproject.toml**
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
    "countries",
    "states",
    "cities",
    "geography",
    "geolocation",
    "timezone",
    "translations",
    "iso",
    "lazy-loading",
    "type-hints"
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Open Database License (ODbL)",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
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
Documentation = "https://github.com/dr5hn/countries-states-cities-database/tree/master/python/packages/countries"
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
addopts = "-v --cov=countrystatecity_countries --cov-report=term-missing"

[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.black]
line-length = 88
target-version = ["py38"]

[tool.isort]
profile = "black"
line_length = 88

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP"]
```

---

## 📦 Additional Packages (Future)

### **2. countrystatecity-timezones**
```python
from countrystatecity_timezones import get_timezones_by_country, convert_time

us_tz = get_timezones_by_country("US")
converted = convert_time(datetime.now(), "America/New_York", "Asia/Kolkata")
```

### **3. countrystatecity-currencies**
```python
from countrystatecity_currencies import get_currency_by_code, format_currency

usd = get_currency_by_code("USD")
formatted = format_currency(1234.56, "USD", "en_US")  # "$1,234.56"
```

### **4. countrystatecity-languages**
```python
from countrystatecity_languages import get_languages_by_country, is_rtl

langs = get_languages_by_country("IN")
is_rtl("ar")  # True
```

### **5. countrystatecity-phonecodes**
```python
from countrystatecity_phonecodes import validate_phone, format_phone

is_valid = validate_phone("+1234567890", "US")
formatted = format_phone("2345678900", "US")  # "(234) 567-8900"
```

---

## 🔧 Development Tooling

### **Package Manager: Poetry (Recommended)**

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Initialize new package
cd python/packages/countries
poetry init

# Add dependencies
poetry add pydantic

# Add dev dependencies
poetry add --group dev pytest pytest-cov mypy black isort

# Install
poetry install

# Run tests
poetry run pytest

# Build package
poetry build

# Publish to PyPI
poetry publish
```

### **Testing: pytest**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=countrystatecity_countries --cov-report=html

# Run specific test
pytest tests/test_countries.py::test_get_countries

# Run performance tests
pytest tests/test_performance.py -v
```

---

## 🚀 CI/CD with GitHub Actions

```yaml
# .github/workflows/python-ci.yml

name: Python CI

on:
  push:
    branches: [main, master]
    paths:
      - 'python/**'
  pull_request:
    paths:
      - 'python/**'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      
      - name: Install dependencies
        working-directory: python/packages/countries
        run: |
          poetry install
      
      - name: Run tests
        working-directory: python/packages/countries
        run: |
          poetry run pytest --cov --cov-report=xml
      
      - name: Type check
        working-directory: python/packages/countries
        run: |
          poetry run mypy countrystatecity_countries/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./python/packages/countries/coverage.xml
```

---

## 🎯 Implementation Roadmap

### **Phase 1: Foundation (Weeks 1-4)**

**Week 1: Setup**
- [ ] Create `python/` directory structure
- [ ] Set up Poetry for package management
- [ ] Create shared types and base classes
- [ ] Set up GitHub Actions for Python CI
- [ ] Create pyproject.toml templates

**Week 2: Data Generation**
- [ ] Write MySQL → JSON export script for Python structure
- [ ] Generate countries.json (lightweight)
- [ ] Generate per-country data structure
- [ ] Generate states and cities split files
- [ ] Validate data integrity

**Week 3: Core Package Implementation**
- [ ] Implement Pydantic models
- [ ] Implement lazy data loader
- [ ] Implement API functions (countries, states, cities)
- [ ] Write comprehensive tests (80%+ coverage)
- [ ] Add type hints and mypy checks

**Week 4: Testing & Documentation**
- [ ] Performance testing
- [ ] Memory profiling
- [ ] Write README.md
- [ ] Create usage examples
- [ ] Set up automated tests

### **Phase 2: First Release (Week 5)**

- [ ] Final testing on Python 3.8-3.12
- [ ] Build wheel and sdist
- [ ] Publish to TestPyPI
- [ ] Test installation from TestPyPI
- [ ] Publish to PyPI
- [ ] Create GitHub release
- [ ] Announce on social media

---

## 📊 Success Metrics

### **Package Health**
- PyPI downloads per week
- GitHub stars on main repo
- Issue response time
- Test coverage (target: 80%+)
- Type coverage (target: 100%)

### **Quality Metrics**
- Load time < 50ms
- Memory footprint < 10MB (base)
- mypy strict mode passing
- Zero critical bugs
- Documentation completeness

---

## 🔗 Integration with Existing Repository

### **Data Sync Workflow**

```bash
# 1. Update contributions/ JSON files
vim contributions/cities/US.json

# 2. Import to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py

# 3. Generate all exports (PHP)
cd bin
php console export:json

# 4. Generate Python data structure
cd ../python/scripts
python3 generate_all_data.py

# 5. Test Python packages
cd ../packages/countries
poetry run pytest

# 6. Commit all changes
git add .
git commit -m "feat: add new cities to US database"
```

---

## 🆚 Comparison: Python vs JavaScript

| Aspect | JavaScript | Python |
|--------|-----------|--------|
| Type System | TypeScript interfaces | Pydantic models |
| Package Manager | pnpm | Poetry |
| Data Validation | Runtime checks | Pydantic validation |
| Testing | Vitest | pytest |
| Type Checking | tsc | mypy |
| Lazy Loading | Dynamic imports | LRU cache |
| Publishing | npm | PyPI |

---

## 📝 Example Integration

### **Flask Application**
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

### **Django Integration**
```python
from countrystatecity_countries import get_countries

def get_country_choices():
    """Generate choices for Django ChoiceField"""
    countries = get_countries()
    return [(c.iso2, c.name) for c in countries]
```

---

## 🎉 Summary

This plan provides a complete blueprint for creating a professional Python PyPI package ecosystem that:

1. **Mirrors npm structure** - Same API, adapted for Python
2. **Leverages existing database** - No duplicate data maintenance
3. **Follows Python best practices** - Type hints, Pydantic, Poetry
4. **Integrates with existing repo** - Single source of truth
5. **Provides excellent DX** - Easy to use, well-documented
6. **Scales to multiple packages** - Clear path for timezones, currencies, etc.

**Estimated Timeline:** 4-6 weeks for first package, 3-4 months for complete ecosystem.
