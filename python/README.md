# Python Packages for Countries States Cities Database

This directory contains official Python packages for the countries-states-cities-database project.

## 📦 Available Packages

### Priority 1 (Released)
- **[countrystatecity-countries](./packages/countries/)** - Countries, states, and cities database with type hints and lazy loading

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
from countrystatecity_countries import get_countries, get_country_by_code

# Get all countries
countries = get_countries()

# Get specific country
usa = get_country_by_code("US")
print(f"{usa.emoji} {usa.name}")
```

## 🏗️ Repository Structure

```
python/
├── packages/
│   ├── countries/           # Priority 1: Core package
│   ├── timezones/           # Priority 2 (planned)
│   ├── currencies/          # Priority 3 (planned)
│   ├── languages/           # Priority 4 (planned)
│   └── phone-codes/         # Priority 5 (planned)
├── shared/                  # Shared utilities
├── scripts/                 # Build scripts
└── README.md               # This file
```

## 📖 Documentation

For detailed documentation, please refer to the [specifications folder](../specs/):

- [Python PyPI Monorepo Plan](../specs/1-python-pypi-monorepo-plan.md)
- [Python vs NPM Comparison](../specs/2-python-vs-npm-comparison.md)
- [Python Quick Start Guide](../specs/3-python-quick-start-guide.md)

## 🛠️ Development

### Setup

```bash
# Navigate to a package
cd packages/countries

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=countrystatecity_countries --cov-report=html
```

### Type Checking

```bash
mypy countrystatecity_countries/
```

### Code Formatting

```bash
black countrystatecity_countries/ tests/
isort countrystatecity_countries/ tests/
ruff countrystatecity_countries/ tests/
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
| **Data Format** | JSON | Lazy-loadable data files |

## 🎯 Design Principles

1. **Type Safety** - Full type hints with Pydantic models
2. **Performance** - Lazy loading with LRU cache
3. **Minimal Dependencies** - Only essential dependencies
4. **Python Best Practices** - PEP 8 compliant, well-tested
5. **Developer Experience** - Clear APIs, comprehensive docs

## 📝 License

All packages are licensed under the [Open Database License (ODbL-1.0)](../LICENSE).

## 🤝 Contributing

Contributions are welcome! Please see the [Contributing Guidelines](../CONTRIBUTING.md).

## 📞 Support

- **Documentation**: [GitHub Repository](https://github.com/dr5hn/countrystatecity-pypi)
- **Issues**: [GitHub Issues](https://github.com/dr5hn/countrystatecity-pypi/issues)
- **Website**: [countrystatecity.in](https://countrystatecity.in)

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
