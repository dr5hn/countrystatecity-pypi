# Country State City PyPI Packages

Official Python packages for accessing comprehensive countries, states, cities, timezones, currencies, and translations data with type hints and lazy loading.

[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-countries)](https://pypi.org/project/countrystatecity-countries/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![CI](https://github.com/dr5hn/countrystatecity-pypi/actions/workflows/python-ci.yml/badge.svg)](https://github.com/dr5hn/countrystatecity-pypi/actions/workflows/python-ci.yml)

[![countrystatecity-countries Downloads](https://img.shields.io/pypi/dt/countrystatecity-countries?label=countrystatecity-countries)](https://pypi.org/project/countrystatecity-countries/)
[![countrystatecity-timezones Downloads](https://img.shields.io/pypi/dt/countrystatecity-timezones?label=countrystatecity-timezones)](https://pypi.org/project/countrystatecity-timezones/)
[![countrystatecity-currencies Downloads](https://img.shields.io/pypi/dt/countrystatecity-currencies?label=countrystatecity-currencies)](https://pypi.org/project/countrystatecity-currencies/)
[![countrystatecity-translations Downloads](https://img.shields.io/pypi/dt/countrystatecity-translations?label=countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/)
[![countrystatecity-phonecodes Downloads](https://img.shields.io/pypi/dt/countrystatecity-phonecodes?label=countrystatecity-phonecodes)](https://pypi.org/project/countrystatecity-phonecodes/)

## 📦 Available Packages

| Package | PyPI | Description |
|---|---|---|
| **[countrystatecity-countries](./python/packages/countries/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-countries)](https://pypi.org/project/countrystatecity-countries/) | Countries, states, and cities with full metadata |
| **[countrystatecity-timezones](./python/packages/timezones/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-timezones)](https://pypi.org/project/countrystatecity-timezones/) | IANA timezone data and time conversion utilities |
| **[countrystatecity-currencies](./python/packages/currencies/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-currencies)](https://pypi.org/project/countrystatecity-currencies/) | Currency codes, names, and symbols |
| **[countrystatecity-translations](./python/packages/translations/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/) | Country name translations in 18+ languages |
| **[countrystatecity-phonecodes](./python/packages/phonecodes/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-phonecodes)](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250+ countries |

> **Note:** There is no bare `countrystatecity` package on PyPI. Always install with the suffix (`-countries`, `-timezones`, `-currencies`, `-translations`, `-phonecodes`).

## 🚀 Installation

Install only what you need:

```bash
pip install countrystatecity-countries
pip install countrystatecity-timezones
pip install countrystatecity-currencies
pip install countrystatecity-translations
pip install countrystatecity-phonecodes
```

## 📖 Usage

### Countries

```python
from countrystatecity_countries import (
    get_countries,
    get_country_by_code,
    get_states_of_country,
    get_cities_of_state,
)

# All countries
countries = get_countries()
print(f"Total countries: {len(countries)}")

# Specific country
usa = get_country_by_code("US")
print(f"{usa.emoji} {usa.name} — {usa.capital}")
print(f"Currency: {usa.currency_symbol} {usa.currency_name}")

# States and cities (lazy loaded)
states = get_states_of_country("US")
cities = get_cities_of_state("US", "CA")
```

### Timezones

```python
from countrystatecity_timezones import (
    get_all_timezones,
    get_timezones_by_country,
    get_timezone_by_zone_name,
    get_timezones_by_offset,
    convert_time,
)

# Timezones for a country
timezones = get_timezones_by_country("US")

# Lookup by zone name
tz = get_timezone_by_zone_name("America/New_York")
print(f"{tz.zone_name} — {tz.gmt_offset_name}")

# Convert time between zones
from datetime import datetime
dt = datetime(2024, 1, 1, 12, 0, 0)
converted = convert_time(dt, "America/New_York", "Asia/Kolkata")
```

### Currencies

```python
from countrystatecity_currencies import (
    get_all_currencies,
    get_currency_by_country,
    get_countries_by_currency,
    search_currencies,
)

# Currency for a country
currency = get_currency_by_country("US")
print(f"{currency.symbol} {currency.name} ({currency.code})")

# All countries using a currency
countries = get_countries_by_currency("EUR")

# Search
results = search_currencies("dollar")
```

### Phone Codes

```python
from countrystatecity_phonecodes import (
    get_all_phonecodes,
    get_phonecode_by_country,
    get_countries_by_phonecode,
    search_phonecodes,
)

# Phone code for a country
us = get_phonecode_by_country("US")
print(f"+{us.phoneCode} — {us.countryName}")  # +1 — United States

# All countries sharing a dialing code
plus1 = get_countries_by_phonecode("1")
print(f"{len(plus1)} countries use +1")

# Works with or without + prefix
plus44 = get_countries_by_phonecode("+44")

# Search
results = search_phonecodes("united")
```

### Translations

```python
from countrystatecity_translations import (
    get_all_translations,
    get_translations_by_country,
    get_translations_by_language,
    get_translation,
    search_translations,
)

# Country name in a specific language
translation = get_translation("US", "fr")
print(translation.name)  # États-Unis

# All translations for a country
translations = get_translations_by_country("IN")

# All countries translated in Japanese
japanese = get_translations_by_language("ja")
```

## ✨ Features

- ✅ **Type-safe** with Pydantic models and mypy strict mode
- ✅ **Lazy loading** for minimal memory footprint
- ✅ **250+ countries** with full metadata
- ✅ **5,000+ states/provinces**
- ✅ **150,000+ cities**
- ✅ **400+ timezones** with GMT offsets and time conversion
- ✅ **Currency data** for every country
- ✅ **Translations** in 18+ languages
- ✅ **Phone/dialing codes** for 250+ countries
- ✅ **Zero external dependencies** (except Pydantic)
- ✅ **Python 3.8–3.12** support
- ✅ **Full test coverage** with pytest

## 🏗️ Repository Structure

```
countrystatecity-pypi/
├── python/
│   └── packages/
│       ├── countries/     # countrystatecity-countries
│       ├── timezones/     # countrystatecity-timezones
│       ├── currencies/    # countrystatecity-currencies
│       ├── translations/  # countrystatecity-translations
│       └── phonecodes/    # countrystatecity-phonecodes
│
└── .github/
    └── workflows/
        ├── python-ci.yml    # CI — tests, type check, lint
        ├── publish.yml      # Publish to PyPI
        ├── release.yml      # Version bump + changelog
        └── update-data.yml  # Weekly data sync
```

## 🛠️ Development

```bash
git clone https://github.com/dr5hn/countrystatecity-pypi.git

# Install a package in dev mode (replace 'countries' with any package)
cd python/packages/countries
pip install -e ".[dev]"

# Run tests
pytest --cov=countrystatecity_countries --cov-report=html

# Type check
mypy countrystatecity_countries/ --strict

# Lint and format
ruff check countrystatecity_countries/ tests/
black countrystatecity_countries/ tests/
isort countrystatecity_countries/ tests/
```

## 📊 Technology Stack

| Component | Technology |
|---|---|
| Type System | Pydantic |
| Testing | pytest |
| Type Checking | mypy (strict) |
| Formatting | black + isort |
| Linting | ruff |
| CI/CD | GitHub Actions |

## 📝 License

All packages are licensed under the [Open Database License (ODbL-1.0)](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Open a Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/dr5hn/countrystatecity-pypi/issues)
- **Website**: [countrystatecity.in](https://countrystatecity.in)

## 🔗 Related Projects

- [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) — Source database
- [countrystatecity NPM](https://github.com/dr5hn/countrystatecity-npm) — JavaScript/TypeScript packages

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
