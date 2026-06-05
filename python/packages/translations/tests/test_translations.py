"""Tests for translation API functions."""

import pytest

from countrystatecity_translations import (
    get_all_translations,
    get_translation,
    get_translations_by_country,
    get_translations_by_language,
    search_translations,
)
from countrystatecity_translations.models import Translation


def test_get_all_translations():
    translations = get_all_translations()
    assert isinstance(translations, list)
    assert len(translations) > 0
    assert all(isinstance(t, Translation) for t in translations)


def test_get_all_translations_count():
    translations = get_all_translations()
    assert len(translations) > 4000


def test_get_translations_by_country_de():
    translations = get_translations_by_country("DE")
    assert isinstance(translations, list)
    assert len(translations) > 0
    assert all(t.countryCode == "DE" for t in translations)


def test_get_translations_by_country_has_multiple_languages():
    translations = get_translations_by_country("US")
    langs = [t.lang for t in translations]
    assert "fr" in langs
    assert "de" in langs
    assert "ja" in langs
    assert "ar" in langs


def test_get_translations_by_country_lowercase():
    upper = get_translations_by_country("DE")
    lower = get_translations_by_country("de")
    assert len(upper) == len(lower)


def test_get_translations_by_country_not_found():
    translations = get_translations_by_country("ZZ")
    assert translations == []


def test_get_translations_by_language_fr():
    translations = get_translations_by_language("fr")
    assert isinstance(translations, list)
    assert len(translations) > 0
    assert all(t.lang == "fr" for t in translations)


def test_get_translations_by_language_zh_cn():
    translations = get_translations_by_language("zh-CN")
    assert isinstance(translations, list)
    assert len(translations) > 0


def test_get_translations_by_language_not_found():
    translations = get_translations_by_language("xx")
    assert translations == []


def test_get_translation_specific():
    t = get_translation("DE", "fr")
    assert t is not None
    assert isinstance(t, Translation)
    assert t.countryCode == "DE"
    assert t.lang == "fr"
    assert t.translation == "Allemagne"


def test_get_translation_us_japanese():
    t = get_translation("US", "ja")
    assert t is not None
    assert t.translation == "アメリカ合衆国"


def test_get_translation_not_found_country():
    t = get_translation("ZZ", "fr")
    assert t is None


def test_get_translation_not_found_lang():
    t = get_translation("US", "xx")
    assert t is None


def test_translation_model_fields():
    t = get_translation("DE", "fr")
    assert t is not None
    assert isinstance(t.countryCode, str)
    assert isinstance(t.countryName, str)
    assert isinstance(t.lang, str)
    assert isinstance(t.translation, str)


def test_translation_model_immutable():
    t = get_translation("DE", "fr")
    assert t is not None
    with pytest.raises(Exception):
        t.translation = "Changed"  # type: ignore[misc]


def test_search_translations_by_translated_name():
    results = search_translations("Allemagne")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(t, Translation) for t in results)


def test_search_translations_by_english_name():
    results = search_translations("Germany")
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_translations_case_insensitive():
    lower = search_translations("allemagne")
    upper = search_translations("ALLEMAGNE")
    assert len(lower) == len(upper)


def test_search_translations_no_results():
    results = search_translations("xyzxyzxyz_invalid")
    assert results == []


def test_all_19_languages_present():
    all_langs = {t.lang for t in get_all_translations()}
    expected = {"ar", "br", "de", "es", "fa", "fr", "hi", "hr", "it", "ja",
                "ko", "nl", "pl", "pt", "pt-BR", "ru", "tr", "uk", "zh-CN"}
    assert expected == all_langs
