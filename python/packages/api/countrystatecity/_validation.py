"""Trust-boundary validation for every value that reaches a URL.

Each validator mirrors a rule the production API already enforces, and returns
the normalised string that goes into the request. Two things follow from doing
this locally:

* a malformed call raises :class:`~countrystatecity.errors.ValidationError`
  instead of spending one of the plan's requests on a guaranteed ``400``;
* nothing unvalidated ever reaches path interpolation. Path segments are also
  percent-encoded by :func:`quote_segment`, so neither ``/`` nor ``..`` can
  escape the segment it was given.

Field *names* in ``fields`` and ``sort`` are checked for shape only, not against
a list of known columns: the API's column set is plan-dependent and changes
independently of this package, so the server stays the authority on which names
exist.
"""

import re

# Two Sequences on purpose: the typing one is subscriptable in annotations on
# Python 3.8, the collections.abc one is what isinstance() accepts.
from collections.abc import Mapping as _AbcMapping
from collections.abc import Sequence as _AbcSequence
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union
from urllib.parse import quote, unquote

from .errors import ValidationError

__all__ = ["quote_segment", "request_params", "request_path"]

#: Largest identifier the API accepts for countries, regions, and subregions.
MAX_NUMERIC_ID = 999_999

#: Widest accepted city id. Matches the API's positive-safe-integer rule.
MAX_CITY_ID = 2**53 - 1

_COUNTRY_ISO_RE = re.compile(r"^[A-Za-z]{2,3}$")
_STATE_CODE_RE = re.compile(r"^[A-Za-z0-9-]{1,10}$")
_DIGITS_RE = re.compile(r"^[0-9]+$")
_FIELD_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SORT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?::(?:asc|desc))?$", re.IGNORECASE)
_CURRENCY_CODE_RE = re.compile(r"^[A-Za-z]{3}$")
_DIAL_CODE_RE = re.compile(r"^\+?[0-9]{1,4}(?:-[0-9]{1,6})?$")
_E164_RE = re.compile(r"^\+[0-9]{5,15}$")
_ISO2_RE = re.compile(r"^[A-Za-z]{2}$")
_ISO3_RE = re.compile(r"^[A-Za-z]{3}$")
_ISO_NUMERIC_RE = re.compile(r"^0*[1-9][0-9]{0,2}$")
_ISO_3166_2_RE = re.compile(r"^[A-Za-z]{2}-[A-Za-z0-9]{1,3}$")

#: Printable ASCII with no spaces. Loose on purpose -- the API has issued keys
#: in more than one format -- but strict enough that no whitespace, newline, or
#: control character can reach an HTTP header.
_API_KEY_RE = re.compile(r"^[\x21-\x7e]+$")

_SEARCH_MIN = 2
_SEARCH_MAX = 100

_POSTCODE_CODE_MIN = 1
_POSTCODE_CODE_MAX = 20
_POSTCODE_STATE_CODE_RE = re.compile(r"^[A-Za-z0-9-]{1,32}$")
_CURSOR_MAX = 512

CODE_FORMATS = ("iso2", "iso3", "numeric")
FUZZY_TYPES = ("city", "state", "country")
POSTCODE_TYPES = ("full", "outward", "sector", "district", "area")

#: Path segments that walk up out of the base URL rather than down into it.
_TRAVERSAL_SEGMENTS = frozenset({".", ".."})

#: Separators that must never survive percent-decoding inside a single segment:
#: an encoded ``/`` or ``\`` would turn one segment into two at whatever layer
#: decodes it next.
_SEPARATORS = ("/", "\\")

#: Percent-decoding rounds applied before a segment is judged. One round catches
#: ``%2e%2e``; the extra rounds catch ``%252e%252e``, which a proxy that decodes
#: before forwarding would hand on as ``..``.
_DECODE_ROUNDS = 3


def quote_segment(value: str) -> str:
    """Percent-encode ``value`` for use as a single URL path segment.

    Args:
        value: An already-validated segment.

    Returns:
        The segment with every reserved character encoded, including ``/``.
    """
    return quote(value, safe="")


