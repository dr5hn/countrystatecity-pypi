# countrystatecity-translations

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![translations](https://static.pepy.tech/personalized-badge/countrystatecity-translations?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=translations)](https://pepy.tech/project/countrystatecity-translations)
[![translations](https://static.pepy.tech/personalized-badge/countrystatecity-translations?period=week&units=international_system&left_color=grey&right_color=brightgreen&left_text=translations)](https://pepy.tech/project/countrystatecity-translations)

Official Python package for 4,724 country-name translations covering 250 countries across 19 languages. Part of the [countrystatecity](https://github.com/dr5hn/countrystatecity-pypi) ecosystem.

## From offline prototype to production

This package provides a versioned offline snapshot. For regularly updated data,
server-side search and filtering, field-selected responses, or managed availability
and support, use the Country State City API.

[Get a free API key](https://app.countrystatecity.in/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=translations) ·
[API docs](https://docs.countrystatecity.in/api/introduction) ·
[Pricing](https://countrystatecity.in/pricing/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=translations) ·
[Migration guide](https://github.com/dr5hn/countrystatecity-pypi/blob/main/docs/MIGRATING_TO_API.md)

Keep API keys in server-side environment variables, never in client-side code or
source control.

## Installation

```bash
pip install countrystatecity-translations
```

## Quick Start

```python
from countrystatecity_translations import (
    get_all_translations,
    get_translations_by_country,
    get_translations_by_language,
    get_translation,
    search_translations,
)

# Get all translation entries
translations = get_all_translations()
# [Translation(countryCode="AF", lang="fr", translation="Afghanistan", ...), ...]

# Get all translations for a country (all 19 languages)
de_translations = get_translations_by_country("DE")
# [Translation(countryCode="DE", lang="fr", translation="Allemagne", ...), ...]

# Get all countries translated into a specific language
french = get_translations_by_language("fr")
# [Translation(lang="fr", translation="Afghanistan", ...), ...]

# Lookup a single translation
t = get_translation("DE", "fr")
# Translation(countryCode="DE", countryName="Germany", lang="fr", translation="Allemagne")

# Search translated names
results = search_translations("Allemagne")
```

## Data Model

```python
class Translation(BaseModel):
    countryCode: str  # ISO2 country code (e.g., "DE")
    countryName: str  # English country name (e.g., "Germany")
    lang: str         # Language code (e.g., "fr")
    translation: str  # Translated country name (e.g., "Allemagne")
```

## Supported Languages

| Code | Language | Code | Language |
|---|---|---|---|
| `ar` | Arabic | `ko` | Korean |
| `br` | Breton | `nl` | Dutch |
| `de` | German | `pl` | Polish |
| `es` | Spanish | `pt` | Portuguese |
| `fa` | Persian | `pt-BR` | Portuguese (Brazil) |
| `fr` | French | `ru` | Russian |
| `hi` | Hindi | `tr` | Turkish |
| `hr` | Croatian | `uk` | Ukrainian |
| `it` | Italian | `zh-CN` | Chinese (Simplified) |
| `ja` | Japanese | | |

## API Reference

| Function | Description |
|---|---|
| `get_all_translations()` | Get all translation entries |
| `get_translations_by_country(code)` | Get all language translations for a country |
| `get_translations_by_language(lang)` | Get all countries translated into a language |
| `get_translation(code, lang)` | Get a single country-language translation |
| `search_translations(query)` | Search by translated name or English country name |

## License

ODbL-1.0 — see [LICENSE](LICENSE).

## Other Packages in this Ecosystem

| Package | Description |
|---|---|
| [countrystatecity-countries](https://pypi.org/project/countrystatecity-countries/) | 250 countries, 5,308 states, 171,938 cities |
| [countrystatecity-timezones](https://pypi.org/project/countrystatecity-timezones/) | 432 IANA timezones with country associations and time conversion |
| [countrystatecity-currencies](https://pypi.org/project/countrystatecity-currencies/) | 249 country/currency associations |
| [countrystatecity-phonecodes](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250 countries |
| [countrystatecity-regions](https://pypi.org/project/countrystatecity-regions/) | Region and subregion associations for 250 countries |
| [countrystatecity-postal-codes](https://pypi.org/project/countrystatecity-postal-codes/) | Postal/ZIP records for 125 countries |

Data sourced from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
