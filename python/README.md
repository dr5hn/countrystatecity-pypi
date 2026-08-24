# Python Packages for Countries States Cities Database

This directory contains official Python packages for the [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) project.

## 📦 Available Packages

### Official API client

| Package | PyPI | Description |
|---|---|---|
| **[countrystatecity-api](./packages/api/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-api)](https://pypi.org/project/countrystatecity-api/) | Official client for the Country State City API — sync + async, typed, structured errors |

### Offline data packages

| Package | PyPI | Description |
|---|---|---|
| **[countrystatecity-countries](./packages/countries/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-countries)](https://pypi.org/project/countrystatecity-countries/) | 250 countries, 5,308 states, 171,938 cities |
| **[countrystatecity-timezones](./packages/timezones/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-timezones)](https://pypi.org/project/countrystatecity-timezones/) | 432 IANA timezones with time conversion |
| **[countrystatecity-currencies](./packages/currencies/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-currencies)](https://pypi.org/project/countrystatecity-currencies/) | 249 country/currency associations |
| **[countrystatecity-translations](./packages/translations/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/) | 4,724 translations in 19 languages |
| **[countrystatecity-phonecodes](./packages/phonecodes/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-phonecodes)](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes |
| **[countrystatecity-regions](./packages/regions/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-regions)](https://pypi.org/project/countrystatecity-regions/) | Continents and geographic subregions |
| **[countrystatecity-postal-codes](./packages/postal_codes/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-postal-codes)](https://pypi.org/project/countrystatecity-postal-codes/) | Postal/ZIP codes and format validation |

## From offline prototype to production

The `countrystatecity-*` packages are versioned offline snapshots. Production
applications should use the managed API through the official `countrystatecity`
client for regularly updated data, search, filtering, smaller responses, and
support.

[Get a free API key](https://app.countrystatecity.in/?utm_source=github&utm_medium=repository&utm_campaign=python_packages) ·
[API documentation](https://docs.countrystatecity.in/api/introduction) ·
[Playground](https://playground.countrystatecity.in/) ·
[Pricing](https://countrystatecity.in/pricing/?utm_source=github&utm_medium=repository&utm_campaign=python_packages) ·
[Migration guide](../docs/MIGRATING_TO_API.md)

## 🚀 Installation

Install the API client, the offline packages you need, or both:

```bash
pip install countrystatecity-api

pip install countrystatecity-countries
pip install countrystatecity-timezones
pip install countrystatecity-currencies
pip install countrystatecity-translations
pip install countrystatecity-phonecodes
pip install countrystatecity-regions
pip install countrystatecity-postal-codes
```

## 🏗️ Structure

```
python/
└── packages/
    ├── api/            # countrystatecity-api      (API client)
    ├── countries/      # countrystatecity-countries
    ├── timezones/      # countrystatecity-timezones
    ├── currencies/     # countrystatecity-currencies
    ├── translations/   # countrystatecity-translations
    ├── phonecodes/     # countrystatecity-phonecodes
    ├── regions/        # countrystatecity-regions
    └── postal_codes/   # countrystatecity-postal-codes
```

The data packages import as `countrystatecity_<name>`. The
`countrystatecity-api` distribution imports as the bare `countrystatecity`
namespace. CI keeps that deliberate distribution/import-name difference
explicit.

## 🛠️ Development

```bash
# Install a package in dev mode (replace 'countries' with any package
# directory; use 'api' for the client)
cd packages/countries
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

For the API client, substitute the module name `countrystatecity`:

```bash
cd packages/api
pip install -e ".[dev]"
pytest --cov=countrystatecity --cov-report=term
mypy countrystatecity/ --strict
```

Its tests mock every HTTP call, so no API key is needed to run them.

## 📊 Technology Stack

| Component | Technology |
|---|---|
| Type System | Pydantic (offline packages), TypedDict (API client) |
| HTTP | httpx (API client only) |
| Testing | pytest |
| Type Checking | mypy (strict) |
| Formatting | black + isort |
| Linting | ruff |
| CI/CD | GitHub Actions |

## 📝 License

All packages are licensed under the [Open Database License (ODbL-1.0)](../LICENSE).

## 🤝 Contributing

Contributions are welcome! Please see the [Contributing Guidelines](../CONTRIBUTING.md).

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/dr5hn/countrystatecity-pypi/issues)
- **Website**: [countrystatecity.in](https://countrystatecity.in)
- **Production API**: [Get a free API key](https://app.countrystatecity.in/?utm_source=github&utm_medium=repository&utm_campaign=python_packages)

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
