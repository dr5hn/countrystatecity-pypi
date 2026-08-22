"""One definition per API endpoint, shared by the sync and async clients.

Each function validates its arguments, percent-encodes the path, and returns a
ready-to-send :class:`Endpoint`. The two client classes differ only in how they
hand that ``Endpoint`` to httpx, so route shapes, query names, and validation
rules exist exactly once in this package.

Paths are relative to the ``/v1`` base URL.
"""

from typing import Dict, NamedTuple, Optional, Sequence, Union

from . import _validation as v
from .errors import ValidationError

__all__ = ["Endpoint"]

Identifier = Union[str, int]
FieldSelection = Union[str, Sequence[str]]


class Endpoint(NamedTuple):
    """A prepared request: a validated path and its query parameters."""

    path: str
    params: Dict[str, str]


def _list_params(
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Dict[str, str]:
    """Validate the query parameters shared by every list endpoint."""
    params: Dict[str, str] = {}
    if q is not None:
        params["q"] = v.search_query(q)
    if fields is not None:
        params["fields"] = v.field_list(fields)
    if sort is not None:
        params["sort"] = v.sort_spec(sort)
    return params


def _detail_params(*, fields: Optional[FieldSelection] = None) -> Dict[str, str]:
    """Validate the query parameters shared by every detail endpoint."""
    params: Dict[str, str] = {}
    if fields is not None:
        params["fields"] = v.field_list(fields)
    return params


# --------------------------------------------------------------------------
# Countries, states, cities
# --------------------------------------------------------------------------


def countries(
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /countries`` -- every country."""
    return Endpoint("/countries", _list_params(q=q, fields=fields, sort=sort))


def country(
    country_id: Identifier, *, fields: Optional[FieldSelection] = None
) -> Endpoint:
    """``GET /countries/{ciso}`` -- one country by ISO code or id."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    return Endpoint(f"/countries/{ciso}", _detail_params(fields=fields))


def states(
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /states`` -- every state worldwide."""
    return Endpoint("/states", _list_params(q=q, fields=fields, sort=sort))


def states_of_country(
    country_id: Identifier,
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /countries/{ciso}/states`` -- states within one country."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    return Endpoint(
        f"/countries/{ciso}/states", _list_params(q=q, fields=fields, sort=sort)
    )


def state(
    country_id: Identifier,
    state_id: Identifier,
    *,
    fields: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /countries/{ciso}/states/{siso}`` -- one state."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    siso = v.quote_segment(v.state_code(state_id))
    return Endpoint(f"/countries/{ciso}/states/{siso}", _detail_params(fields=fields))


def cities_of_country(
    country_id: Identifier,
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /countries/{ciso}/cities`` -- every city in one country."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    return Endpoint(
        f"/countries/{ciso}/cities", _list_params(q=q, fields=fields, sort=sort)
    )


def cities_of_state(
    country_id: Identifier,
    state_id: Identifier,
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /countries/{ciso}/states/{siso}/cities`` -- cities in one state."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    siso = v.quote_segment(v.state_code(state_id))
    return Endpoint(
        f"/countries/{ciso}/states/{siso}/cities",
        _list_params(q=q, fields=fields, sort=sort),
    )


# --------------------------------------------------------------------------
# Regions and subregions
# --------------------------------------------------------------------------


def regions(
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /regions`` -- every continental region."""
    return Endpoint("/regions", _list_params(q=q, fields=fields, sort=sort))


def region(
    region_id: Identifier, *, fields: Optional[FieldSelection] = None
) -> Endpoint:
    """``GET /regions/{id}`` -- one region."""
    ident = v.quote_segment(v.entity_id(region_id, name="region_id"))
    return Endpoint(f"/regions/{ident}", _detail_params(fields=fields))


def subregions_of_region(
    region_id: Identifier,
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /regions/{id}/subregions`` -- subregions within one region."""
    ident = v.quote_segment(v.entity_id(region_id, name="region_id"))
    return Endpoint(
        f"/regions/{ident}/subregions", _list_params(q=q, fields=fields, sort=sort)
    )


def subregion(
    subregion_id: Identifier, *, fields: Optional[FieldSelection] = None
) -> Endpoint:
    """``GET /subregions/{id}`` -- one subregion."""
    ident = v.quote_segment(v.entity_id(subregion_id, name="subregion_id"))
    return Endpoint(f"/subregions/{ident}", _detail_params(fields=fields))


def countries_of_subregion(
    subregion_id: Identifier,
    *,
    q: Optional[str] = None,
    fields: Optional[FieldSelection] = None,
    sort: Optional[FieldSelection] = None,
) -> Endpoint:
    """``GET /subregions/{id}/countries`` -- countries in one subregion."""
    ident = v.quote_segment(v.entity_id(subregion_id, name="subregion_id"))
    return Endpoint(
        f"/subregions/{ident}/countries", _list_params(q=q, fields=fields, sort=sort)
    )


# --------------------------------------------------------------------------
# Timezones
# --------------------------------------------------------------------------


def timezone_of_country(country_id: Identifier) -> Endpoint:
    """``GET /timezone/{ciso}`` -- a country's canonical timezone."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    return Endpoint(f"/timezone/{ciso}", {})


def timezone_of_state(country_id: Identifier, state_id: Identifier) -> Endpoint:
    """``GET /timezone/{ciso}/{siso}`` -- a state's timezone."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    siso = v.quote_segment(v.state_code(state_id))
    return Endpoint(f"/timezone/{ciso}/{siso}", {})


def timezone_of_city(
    country_id: Identifier, state_id: Identifier, city: Identifier
) -> Endpoint:
    """``GET /timezone/{ciso}/{siso}/{city_id}`` -- a city's timezone."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    siso = v.quote_segment(v.state_code(state_id))
    cid = v.quote_segment(v.city_id(city))
    return Endpoint(f"/timezone/{ciso}/{siso}/{cid}", {})


# --------------------------------------------------------------------------
# Currencies
# --------------------------------------------------------------------------


def currencies(*, code: Optional[str] = None) -> Endpoint:
    """``GET /currency`` -- every country currency, optionally filtered.

    The published OpenAPI contract lists this route as ``/currencies``; the
    production API serves ``/currency``, which is what this client calls.
    """
    params: Dict[str, str] = {}
    if code is not None:
        params["code"] = v.currency_code(code)
    return Endpoint("/currency", params)


def currency_of_country(country_id: Identifier) -> Endpoint:
    """``GET /currency/{ciso}`` -- one country's currency."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    return Endpoint(f"/currency/{ciso}", {})


# --------------------------------------------------------------------------
# Phone
# --------------------------------------------------------------------------


def dial_codes(*, code: Optional[str] = None) -> Endpoint:
    """``GET /phone`` -- every dial code, optionally filtered by code."""
    params: Dict[str, str] = {}
    if code is not None:
        params["code"] = v.dial_code(code)
    return Endpoint("/phone", params)


def dial_code_of_country(country_id: Identifier) -> Endpoint:
    """``GET /phone/{ciso}`` -- one country's dial code."""
    ciso = v.quote_segment(v.country_identifier(country_id))
    return Endpoint(f"/phone/{ciso}", {})


def parse_phone_number(number: str) -> Endpoint:
    """``GET /phone/parse`` -- split an E.164 number into country and national parts."""
    return Endpoint("/phone/parse", {"number": v.phone_number(number)})


# --------------------------------------------------------------------------
# ISO lookups
# --------------------------------------------------------------------------


def lookup_country_iso(
    *,
    iso2: Optional[str] = None,
    iso3: Optional[str] = None,
    numeric: Optional[str] = None,
) -> Endpoint:
    """``GET /iso/country`` -- resolve a country from one ISO 3166-1 code.

    Raises:
        ValidationError: If anything other than exactly one code is supplied.
    """
    supplied = {
        "iso2": iso2,
        "iso3": iso3,
        "numeric": numeric,
    }
    given = {key: value for key, value in supplied.items() if value is not None}
    if len(given) != 1:
        raise ValidationError(
            "Provide exactly one of iso2, iso3, or numeric; " f"got {len(given)}."
        )
    name, value = next(iter(given.items()))
    return Endpoint("/iso/country", {name: v.iso_country_code(value, name=name)})


def lookup_state_iso(iso: str) -> Endpoint:
    """``GET /iso/state`` -- resolve a state from its ISO 3166-2 code."""
    return Endpoint("/iso/state", {"iso": v.iso_3166_2(iso)})


def convert_country_code(value: str, *, from_format: str, to_format: str) -> Endpoint:
    """``GET /iso/country/convert`` -- convert between ISO 3166-1 formats.

    Raises:
        ValidationError: If the formats match, or the value does not match the
            source format.
    """
    source = v.code_format(from_format, name="from_format")
    target = v.code_format(to_format, name="to_format")
    if source == target:
        raise ValidationError("from_format and to_format must be different.")
    return Endpoint(
        "/iso/country/convert",
        {
            "from": source,
            "to": target,
            "value": v.iso_country_code(value, name=source, label="value"),
        },
    )


# --------------------------------------------------------------------------
# Fuzzy search
# --------------------------------------------------------------------------


def fuzzy_search(
    query: str,
    *,
    entity: str = "city",
    country: Optional[str] = None,
    limit: int = 10,
    threshold: float = 0.3,
) -> Endpoint:
    """``GET /search/fuzzy`` -- typo-tolerant search over one entity type.

    Raises:
        ValidationError: If ``country`` is combined with ``entity="country"``,
            which the API rejects, or any argument is out of range.
    """
    resolved_entity = v.fuzzy_type(entity)
    params: Dict[str, str] = {
        "q": v.search_query(query),
        "type": resolved_entity,
        "limit": str(v.bounded_int(limit, name="limit", minimum=1, maximum=50)),
        "threshold": str(
            v.bounded_float(threshold, name="threshold", minimum=0.1, maximum=1.0)
        ),
    }
    if country is not None:
        if resolved_entity == "country":
            raise ValidationError(
                "country is not a valid filter when entity='country'."
            )
        params["country"] = v.iso_country_code(country, name="iso2", label="country")
    return Endpoint("/search/fuzzy", params)
