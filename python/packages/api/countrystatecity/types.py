"""Typed shapes for Country State City API payloads.

Every payload is a plain ``dict`` at runtime; these ``TypedDict`` definitions
describe the keys a response may contain without adding a validation layer.

All of them are ``total=False`` on purpose. Which keys arrive depends on the
caller's plan data-access level and on the ``fields`` query parameter, so no key
is guaranteed present on every plan. Read optional keys with ``.get()``, or
assert the ones your plan guarantees at your own boundary.

Documented tier gating (see the API pricing page for the current table):

* **basic** -- core identity, coordinates, region, and timezone fields.
* **coordinates** -- adds extended metadata such as ``population``, ``tld``,
  ``nationality``, ``numeric_code``, and postal-code patterns.
* **full** -- adds ``translations`` and ``wikiDataId``.
"""

from typing import Any, Dict, Optional, TypedDict

__all__ = [
    "City",
    "Country",
    "CurrencyDetail",
    "CurrencyInfo",
    "DialCode",
    "FuzzyResult",
    "IsoConvert",
    "IsoCountry",
    "IsoState",
    "JsonDict",
    "JsonValue",
    "PhoneParsed",
    "Region",
    "State",
    "Subregion",
    "TimezoneInfo",
]

#: A decoded JSON value of any shape.
JsonValue = Any

#: A decoded JSON object.
JsonDict = Dict[str, Any]


class Country(TypedDict, total=False):
    """A country record from ``/countries`` and related endpoints."""

    id: int
    name: str
    iso2: str
    iso3: str
    phonecode: str
    capital: Optional[str]
    currency: Optional[str]
    native: Optional[str]
    emoji: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    region: Optional[str]
    region_id: Optional[int]
    subregion: Optional[str]
    subregion_id: Optional[int]
    timezones: Optional[str]
    numeric_code: Optional[str]
    currency_name: Optional[str]
    currency_symbol: Optional[str]
    tld: Optional[str]
    nationality: Optional[str]
    population: Optional[int]
    gdp: Optional[int]
    area_sq_km: Optional[float]
    postal_code_format: Optional[str]
    postal_code_regex: Optional[str]
    emojiU: Optional[str]
    translations: Optional[str]
    wikiDataId: Optional[str]


class State(TypedDict, total=False):
    """A state, province, or comparable subdivision record."""

    id: int
    name: str
    iso2: Optional[str]
    country_id: int
    country_code: str
    latitude: Optional[str]
    longitude: Optional[str]
    timezone: Optional[str]
    fips_code: Optional[str]
    iso3166_2: Optional[str]
    type: Optional[str]
    level: Optional[int]
    parent_id: Optional[int]
    native: Optional[str]
    population: Optional[int]
    translations: Optional[str]
    wikiDataId: Optional[str]


class City(TypedDict, total=False):
    """A city record."""

    id: int
    name: str
    state_id: int
    state_code: str
    country_id: int
    country_code: str
    latitude: str
    longitude: str
    timezone: Optional[str]
    population: Optional[int]
    type: Optional[str]
    level: Optional[int]
    parent_id: Optional[int]
    native: Optional[str]
    translations: Optional[str]
    wikiDataId: Optional[str]


class Region(TypedDict, total=False):
    """A continental region record."""

    id: int
    name: str
    translations: Optional[str]
    wikiDataId: Optional[str]


class Subregion(TypedDict, total=False):
    """A geographic subregion within a region."""

    id: int
    name: str
    region_id: int
    translations: Optional[str]
    wikiDataId: Optional[str]


class TimezoneInfo(TypedDict, total=False):
    """An IANA timezone with its UTC offsets and current DST state.

    The API derives ``offset_utc`` and ``dst_offset_utc`` by sampling 1 January
    and 1 July of the current year, so zones whose DST window falls outside both
    sample dates (notably ``Africa/Casablanca``) can report the two offsets as
    equal and ``is_dst_now`` incorrectly.
    """

    iana: str
    abbreviation: str
    offset_utc: str
    dst_offset_utc: str
    is_dst_now: bool


class CurrencyDetail(TypedDict, total=False):
    """The currency half of a :class:`CurrencyInfo` record."""

    code: str
    name: Optional[str]
    symbol: Optional[str]


class CurrencyInfo(TypedDict, total=False):
    """A country's ISO 4217 currency.

    ``currency.code`` is always present; ``name`` and ``symbol`` are null for a
    small number of currency-union and non-monetary territories. Fall back to
    ``code`` when rendering a missing symbol.
    """

    country: str
    currency: CurrencyDetail


class DialCode(TypedDict, total=False):
    """An international dial code for a country.

    ``area_code`` is present only for NANP territories that pin a fixed area
    code, such as ``246`` for Barbados.
    """

    country: str
    dial_code: str
    iso2: str
    iso3: str
    area_code: str


class PhoneParsed(TypedDict, total=False):
    """The result of parsing an E.164 phone number.

    Echoes the caller's number back in ``e164`` and ``national_number``. That is
    personal data: the API marks the response ``Cache-Control: no-store``, and
    it should not be logged.
    """

    country: str
    dial_code: str
    iso2: str
    iso3: str
    national_number: str
    e164: str
    area_code: str


class IsoCountry(TypedDict, total=False):
    """A country record from the ISO 3166-1 lookup endpoint."""

    id: int
    name: str
    iso2: str
    iso3: str
    numeric_code: Optional[str]


class IsoState(TypedDict, total=False):
    """A state record from the ISO 3166-2 lookup endpoint."""

    id: int
    name: str
    iso2: Optional[str]
    iso3166_2: Optional[str]
    country_id: int
    country_code: str


#: The result of an ISO 3166-1 code conversion.
#:
#: Defined with the functional syntax because ``from`` is a Python keyword.
#:
#: The production API returns the caller's code under the key ``input``. The
#: published OpenAPI contract names that key ``value``; both are declared here
#: so either spelling type-checks, but production sends ``input``.
IsoConvert = TypedDict(
    "IsoConvert",
    {"from": str, "to": str, "input": str, "value": str, "result": str},
    total=False,
)


class FuzzyResult(TypedDict, total=False):
    """One typo-tolerant search hit.

    Every hit carries these keys. Each hit *also* carries the full field set of
    the matched entity for the caller's data-access level -- a :class:`Country`,
    :class:`State`, or :class:`City` depending on the ``type`` argument -- which
    is why ``fuzzy_search`` is typed as returning plain dicts. Cast to the
    entity type you searched for when you need static field checking.
    """

    id: int
    name: str
    match_score: float
    matched_alias: Optional[str]
    country_name: str
    state_name: Optional[str]
