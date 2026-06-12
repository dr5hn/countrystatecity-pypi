# countrystatecity-translations

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![Monthly Downloads](https://img.shields.io/pypi/dm/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/)
[![Weekly Downloads](https://img.shields.io/pypi/dw/countrystatecity-translations)](https://pypi.org/project/countrystatecity-translations/)

Official Python package for country name translations — 4700+ entries covering 195 countries across 19 languages. Part of the [countrystatecity](https://github.com/dr5hn/countrystatecity-pypi) ecosystem.

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
| [countrystatecity-countries](https://pypi.org/project/countrystatecity-countries/) | 250+ countries, 5,000+ states, 150,000+ cities |
| [countrystatecity-timezones](https://pypi.org/project/countrystatecity-timezones/) | 400+ IANA timezones with country associations and time conversion |
| [countrystatecity-currencies](https://pypi.org/project/countrystatecity-currencies/) | Currency codes, names, and symbols for every country |
| [countrystatecity-phonecodes](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250+ countries |

Data sourced from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
