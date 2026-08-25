"""Payload types match what the production API actually serialises.

The API's geographic tables key on 64-bit ``BIGINT`` columns, and the API calls
``enableBigIntSerialization()`` at startup (``api/src/utils/bigint.ts``, wired up
in ``api/src/app.ts``), which installs ``BigInt.prototype.toJSON`` returning
``this.toString()``. Every ``bigint`` column therefore leaves the API as a JSON
*string*, and the controllers hand rows straight to ``res.json`` without
coercing them back to numbers.

Typing those keys ``int`` would be wrong in a way nothing else catches: the
values decode fine, comparisons like ``country["id"] == 101`` just silently stop
matching. So the mapping is pinned here from both directions.

The table below is transcribed from ``api/src/types/geographic.ts`` and
``api/src/controllers/fuzzySearch.controller.ts`` on the API's ``origin/main``,
not from this package's mocked fixtures -- a fixture can be wrong in the same
way the type is.
"""

from typing import (
    Any,
    Dict,
    FrozenSet,
    Optional,
    Set,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import pytest

from countrystatecity import types as payload_types
from countrystatecity.types import (
    City,
    Country,
    FuzzyResult,
    IsoCountry,
    IsoState,
    Postcode,
    Region,
    State,
    Subregion,
)

#: Every key whose value is a ``bigint`` column in the API's schema, and which
#: therefore arrives as a decimal string. Keyed by ``TypedDict`` name.
BIGINT_FIELDS: Dict[str, FrozenSet[str]] = {
    "Country": frozenset({"id", "region_id", "subregion_id", "population", "gdp"}),
    "State": frozenset({"id", "country_id", "parent_id", "population"}),
    "City": frozenset({"id", "state_id", "country_id", "parent_id", "population"}),
    "Region": frozenset({"id"}),
    "Subregion": frozenset({"id", "region_id"}),
    "IsoCountry": frozenset({"id"}),
    "IsoState": frozenset({"id", "country_id"}),
    "FuzzyResult": frozenset({"id"}),
    "Postcode": frozenset({"id", "country_id", "state_id", "city_id"}),
}

#: The only keys anywhere in :mod:`countrystatecity.types` that are genuinely
#: numeric in the API's schema. ``level`` is a plain ``INTEGER``, ``area_sq_km``
#: is floating point, and ``match_score`` is computed inside the fuzzy-search
#: query. Anything else numeric is a bigint that was typed wrongly.
NUMERIC_FIELDS: FrozenSet[Tuple[str, str]] = frozenset(
    {
        ("State", "level"),
        ("City", "level"),
        ("Country", "area_sq_km"),
        ("FuzzyResult", "match_score"),
        ("PostcodePagination", "limit"),
    }
)

#: Key names that name a row identity. Used to catch a *new* id field that is
#: added without being registered in :data:`BIGINT_FIELDS`.
_ID_LIKE = frozenset({"id", "population", "gdp"})


def _typed_dicts() -> Dict[str, Any]:
    """Return every ``TypedDict`` exported by :mod:`countrystatecity.types`."""
    found: Dict[str, Any] = {}
    for name in payload_types.__all__:
        obj = getattr(payload_types, name)
        if hasattr(obj, "__annotations__") and hasattr(obj, "__total__"):
            found[name] = obj
    return found


def _hints(typed_dict: Any) -> Dict[str, Any]:
    """Return one ``TypedDict``'s resolved annotations."""
    return dict(get_type_hints(typed_dict))


def _flatten(annotation: Any) -> Set[Any]:
    """Return the set of leaf types inside a possibly-``Optional`` annotation.

    Args:
        annotation: A resolved type annotation.

    Returns:
        ``{str}`` for ``str``, ``{str, NoneType}`` for ``Optional[str]``, and so
        on, so a check can ignore how the optionality is spelled.
    """
    if get_origin(annotation) is Union:
        leaves: Set[Any] = set()
        for arg in get_args(annotation):
            leaves |= _flatten(arg)
        return leaves
    return {annotation}


def _is_id_like(field: str) -> bool:
    """Return whether ``field`` names a row identity or a bigint metric."""
    return field in _ID_LIKE or field.endswith("_id")


TYPED_DICTS = _typed_dicts()

BIGINT_CASES = sorted(
    (name, field) for name, fields in BIGINT_FIELDS.items() for field in fields
)


def test_every_exported_typed_dict_is_discovered() -> None:
    """Guards the reflection below against silently finding nothing."""
    assert set(BIGINT_FIELDS) <= set(TYPED_DICTS)
    assert len(TYPED_DICTS) >= 14


@pytest.mark.parametrize(
    "type_name, field", BIGINT_CASES, ids=[f"{n}.{f}" for n, f in BIGINT_CASES]
)
def test_bigint_backed_fields_are_declared_as_strings(
    type_name: str, field: str
) -> None:
    """A bigint column reaches Python as a decimal string, never an int."""
    hints = _hints(TYPED_DICTS[type_name])
    assert field in hints, f"{type_name} no longer declares {field!r}"

    leaves = _flatten(hints[field])
    assert str in leaves, f"{type_name}.{field} must be str-typed; got {hints[field]}"
    assert int not in leaves, (
        f"{type_name}.{field} is a BIGINT column: the API serialises it as a "
        f"JSON string, so int is wrong. Got {hints[field]}."
    )


def test_no_unregistered_numeric_field_exists() -> None:
    """A new int/float key must be a real number, not an unconverted bigint."""
    offenders = []
    for type_name, typed_dict in TYPED_DICTS.items():
        for field, annotation in _hints(typed_dict).items():
            leaves = _flatten(annotation)
            if (int in leaves or float in leaves) and (
                type_name,
                field,
            ) not in NUMERIC_FIELDS:
                offenders.append(f"{type_name}.{field}: {annotation}")

    assert offenders == [], (
        "These fields are typed numerically but are not in NUMERIC_FIELDS. If "
        "the column is a BIGINT, type it str; if it is genuinely numeric, add "
        f"it to NUMERIC_FIELDS with a reason: {offenders}"
    )


def test_every_id_like_field_is_registered_as_a_bigint() -> None:
    """A newly added ``*_id`` key cannot slip in untyped and unchecked."""
    unregistered = []
    for type_name, typed_dict in TYPED_DICTS.items():
        registered = BIGINT_FIELDS.get(type_name, frozenset())
        for field in _hints(typed_dict):
            if _is_id_like(field) and field not in registered:
                unregistered.append(f"{type_name}.{field}")

    assert unregistered == [], (
        "These keys look like row identities but are absent from "
        f"BIGINT_FIELDS: {unregistered}"
    )


def test_optionality_matches_the_api_schema() -> None:
    """Nullable columns stay ``Optional``; non-nullable ones stay bare."""
    nullable = {
        ("Country", "region_id"),
        ("Country", "subregion_id"),
        ("Country", "population"),
        ("Country", "gdp"),
        ("State", "parent_id"),
        ("State", "population"),
        ("City", "parent_id"),
        ("City", "population"),
        ("Postcode", "state_id"),
        ("Postcode", "city_id"),
    }
    for type_name, field in BIGINT_CASES:
        leaves = _flatten(_hints(TYPED_DICTS[type_name])[field])
        expected_optional = (type_name, field) in nullable
        assert (type(None) in leaves) is expected_optional, (
            f"{type_name}.{field} optionality does not match the API schema; "
            f"expected optional={expected_optional}"
        )


def _static_required_ids_are_strings(
    country: Country,
    state: State,
    city: City,
    region: Region,
    subregion: Subregion,
    iso_country: IsoCountry,
    iso_state: IsoState,
    hit: FuzzyResult,
    postcode: Postcode,
) -> Tuple[str, ...]:
    """Static half of the guard: ``mypy --strict`` fails if any of these is an int.

    Never called; it exists so the type checker proves the same property the
    runtime tests above assert.
    """
    return (
        country["id"],
        state["id"],
        state["country_id"],
        city["id"],
        city["state_id"],
        city["country_id"],
        region["id"],
        subregion["id"],
        subregion["region_id"],
        iso_country["id"],
        iso_state["id"],
        iso_state["country_id"],
        hit["id"],
        postcode["id"],
        postcode["country_id"],
    )


def _static_nullable_ids_are_optional_strings(
    country: Country, state: State, city: City, postcode: Postcode
) -> Tuple[Optional[str], ...]:
    """Static guard for the nullable bigint columns. Never called."""
    return (
        country["region_id"],
        country["subregion_id"],
        country["population"],
        country["gdp"],
        state["parent_id"],
        state["population"],
        city["parent_id"],
        city["population"],
        postcode["state_id"],
        postcode["city_id"],
    )
