# Changelog

All notable changes to `countrystatecity-translations` will be documented in this file.

## [1.0.0] - 2026-06-05

### Added
- Initial release
- `Translation` Pydantic model with country code, English name, language code, and translated name
- `get_all_translations()` — retrieve all 4700+ translation entries
- `get_translations_by_country(country_code)` — get all language translations for a country
- `get_translations_by_language(lang)` — get all countries translated into a specific language
- `get_translation(country_code, lang)` — lookup a single country-language translation
- `search_translations(query)` — case-insensitive search across translated and English names
- 19 languages: ar, br, de, es, fa, fr, hi, hr, it, ja, ko, nl, pl, pt, pt-BR, ru, tr, uk, zh-CN
- Python 3.8–3.12 support
- Full type hints and mypy strict mode compliance
- PEP 561 `py.typed` marker