def request_path(value: str, *, name: str = "path") -> str:
    """Validate a caller-supplied path for the raw ``request`` escape hatch.

    The escape hatch promises requests stay *under* the client's base URL, and
    httpx does not enforce that. Given a base URL of
    ``https://api.countrystatecity.in/v1``, httpx resolves the path
    ``/../admin`` to the host root followed by ``/admin`` -- outside ``/v1``
    entirely. This is the one place a caller hands over a whole path, so the
    containment rule is checked here.

    Accepts any ordinary ``/v1``-relative path, so endpoints added after this
    release need no change: only the escape shapes listed below are refused.

    Args:
        value: The path, relative to the base URL and starting with ``/``.
        name: Argument name, used in the error message.

    Returns:
        The path unchanged.

    Raises:
        ValidationError: If the path is not a string starting with a single
            ``/``; starts with ``//``, which reads as a protocol-relative URL
            pointing at another host; embeds a query or fragment, which belongs
            in ``params``; or contains a ``.`` or ``..`` segment, including its
            percent-encoded spellings.
    """
    if not isinstance(value, str) or not value.startswith("/"):
        raise ValidationError(f"{name} must be a string starting with '/'.")
    if value.startswith("//"):
        raise ValidationError(
            f"{name} must start with a single '/'; a leading '//' is read as a "
            "protocol-relative URL to another host."
        )
    for character in ("?", "#"):
        if character in value:
            raise ValidationError(
                f"{name} must not contain {character!r}; pass query parameters "
                "as params={...} instead."
            )
    for segment in value.split("/"):
        decoded = _decode_segment(segment)
        if decoded in _TRAVERSAL_SEGMENTS or any(sep in decoded for sep in _SEPARATORS):
            raise ValidationError(
                f"a {name} segment would escape the base URL; "
                "'.', '..', and encoded separators are not allowed."
            )
    return value


def request_params(
    value: Optional[Mapping[str, Any]], *, name: str = "params"
) -> Dict[str, Any]:
    """Validate query parameters for the raw ``request`` escape hatch.

    Args:
        value: A string-keyed mapping whose values are URL scalar values or
            lists/tuples of those values.
        name: Argument name, used in the error message.

    Returns:
        A plain dictionary suitable for ``httpx``.

    Raises:
        ValidationError: If the mapping shape or a key/value is unsupported.
            Raw values are never repeated in the error message.
    """
    if value is None:
        return {}
    if not isinstance(value, _AbcMapping):
        raise ValidationError(
            f"{name} must be a mapping with string keys and URL scalar values."
        )

    result: Dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not _query_value(item):
            raise ValidationError(
                f"{name} must be a mapping with string keys and URL scalar values."
            )
        result[key] = item
    return result


