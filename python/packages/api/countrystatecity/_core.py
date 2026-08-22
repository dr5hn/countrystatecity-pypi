"""Configuration, response decoding, and error mapping shared by both clients.

Everything in here is transport-agnostic: it never awaits and never blocks, so
:mod:`countrystatecity.client` and :mod:`countrystatecity.aio` run identical
logic and differ only in how they hand a request to httpx.
"""

import math
import os
from typing import Any, Dict, Mapping, Optional, Tuple, Union
from urllib.parse import urlsplit, urlunsplit

import httpx

from ._validation import api_key as validate_api_key
from ._version import __version__
from .errors import (
    APIConnectionError,
    APIResponseError,
    APITimeoutError,
    ConfigurationError,
    ValidationError,
    status_error_class,
)
from .response import ApiResponse, ResponseMeta

__all__ = [
    "API_KEY_ENV_VAR",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "USER_AGENT",
    "loggable_url",
]

#: Production API root. Every endpoint path in this package is relative to it.
DEFAULT_BASE_URL = "https://api.countrystatecity.in/v1"

#: Environment variable read when no ``api_key`` argument is given.
API_KEY_ENV_VAR = "CSC_API_KEY"

#: Header the API authenticates with.
API_KEY_HEADER = "X-CSCAPI-KEY"

#: Total seconds allowed per request. Finite by design: an unbounded client can
#: wedge a worker forever on a stalled connection.
DEFAULT_TIMEOUT = 30.0

USER_AGENT = f"countrystatecity-python/{__version__}"

#: Keys that carry the message itself rather than structured error detail.
_ENVELOPE_KEYS = frozenset({"status", "message", "error", "details"})

#: How much of a non-JSON error body to quote back in the exception message.
_BODY_SNIPPET = 200


def resolve_api_key(api_key: Optional[str]) -> str:
    """Resolve and validate the API key before any network I/O.

    Args:
        api_key: An explicit key, or ``None`` to read the ``CSC_API_KEY``
            environment variable.

    Returns:
        The validated key.

    Raises:
        ConfigurationError: If no usable key is available.
    """
    candidate = api_key if api_key is not None else os.environ.get(API_KEY_ENV_VAR)
    try:
        return validate_api_key(candidate, env_var=API_KEY_ENV_VAR)
    except ValidationError as exc:
        raise ConfigurationError(str(exc)) from None


def normalize_base_url(base_url: str) -> str:
    """Validate a base URL and strip its trailing slash.

    Args:
        base_url: Absolute ``http`` or ``https`` URL for the API root.

    Returns:
        The URL without a trailing slash.

    Raises:
        ConfigurationError: If the URL is blank, relative, or uses a scheme
            other than ``http``/``https``. The API key is sent to whatever host
            this names, so anything unrecognisable is rejected outright.
    """
    if not isinstance(base_url, str) or not base_url.strip():
        raise ConfigurationError("base_url must be a non-empty string.")
    cleaned = base_url.strip().rstrip("/")
    parts = urlsplit(cleaned)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ConfigurationError(
            "base_url must be an absolute http(s) URL, e.g. "
            f"{DEFAULT_BASE_URL!r}; got {base_url!r}."
        )
    return cleaned


def normalize_timeout(timeout: Union[int, float, httpx.Timeout]) -> httpx.Timeout:
    """Validate the request timeout and return it as an ``httpx.Timeout``.

    Args:
        timeout: Seconds as a positive finite number, or a fully-specified
            ``httpx.Timeout``.

    Returns:
        The normalised timeout.

    Raises:
        ConfigurationError: If the timeout is non-positive, non-finite, or an
            ``httpx.Timeout`` with a ``None`` component. Disabling the timeout
            is not supported.
    """
    if isinstance(timeout, httpx.Timeout):
        for phase in ("connect", "read", "write", "pool"):
            if getattr(timeout, phase, None) is None:
                raise ConfigurationError(
                    f"timeout.{phase} must not be None; this client requires a "
                    "finite timeout on every phase."
                )
        return timeout
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ConfigurationError(
            "timeout must be a number of seconds or an httpx.Timeout; got "
            f"{type(timeout).__name__}."
        )
    if not math.isfinite(timeout) or timeout <= 0:
        raise ConfigurationError(
            f"timeout must be a positive, finite number of seconds; got {timeout!r}."
        )
    return httpx.Timeout(float(timeout))


def loggable_url(url: Union[str, httpx.URL]) -> str:
    """Reduce a request URL to the part that is safe to record and log.

    Every query value this client sends comes from the caller, and some of it is
    sensitive: ``/phone/parse?number=`` carries a phone number, ``?q=`` carries
    a user's search term, and a future endpoint could carry anything. Exceptions
    are printed, logged, and shipped to error trackers, so the query string and
    fragment are dropped entirely rather than filtered key by key -- a
    deny-list would silently leak the next parameter nobody remembered to add.

    Only the recorded URL changes. The request itself is built and sent with its
    full query string.

    Args:
        url: The absolute URL of a prepared request.

    Returns:
        The same URL with its query and fragment removed. The API key is never
        part of a URL to begin with -- it travels in the ``X-CSCAPI-KEY``
        header.
    """
    parts = urlsplit(str(url))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def build_headers(api_key: str) -> Dict[str, str]:
    """Build the default headers for every request.

    Args:
        api_key: The validated API key.

    Returns:
        Headers carrying the key, the JSON ``Accept``, and the client's
        ``User-Agent``.
    """
    return {
        API_KEY_HEADER: api_key,
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }


