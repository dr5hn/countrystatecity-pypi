# Country State City PyPI Packages

Official Python packages for Country State City data: a live API client for
production, and versioned offline snapshots for development and repeatable
builds. All of them are type-hinted and checked under `mypy --strict`.

[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-countries)](https://pypi.org/project/countrystatecity-countries/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![CI](https://github.com/dr5hn/countrystatecity-pypi/actions/workflows/python-ci.yml/badge.svg)](https://github.com/dr5hn/countrystatecity-pypi/actions/workflows/python-ci.yml)

[![countries](https://static.pepy.tech/personalized-badge/countrystatecity-countries?period=total&units=international_system&left_color=grey&right_color=blue&left_text=countries)](https://pepy.tech/project/countrystatecity-countries)
[![timezones](https://static.pepy.tech/personalized-badge/countrystatecity-timezones?period=total&units=international_system&left_color=grey&right_color=blue&left_text=timezones)](https://pepy.tech/project/countrystatecity-timezones)
[![currencies](https://static.pepy.tech/personalized-badge/countrystatecity-currencies?period=total&units=international_system&left_color=grey&right_color=blue&left_text=currencies)](https://pepy.tech/project/countrystatecity-currencies)
[![translations](https://static.pepy.tech/personalized-badge/countrystatecity-translations?period=total&units=international_system&left_color=grey&right_color=blue&left_text=translations)](https://pepy.tech/project/countrystatecity-translations)
[![phonecodes](https://static.pepy.tech/personalized-badge/countrystatecity-phonecodes?period=total&units=international_system&left_color=grey&right_color=blue&left_text=phonecodes)](https://pepy.tech/project/countrystatecity-phonecodes)
[![regions](https://static.pepy.tech/personalized-badge/countrystatecity-regions?period=total&units=international_system&left_color=grey&right_color=blue&left_text=regions)](https://pepy.tech/project/countrystatecity-regions)
[![postal-codes](https://static.pepy.tech/personalized-badge/countrystatecity-postal-codes?period=total&units=international_system&left_color=grey&right_color=blue&left_text=postal-codes)](https://pepy.tech/project/countrystatecity-postal-codes)

## 📦 Available Packages

### Official API client — the production path

| Package | PyPI | Description |
|---|---|---|
| **[countrystatecity](./python/packages/api/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity)](https://pypi.org/project/countrystatecity/) | Official client for the Country State City API — sync + async, typed, structured errors |

```bash
pip install countrystatecity
export CSC_API_KEY="your-api-key"   # free key: https://app.countrystatecity.in/
```

```python
from countrystatecity import CountryStateCity

csc = CountryStateCity()
india = csc.get_country("IN")
states = csc.get_states_of_country("IN")
```

Use this when you need data that is current rather than pinned, server-side
search and filtering, field-selected responses, fuzzy matching, managed
availability, or support.

### Offline data packages — versioned snapshots

No network, no key, no quota. Best for development, tests, air-gapped builds,
and anything that must be reproducible.

| Package | PyPI | Description |
|---|---|---|
| **[countrystatecity-countries](./python/packages/countries/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-countries)](https://pypi.org/project/countrystatecity-countries/) | 250 countries, 5,308 states, and 171,938 cities |
| **[countrystatecity-timezones](./python/packages/timezones/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-timezones)](https://pypi.org/project/countrystatecity-timezones/) | 432 IANA timezones and time conversion utilities |
| **[countrystatecity-currencies](./python/packages/currencies/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-currencies)](https://pypi.org/project/countrystatecity-currencies/) | 249 country/currency associations |
| **[countrystatecity-translations](./python/packages/translations/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/) | 4,724 country-name translations in 19 languages |
| **[countrystatecity-phonecodes](./python/packages/phonecodes/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-phonecodes)](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250 countries |
| **[countrystatecity-regions](./python/packages/regions/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-regions)](https://pypi.org/project/countrystatecity-regions/) | Region and subregion associations for 250 countries |
| **[countrystatecity-postal-codes](./python/packages/postal_codes/)** | [![PyPI](https://img.shields.io/pypi/v/countrystatecity-postal-codes)](https://pypi.org/project/countrystatecity-postal-codes/) | Postal/ZIP records for 125 countries |

> **Note:** The bare `countrystatecity` package is the API client. The offline
> data packages always carry a suffix (`-countries`, `-timezones`, `-currencies`,
> `-translations`, `-phonecodes`, `-regions`, `-postal-codes`).

## From offline prototype to production

The offline packages are versioned snapshots: the data they carry is frozen at
release time. Production applications that need regularly updated data,
server-side search and filtering, field-selected responses, or managed
availability and support should use the Country State City API through the
official `countrystatecity` client.

[Get a free API key](https://app.countrystatecity.in/?utm_source=github&utm_medium=repository&utm_campaign=python_packages) ·
[Read the API docs](https://docs.countrystatecity.in/api/introduction) ·
[Try the playground](https://playground.countrystatecity.in/) ·
[Compare plans](https://countrystatecity.in/pricing/?utm_source=github&utm_medium=repository&utm_campaign=python_packages) ·
[Migration guide](./docs/MIGRATING_TO_API.md)

API keys must stay in server-side environment variables, never in browser code or
source control. The client sends the key only in the `X-CSCAPI-KEY` header and
keeps it out of URLs, `repr()`, and exception messages.

## 🚀 Installation

Install the API client, the offline packages you need, or both:

```bash
pip install countrystatecity

pip install countrystatecity-countries
pip install countrystatecity-timezones
pip install countrystatecity-currencies
pip install countrystatecity-translations
pip install countrystatecity-phonecodes
pip install countrystatecity-regions
pip install countrystatecity-postal-codes
```

## 📖 Usage

### API client (`countrystatecity`)

```python
from countrystatecity import CountryStateCity, RateLimitError

csc = CountryStateCity()          # reads CSC_API_KEY

# Traversal
india = csc.get_country("IN")
states = csc.get_states_of_country("IN")
cities = csc.get_cities_of_state("IN", "MH")

# Paid-plan query features
filtered_cities = csc.get_cities_of_state("IN", "MH", q="pune")
compact = csc.get_countries(fields=["id", "name", "iso2", "emoji"])
biggest = csc.get_countries(sort="population:desc")
hits = csc.fuzzy_search("bangalor", entity="city", country="IN")

# Lookups
csc.get_timezone_of_country("IN")
csc.get_currency_of_country("IN")
csc.parse_phone_number("+14155552671")
csc.convert_country_code("US", from_format="iso2", to_format="iso3")

# Plan and quota headers, without a second call
response = csc.request("/countries")
print(response.meta.plan, response.meta.daily.remaining, response.meta.cache)

try:
    csc.get_country("IN")
except RateLimitError as exc:
    print(f"{exc.period} limit of {exc.limit} reached — {exc.upgrade_url}")
```

Async, same surface:

```python
import asyncio
from countrystatecity import AsyncCountryStateCity

async def main() -> None:
    async with AsyncCountryStateCity() as csc:
        country, states = await asyncio.gather(
            csc.get_country("IN"),
            csc.get_states_of_country("IN"),
        )

asyncio.run(main())
```

See the [client README](./python/packages/api/README.md) for the full method
table and error reference.

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

### Regions

```python
from countrystatecity_regions import (
    get_region_by_country,
    get_countries_by_region,
    get_countries_by_subregion,
    get_all_region_names,
    search_regions,
)

# Region/subregion for a country
region = get_region_by_country("US")
print(f"{region.region} — {region.subregion}")  # Americas — Northern America

# All countries in a region
asian_countries = get_countries_by_region("Asia")

# All countries in a subregion
south_asia = get_countries_by_subregion("Southern Asia")

# List distinct regions
print(get_all_region_names())  # ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania', 'Polar']

# Search
results = search_regions("southern asia")
```

### Postal Codes

```python
from countrystatecity_postal_codes import (
    get_postal_info_by_country,
    get_postcodes_of_country,
    validate_postcode,
)

# Postal code format/regex for a country
us_info = get_postal_info_by_country("US")
print(us_info.postalCodeFormat)  # #####-####

# Validate a postcode against the country's known format
validate_postcode("US", "10001")  # True

# All postcodes for a country (lazy loaded)
postcodes = get_postcodes_of_country("AD")
```

## ✨ Features

### API client

- ✅ **Sync and async** clients with identical method names and signatures
- ✅ **Typed payloads** via `TypedDict`, plus `py.typed`
- ✅ **Structured errors** for transport failures and 400/401/403/404/429/5xx,
  preserving `feature`, `upgradeUrl`, `tier`, `limit`, and `period`
- ✅ **Plan and quota metadata** from response headers
- ✅ **Input validated locally** against the API's own rules, so malformed calls
  never spend quota
- ✅ **Finite timeouts**, no implicit retries, no telemetry
- ✅ **One dependency** (httpx)

### Offline packages

- ✅ **Type-safe** with Pydantic models and mypy strict mode
- ✅ **Lazy loading** for minimal memory footprint
- ✅ **250 countries** with metadata
- ✅ **5,308 states/provinces**
- ✅ **171,938 cities**
- ✅ **432 timezones** with GMT offsets and time conversion
- ✅ **249 country/currency associations**
- ✅ **4,724 translations** in 19 languages
- ✅ **Phone/dialing codes** for 250 countries
- ✅ **Regions and subregions** for 250 countries
- ✅ **844,248 postal/ZIP-code records** across 125 countries, with validation regexes for 189
- ✅ **Zero external dependencies** (except Pydantic)
- ✅ **Python 3.8–3.12** support
- ✅ **Full test coverage** with pytest

## 🏗️ Repository Structure

```
countrystatecity-pypi/
├── python/
│   └── packages/
│       ├── api/           # countrystatecity          (API client)
│       ├── countries/     # countrystatecity-countries
│       ├── timezones/     # countrystatecity-timezones
│       ├── currencies/    # countrystatecity-currencies
│       ├── translations/  # countrystatecity-translations
│       ├── phonecodes/    # countrystatecity-phonecodes
│       ├── regions/       # countrystatecity-regions
│       └── postal_codes/  # countrystatecity-postal-codes
│
└── .github/
    └── workflows/
        ├── python-ci.yml    # CI — tests, type check, lint
        ├── publish.yml      # Publish to PyPI
        ├── release.yml      # Version bump + changelog (data packages)
        └── update-data.yml  # Weekly data sync
```

Each package's import name is derived from its `[project].name` in
`pyproject.toml` (hyphens become underscores), so the data packages import as
`countrystatecity_<name>` while the API client imports as the bare
`countrystatecity` namespace. CI and the publish workflow read it from there
rather than assuming a prefix.

Version bumps differ too: `release.yml` moves the seven data packages in
lockstep on every upstream data sync, while `countrystatecity` is versioned by
hand — it ships no data, so a data sync does not change it.

## 🛠️ Development

```bash
git clone https://github.com/dr5hn/countrystatecity-pypi.git

# Install a package in dev mode (replace 'countries' with any package
# directory; use 'api' for the client)
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

For the API client the module name is `countrystatecity`:

```bash
cd python/packages/api
pip install -e ".[dev]"
pytest --cov=countrystatecity --cov-report=term
mypy countrystatecity/ --strict
ruff check countrystatecity/ tests/
black --check countrystatecity/ tests/
isort --check countrystatecity/ tests/
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
- **Production API**: [Get a free API key](https://app.countrystatecity.in/?utm_source=github&utm_medium=repository&utm_campaign=python_packages)
- **Pricing**: [Compare API plans](https://countrystatecity.in/pricing/?utm_source=github&utm_medium=repository&utm_campaign=python_packages)

## 🔗 Related Projects

- [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) — Source database
- [countrystatecity NPM](https://github.com/dr5hn/countrystatecity-npm) — JavaScript/TypeScript packages

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