def _query_value(value: Any) -> bool:
    """Return whether ``value`` has a deterministic httpx query encoding."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    return isinstance(value, (list, tuple)) and all(
        item is None or isinstance(item, (str, int, float, bool)) for item in value
    )


def _decode_segment(segment: str) -> str:
    """Percent-decode one path segment until it stops changing.

    Args:
        segment: A single ``/``-delimited piece of a path.

    Returns:
        The segment after up to :data:`_DECODE_ROUNDS` decoding passes, so a
        doubly-encoded ``..`` is judged as ``..`` rather than as opaque text.
    """
    for _ in range(_DECODE_ROUNDS):
        decoded = unquote(segment)
        if decoded == segment:
            break
        segment = decoded
    return segment


def api_key(value: Optional[str], *, env_var: str) -> str:
    """Validate an API key before it is ever put on the wire.

    Args:
        value: The key supplied explicitly or read from the environment.
        env_var: Name of the environment variable, used in the error message.

    Returns:
        The key with surrounding whitespace removed.

    Raises:
        ValidationError: If the key is missing, blank, or contains a character
            that cannot appear in an HTTP header value.
    """
    if value is not None and not isinstance(value, str):
        raise ValidationError(f"api_key must be a string; got {type(value).__name__}.")
    if value is None or not value.strip():
        raise ValidationError(
            "An API key is required. Pass api_key=... or set the "
            f"{env_var} environment variable. Get a free key at "
            "https://app.countrystatecity.in/"
        )
    stripped = value.strip()
    if not _API_KEY_RE.match(stripped):
        # Deliberately does not echo the value: error messages get logged.
        raise ValidationError(
            "api_key contains characters that are not valid in an HTTP header. "
            "Expected printable ASCII with no spaces."
        )
    return stripped


def country_identifier(value: Union[str, int], *, name: str = "country") -> str:
    """Validate a country identifier: ISO2, ISO3, or numeric id.

    Args:
        value: ``"IN"``, ``"IND"``, ``233``, or ``"233"``.
        name: Argument name, used in the error message.

    Returns:
        The identifier as a string.

    Raises:
        ValidationError: If the value is neither a 2-3 letter ISO code nor a
            positive integer id within the API's accepted range.
    """
    text = _as_text(value, name=name)
    if _DIGITS_RE.match(text):
        return _numeric_in_range(text, name=name, maximum=MAX_NUMERIC_ID)
    if not _COUNTRY_ISO_RE.match(text):
        raise ValidationError(
            f"{name} must be a 2- or 3-letter ISO 3166-1 code (e.g. 'IN', 'IND') "
            f"or a numeric country id; got {text!r}."
        )
    return text


def state_code(value: Union[str, int], *, name: str = "state") -> str:
    """Validate a state or province code such as ``"MH"`` or ``"AN-AMA"``.

    Args:
        value: The subdivision code.
        name: Argument name, used in the error message.

    Returns:
        The code as a string.

    Raises:
        ValidationError: If the code is empty or longer than 10 characters, or
            contains anything other than letters, digits, and hyphens.
    """
    text = _as_text(value, name=name)
    if not _STATE_CODE_RE.match(text):
        raise ValidationError(
            f"{name} must be 1-10 letters, digits, or hyphens (e.g. 'MH', "
            f"'AN-AMA'); got {text!r}."
        )
    return text


def entity_id(value: Union[str, int], *, name: str) -> str:
    """Validate a region or subregion id.

    Args:
        value: A positive integer id, as ``int`` or digit string.
        name: Argument name, used in the error message.

    Returns:
        The id as a string.

    Raises:
        ValidationError: If the value is not a positive integer within range.
    """
    return _numeric_in_range(
        _as_text(value, name=name), name=name, maximum=MAX_NUMERIC_ID
    )


def city_id(value: Union[str, int], *, name: str = "city_id") -> str:
    """Validate a city id.

    City ids come from a 64-bit sequence and legitimately exceed the six-digit
    cap that applies to countries and regions, so only the positive
    safe-integer bound is enforced.

    Args:
        value: A positive integer id, as ``int`` or digit string.
        name: Argument name, used in the error message.

    Returns:
        The id as a string.

    Raises:
        ValidationError: If the value is not a positive integer within range.
    """
    return _numeric_in_range(_as_text(value, name=name), name=name, maximum=MAX_CITY_ID)


def search_query(value: str, *, name: str = "q") -> str:
    """Validate an inline search term.

    Args:
        value: The search term.
        name: Argument name, used in the error message.

    Returns:
        The term unchanged.

    Raises:
        ValidationError: If the term is not a string of 2-100 characters.
    """
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string; got {type(value).__name__}.")
    if not _SEARCH_MIN <= len(value) <= _SEARCH_MAX:
        raise ValidationError(
            f"{name} must be between {_SEARCH_MIN} and {_SEARCH_MAX} characters; "
            f"got {len(value)}."
        )
    return value


def field_list(value: Union[str, Sequence[str]], *, name: str = "fields") -> str:
    """Normalise a ``fields`` selection to a comma-separated string.

    Accepts either ``"id,name"`` or ``["id", "name"]``. Field names are checked
    for shape only; the API validates them against the caller's plan.

    Args:
        value: The requested field names.
        name: Argument name, used in the error message.

    Returns:
        The field names joined by commas.

    Raises:
        ValidationError: If the selection is empty or a name is malformed.
    """
    tokens = _tokenise(value, name=name)
    for token in tokens:
        if not _FIELD_RE.match(token):
            raise ValidationError(f"{name} entry {token!r} is not a valid field name.")
    return ",".join(tokens)


def sort_spec(value: Union[str, Sequence[str]], *, name: str = "sort") -> str:
    """Normalise a ``sort`` selection to a comma-separated string.

    Accepts ``"name:asc,population:desc"`` or the equivalent list. Whitespace
    around the colon is tolerated and removed. Direction defaults to ``asc`` on
    the server when omitted.

    Args:
        value: The requested sort terms.
        name: Argument name, used in the error message.

    Returns:
        The sort terms joined by commas.

    Raises:
        ValidationError: If the selection is empty or a term is malformed.
    """
    normalised: List[str] = []
    for token in _tokenise(value, name=name):
        # Tolerate the spacing the API itself tolerates ("name : desc") and
        # send the canonical form.
        candidate = ":".join(part.strip() for part in token.split(":"))
        if not _SORT_RE.match(candidate):
            raise ValidationError(
                f"{name} entry {token!r} must be 'field' or 'field:asc' / "
                "'field:desc'."
            )
        normalised.append(candidate)
    return ",".join(normalised)


def currency_code(value: str, *, name: str = "code") -> str:
    """Validate an ISO 4217 currency code such as ``"USD"``.

    Args:
        value: The currency code.
        name: Argument name, used in the error message.

    Returns:
        The code unchanged.

    Raises:
        ValidationError: If the code is not exactly three letters.
    """
    text = _as_text(value, name=name)
    if not _CURRENCY_CODE_RE.match(text):
        raise ValidationError(
            f"{name} must be a 3-letter ISO 4217 code (e.g. 'USD'); got {text!r}."
        )
    return text


def dial_code(value: Union[str, int], *, name: str = "code") -> str:
    """Validate an international dial code such as ``"+91"`` or ``"1-246"``.

    Args:
        value: The dial code, with or without a leading ``+``.
        name: Argument name, used in the error message.

    Returns:
        The dial code as a string.

    Raises:
        ValidationError: If the code is not 1-4 digits with an optional ``+``
            prefix and optional ``-`` area-code suffix.
    """
    text = _as_text(value, name=name)
    if not _DIAL_CODE_RE.match(text):
        raise ValidationError(
            f"{name} must be a dial code such as '+91', '44', or '1-246'; "
            f"got {text!r}."
        )
    return text


def phone_number(value: str, *, name: str = "number") -> str:
    """Validate an E.164 phone number.

    Args:
        value: The number, including its ``+`` prefix.
        name: Argument name, used in the error message.

    Returns:
        The number with surrounding whitespace removed.

    Raises:
        ValidationError: If the number is not ``+`` followed by 5-15 digits.
    """
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string; got {type(value).__name__}.")
    text = value.strip()
    if not _E164_RE.match(text):
        # Never echo the number: it is personal data and errors get logged.
        raise ValidationError(
            f"{name} must be in E.164 format: '+' followed by 5-15 digits "
            "(e.g. '+14155552671')."
        )
    return text


def postcode_code(value: str, *, name: str = "code") -> str:
    """Validate a postcode/ZIP code for exact lookup.

    Args:
        value: The code to look up.
        name: Argument name, used in the error message.

    Returns:
        The code with outer whitespace trimmed. Internal spaces and hyphens
        are preserved; matching is case-insensitive server-side.

    Raises:
        ValidationError: If the trimmed code is not 1-20 characters.
    """
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string; got {type(value).__name__}.")
    trimmed = value.strip()
    if not _POSTCODE_CODE_MIN <= len(trimmed) <= _POSTCODE_CODE_MAX:
        raise ValidationError(
            f"{name} must be {_POSTCODE_CODE_MIN}-{_POSTCODE_CODE_MAX} characters "
            f"after trimming outer whitespace; got {len(trimmed)}."
        )
    return trimmed


def postcode_state_code(value: Union[str, int], *, name: str = "state_code") -> str:
    """Validate the ``state_code`` filter on postcode search.

    Unlike the path-segment :func:`state_code`, which caps at 10 characters to
    match real subdivision codes, the postcode search API documents this filter
    with a wider 1-32 character bound.

    Args:
        value: The subdivision code to filter by.
        name: Argument name, used in the error message.

    Returns:
        The code as a string.

    Raises:
        ValidationError: If the code is empty, longer than 32 characters, or
            contains anything other than letters, digits, and hyphens.
    """
    text = _as_text(value, name=name)
    if not _POSTCODE_STATE_CODE_RE.match(text):
        raise ValidationError(
            f"{name} must be 1-32 letters, digits, or hyphens; got {text!r}."
        )
    return text


def postcode_type(value: str, *, name: str = "type") -> str:
    """Validate a postcode granularity filter.

    Args:
        value: ``"full"``, ``"outward"``, ``"sector"``, ``"district"``, or
            ``"area"``.
        name: Argument name, used in the error message.

    Returns:
        The type unchanged.

    Raises:
        ValidationError: If the type is not one of the five granularities.
    """
    return _one_of(value, POSTCODE_TYPES, name=name)


def cursor_token(value: str, *, name: str = "cursor") -> str:
    """Validate an opaque postcode-search pagination cursor.

    The cursor's internal shape is never inspected here: it is an
    implementation detail of the API's pagination, and this package must not
    parse or construct it -- only pass back a value the API itself returned.

    Args:
        value: The cursor, taken verbatim from a previous response's
            ``pagination["next_cursor"]``.
        name: Argument name, used in the error message.

    Returns:
        The cursor unchanged.

    Raises:
        ValidationError: If the cursor is not a non-empty string of at most
            512 characters.
    """
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{name} must be a non-empty string.")
    if len(value) > _CURSOR_MAX:
        raise ValidationError(
            f"{name} must be at most {_CURSOR_MAX} characters; got {len(value)}."
        )
    return value


def iso_country_code(value: str, *, name: str, label: Optional[str] = None) -> str:
    """Validate one of the three ISO 3166-1 country code formats.

    Args:
        value: The code.
        name: The format to enforce: ``"iso2"``, ``"iso3"``, or ``"numeric"``.
        label: Argument name to quote in the error message. Defaults to
            ``name``, which is right when the argument is itself called
            ``iso2``/``iso3``/``numeric``.

    Returns:
        The code as a string.

    Raises:
        ValidationError: If the code does not match the named format.
    """
    shown = label or name
    text = _as_text(value, name=shown)
    patterns = {"iso2": _ISO2_RE, "iso3": _ISO3_RE, "numeric": _ISO_NUMERIC_RE}
    expected = {
        "iso2": "2 letters (e.g. 'US')",
        "iso3": "3 letters (e.g. 'USA')",
        "numeric": "1-3 non-zero digits (e.g. '840')",
    }
    if not patterns[name].match(text):
        raise ValidationError(f"{shown} must be {expected[name]}; got {text!r}.")
    return text


def iso_3166_2(value: str, *, name: str = "iso") -> str:
    """Validate an ISO 3166-2 subdivision code such as ``"US-CA"``.

    Args:
        value: The subdivision code.
        name: Argument name, used in the error message.

    Returns:
        The code as a string.

    Raises:
        ValidationError: If the code is not ``XX-YYY`` shaped.
    """
    text = _as_text(value, name=name)
    if not _ISO_3166_2_RE.match(text):
        raise ValidationError(
            f"{name} must be an ISO 3166-2 code such as 'US-CA'; got {text!r}."
        )
    return text


def code_format(value: str, *, name: str) -> str:
    """Validate an ISO code format selector.

    Args:
        value: ``"iso2"``, ``"iso3"``, or ``"numeric"``.
        name: Argument name, used in the error message.

    Returns:
        The selector unchanged.

    Raises:
        ValidationError: If the selector is not one of the three formats.
    """
    return _one_of(value, CODE_FORMATS, name=name)


def fuzzy_type(value: str, *, name: str = "type") -> str:
    """Validate a fuzzy-search entity type.

    Args:
        value: ``"city"``, ``"state"``, or ``"country"``.
        name: Argument name, used in the error message.

    Returns:
        The type unchanged.

    Raises:
        ValidationError: If the type is not one of the three entities.
    """
    return _one_of(value, FUZZY_TYPES, name=name)


def bounded_int(value: int, *, name: str, minimum: int, maximum: int) -> int:
    """Validate an integer argument against an inclusive range.

    Args:
        value: The integer.
        name: Argument name, used in the error message.
        minimum: Smallest accepted value.
        maximum: Largest accepted value.

    Returns:
        The integer unchanged.

    Raises:
        ValidationError: If the value is not an int, or is out of range.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer; got {type(value).__name__}.")
    if not minimum <= value <= maximum:
        raise ValidationError(
            f"{name} must be between {minimum} and {maximum}; got {value}."
        )
    return value


