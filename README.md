# Country State City PyPI Packages

Official Python packages for accessing comprehensive countries, states, and cities database with type hints and lazy loading.

[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-countries)](https://pypi.org/project/countrystatecity-countries/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)

## 📦 Available Packages

### Priority 1 (Released)
- **[countrystatecity-countries](./python/packages/countries/)** - Countries, states, and cities database with type hints and lazy loading

### Coming Soon
- **countrystatecity-timezones** - IANA timezone data and utilities
- **countrystatecity-currencies** - Currency codes, symbols, and formatting
- **countrystatecity-languages** - Language codes and metadata
- **countrystatecity-phonecodes** - International dialing codes and validation

## 🚀 Quick Start

### Installation

```bash
pip install countrystatecity-countries
```

### Usage

```python
from countrystatecity_countries import (
    get_countries,
    get_country_by_code,
    get_states_of_country,
    get_cities_of_state,
)

# Get all countries
countries = get_countries()
print(f"Total countries: {len(countries)}")

# Get specific country
usa = get_country_by_code("US")
print(f"{usa.emoji} {usa.name}")
print(f"Capital: {usa.capital}")
print(f"Currency: {usa.currency_symbol} {usa.currency_name}")

# Get states (lazy loaded)
states = get_states_of_country("US")
print(f"Total states: {len(states)}")

# Get cities (lazy loaded)
cities = get_cities_of_state("US", "CA")
print(f"Cities in California: {len(cities)}")
```

## ✨ Features

- ✅ **Type-safe** with Pydantic models and mypy support
- ✅ **Lazy loading** for minimal memory footprint
- ✅ **250+ countries** with full metadata
- ✅ **5,000+ states/provinces**
- ✅ **151,000+ cities**
- ✅ **Translations** in 18+ languages
- ✅ **Timezone data** per location
- ✅ **Zero external dependencies** (except Pydantic)
- ✅ **Full test coverage** with pytest

## 📖 Documentation

For detailed documentation, please refer to:

- [Python Packages Overview](./python/README.md)
- [countrystatecity-countries Package](./python/packages/countries/README.md)
- [Specifications](./specs/README.md)

## 🏗️ Repository Structure

```
countrystatecity-pypi/
├── python/                        # Python packages root
│   ├── packages/
│   │   └── countries/             # Priority 1: Core package
│   ├── shared/                    # Shared utilities
│   ├── scripts/                   # Build scripts
│   └── README.md
│
├── specs/                         # Specifications
│   ├── README.md
│   ├── 1-python-pypi-monorepo-plan.md
│   ├── 2-python-vs-npm-comparison.md
│   └── 3-python-quick-start-guide.md
│
└── .github/
    └── workflows/
        └── python-ci.yml          # CI/CD workflow
```

## 🛠️ Development

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

# Type checking
mypy countrystatecity_countries/ --strict

# Linting
ruff check countrystatecity_countries/ tests/

# Formatting
black countrystatecity_countries/ tests/
isort countrystatecity_countries/ tests/
```

## 📊 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Package Manager** | pip/setuptools | Dependency management |
| **Type System** | Pydantic | Data validation, immutable models |
| **Testing** | pytest | Unit and integration tests |
| **Type Checking** | mypy | Static type checking |
| **Formatting** | black + isort | Code formatting |
| **Linting** | ruff | Fast Python linter |
| **CI/CD** | GitHub Actions | Automated testing |

## 🎯 Design Principles

1. **Type Safety** - Full type hints with Pydantic models
2. **Performance** - Lazy loading with LRU cache
3. **Minimal Dependencies** - Only essential dependencies
4. **Python Best Practices** - PEP 8 compliant, well-tested
5. **Developer Experience** - Clear APIs, comprehensive docs

## 📝 License

All packages are licensed under the [Open Database License (ODbL-1.0)](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📞 Support

- **Documentation**: [GitHub Repository](https://github.com/dr5hn/countrystatecity-pypi)
- **Issues**: [GitHub Issues](https://github.com/dr5hn/countrystatecity-pypi/issues)
- **Website**: [countrystatecity.in](https://countrystatecity.in)

## 🔗 Related Projects

- [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) - The source database (MySQL)
- [countrystatecity NPM packages](https://github.com/dr5hn/countrystatecity) - JavaScript/TypeScript packages

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