def process_response(
    response: httpx.Response, *, method: str, url: str
) -> ApiResponse[Any]:
    """Decode a response, or raise the error class that models its status.

    Args:
        response: A fully-read httpx response.
        method: HTTP method, recorded on any raised error.
        url: Request URL recorded on any raised error. Pass the value returned
            by :func:`loggable_url`, which carries no query or fragment.

    Returns:
        The decoded body wrapped with its plan, quota, and cache metadata.

    Raises:
        APIResponseError: If a success response did not contain valid JSON.
        APIStatusError: For any non-2xx status, as the subclass matching it.
    """
    meta = ResponseMeta.from_headers(response.headers)

    if response.is_success:
        try:
            data = response.json()
        except ValueError as exc:
            raise APIResponseError(
                "The API returned a successful status with a body that is not "
                "valid JSON.",
                status_code=response.status_code,
                body=_snippet(response),
            ) from exc
        return ApiResponse(data=data, status_code=response.status_code, meta=meta)

    message, details = extract_error(response)
    raise status_error_class(response.status_code)(
        message,
        status_code=response.status_code,
        details=details,
        meta=meta,
        method=method,
        url=url,
    )


def extract_error(response: httpx.Response) -> Tuple[str, Dict[str, Any]]:
    """Pull a message and structured detail out of an error response.

    The API uses two error envelopes. The global handler returns
    ``{"status": "error", "message": ..., "details": {...}}``; several
    controllers return a flat ``{"error": ...}`` alongside top-level fields such
    as ``feature`` or ``limit``. Both are normalised here so callers see one
    shape regardless of which produced the error, and a body that is not JSON at
    all (an HTML 404 or a proxy's 502 page) still yields a usable message.

    Args:
        response: The error response.

    Returns:
        A ``(message, details)`` pair. ``details`` is never ``None``.
    """
    payload: Any
    try:
        payload = response.json()
    except ValueError:
        payload = None

    details: Dict[str, Any] = {}
    message: Optional[str] = None

    if isinstance(payload, dict):
        raw_details = payload.get("details")
        if isinstance(raw_details, dict):
            details.update(raw_details)
        for key, value in payload.items():
            if key not in _ENVELOPE_KEYS and key not in details:
                details[key] = value
        message = _first_text(payload.get("message"), payload.get("error"))
    elif isinstance(payload, str) and payload.strip():
        message = payload.strip()

    if message is None:
        snippet = _snippet(response)
        reason = response.reason_phrase or "error"
        message = f"HTTP {response.status_code} {reason}".strip()
        if snippet:
            message = f"{message}: {snippet}"

    return message, details


def translate_transport_error(
    exc: httpx.HTTPError, *, method: str, url: str
) -> APIConnectionError:
    """Convert an httpx transport failure into this package's error type.

    Args:
        exc: The httpx exception. Only transport-level errors reach here;
            status errors are handled by :func:`process_response`.
        method: HTTP method of the failed request.
        url: Request URL of the failed request. Pass the value returned by
            :func:`loggable_url`: this message names the target, and a raw URL
            would put the caller's query values into every log line.

    Returns:
        An :class:`~countrystatecity.errors.APITimeoutError` for timeouts, and
        an :class:`~countrystatecity.errors.APIConnectionError` otherwise. The
        original exception is preserved on ``.cause``.
    """
    where = f"{method} {url}"
    if isinstance(exc, httpx.TimeoutException):
        return APITimeoutError(f"Request timed out: {where} ({exc})", cause=exc)
    return APIConnectionError(f"Could not reach the API: {where} ({exc})", cause=exc)


def redacted_repr(class_name: str, base_url: str, timeout: httpx.Timeout) -> str:
    """Build a ``repr`` that never contains the API key.

    Args:
        class_name: Name of the client class.
        base_url: The client's base URL.
        timeout: The client's timeout.

    Returns:
        A representation safe to write to logs and tracebacks.
    """
    return f"{class_name}(base_url={base_url!r}, timeout={timeout!r}, api_key=***)"


def _first_text(*candidates: Any) -> Optional[str]:
    """Return the first candidate that is a non-blank string."""
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def _snippet(response: httpx.Response) -> str:
    """Return a short, single-line excerpt of a response body for messages."""
    try:
        text = response.text
    except Exception:  # pragma: no cover - body already read in practice
        return ""
    collapsed = " ".join(text.split())
    if len(collapsed) <= _BODY_SNIPPET:
        return collapsed
    return collapsed[:_BODY_SNIPPET] + "..."


def merge_headers(
    defaults: Mapping[str, str], extra: Optional[Mapping[str, str]]
) -> Dict[str, str]:
    """Merge caller-supplied headers over the defaults.

    Args:
        defaults: Headers built by :func:`build_headers`.
        extra: Additional headers, or ``None``.

    Returns:
        The merged mapping.

    Raises:
        ConfigurationError: If the caller tries to override the API key header,
            which would silently defeat the key validation done at construction.
    """
    merged = dict(defaults)
    if not extra:
        return merged
    for key, value in extra.items():
        if key.lower() == API_KEY_HEADER.lower():
            raise ConfigurationError(
                f"Set the API key with api_key=..., not a {API_KEY_HEADER} header."
            )
        merged[key] = value
    return merged