def bounded_float(value: float, *, name: str, minimum: float, maximum: float) -> float:
    """Validate a float argument against an inclusive range.

    Args:
        value: The number.
        name: Argument name, used in the error message.
        minimum: Smallest accepted value.
        maximum: Largest accepted value.

    Returns:
        The value as a float.

    Raises:
        ValidationError: If the value is not numeric, or is out of range.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be a number; got {type(value).__name__}.")
    if not minimum <= value <= maximum:
        raise ValidationError(
            f"{name} must be between {minimum} and {maximum}; got {value}."
        )
    return float(value)


def _one_of(value: str, allowed: Sequence[str], *, name: str) -> str:
    """Validate that ``value`` is one of ``allowed``."""
    if not isinstance(value, str) or value not in allowed:
        raise ValidationError(
            f"{name} must be one of {', '.join(allowed)}; got {value!r}."
        )
    return value


def _as_text(value: Union[str, int], *, name: str) -> str:
    """Coerce a string-or-int argument to a non-empty string."""
    if isinstance(value, bool):
        raise ValidationError(f"{name} must be a string or integer; got a bool.")
    if isinstance(value, int):
        return str(value)
    if not isinstance(value, str):
        raise ValidationError(
            f"{name} must be a string or integer; got {type(value).__name__}."
        )
    text = value.strip()
    if not text:
        raise ValidationError(f"{name} must not be empty.")
    return text


def _numeric_in_range(text: str, *, name: str, maximum: int) -> str:
    """Validate a digit string as a positive integer no larger than ``maximum``."""
    if not _DIGITS_RE.match(text):
        raise ValidationError(f"{name} must be a positive integer; got {text!r}.")
    number = int(text)
    if not 1 <= number <= maximum:
        raise ValidationError(f"{name} must be between 1 and {maximum}; got {number}.")
    return text


def _tokenise(value: Union[str, Sequence[str]], *, name: str) -> List[str]:
    """Split a string-or-sequence argument into non-empty comma-free tokens."""
    if isinstance(value, str):
        raw: Iterable[str] = value.split(",")
    elif isinstance(value, (bytes, bytearray)):
        raise ValidationError(f"{name} must be a string or a sequence of strings.")
    elif isinstance(value, _AbcSequence):
        parts: List[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValidationError(
                    f"{name} entries must be strings; got {type(item).__name__}."
                )
            parts.extend(item.split(","))
        raw = parts
    else:
        raise ValidationError(f"{name} must be a string or a sequence of strings.")

    tokens = [token.strip() for token in raw]
    tokens = [token for token in tokens if token]
    if not tokens:
        raise ValidationError(f"{name} must name at least one field.")
    return tokens
