"""Structured exceptions raised by the Country State City API client.

Every failure mode raises a subclass of :class:`CountryStateCityError`, so a
single ``except CountryStateCityError`` clause is enough to contain the client.
More specific classes let callers branch on the failure they care about --
quota exhaustion, plan restrictions, or an unreachable network.
"""

from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Type

if TYPE_CHECKING:  # pragma: no cover - import cycle guard, types only
    from .response import ResponseMeta

__all__ = [
    "APIConnectionError",
    "APIResponseError",
    "APIStatusError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "ConfigurationError",
    "CountryStateCityError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    "status_error_class",
]


class CountryStateCityError(Exception):
    """Base class for every error raised by this package."""


class ConfigurationError(CountryStateCityError):
    """The client was constructed with settings it cannot use.

    Raised for a missing or blank API key, an unusable base URL, or a
    non-finite timeout. Always raised before any network I/O so a misconfigured
    deployment fails immediately rather than at first request.
    """


class ValidationError(CountryStateCityError, ValueError):
    """An argument failed client-side validation.

    Path and query inputs are checked against the same rules the production API
    enforces, so a malformed call fails locally instead of spending request
    quota on a guaranteed ``400``.
    """


class APIConnectionError(CountryStateCityError):
    """The request never produced an HTTP response.

    Covers DNS failures, refused connections, TLS errors, and truncated
    responses. The originating exception is available on :attr:`cause`.
    """

    def __init__(self, message: str, *, cause: Optional[BaseException] = None) -> None:
        super().__init__(message)
        self.cause = cause


class APITimeoutError(APIConnectionError):
    """The request exceeded the client's configured timeout."""


class APIResponseError(CountryStateCityError):
    """The API returned a success status with a body that is not valid JSON."""

    def __init__(self, message: str, *, status_code: int, body: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class APIStatusError(CountryStateCityError):
    """The API returned a non-2xx HTTP status.

    Attributes:
        status_code: The HTTP status code.
        details: Structured fields the API attached to the error. The API uses
            two error envelopes -- ``{"status", "message", "details"}`` from the
            global handler and a flat ``{"error", ...}`` from some controllers.
            Both are flattened into this single mapping, so keys such as
            ``feature``, ``upgradeUrl``, ``tier``, ``limit``, and ``period`` are
            available regardless of which envelope produced them.
        meta: Plan, quota, and cache metadata read from the response headers.
            Mostly empty on ``401``/``429``, where the API rejects the request
            before it sets those headers.
        method: HTTP method of the failed request.
        url: Scheme, host, and path of the failed request -- safe to log. The
            query string and fragment are stripped, because query values are
            caller data (``/phone/parse?number=`` is a phone number, ``?q=`` is
            a search term) and exceptions end up in logs. The API key is never
            in a URL at all; it travels in the ``X-CSCAPI-KEY`` header only.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        details: Mapping[str, Any],
        meta: "ResponseMeta",
        method: str,
        url: str,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details: Dict[str, Any] = dict(details)
        self.meta = meta
        self.method = method
        self.url = url

    def __str__(self) -> str:
        """Render the status code alongside the API's own message."""
        return f"[{self.status_code}] {super().__str__()}"

    @property
    def upgrade_url(self) -> Optional[str]:
        """Plan-upgrade URL the API suggested, when it supplied one."""
        return _as_str(self.details.get("upgradeUrl"))


class BadRequestError(APIStatusError):
    """``400`` -- the API rejected a path or query parameter."""


class AuthenticationError(APIStatusError):
    """``401`` -- the API key is missing, malformed, or unknown."""


class PermissionDeniedError(APIStatusError):
    """``403`` -- the key is valid but not entitled to this request.

    Raised for endpoints and query features gated behind a paid plan, and for
    keys blocked by their domain or IP allow-list.
    """

    @property
    def feature(self) -> Optional[str]:
        """Feature flag the API denied, e.g. ``"bulkStates"``."""
        return _as_str(self.details.get("feature"))

    @property
    def required_tier(self) -> Optional[str]:
        """Lowest tier that includes the requested endpoint, when reported."""
        return _as_str(self.details.get("requiredTier"))

    @property
    def current_tier(self) -> Optional[str]:
        """Tier the API resolved for this key, when reported."""
        return _as_str(self.details.get("currentTier"))


class NotFoundError(APIStatusError):
    """``404`` -- no resource matches the requested identifiers."""


class RateLimitError(APIStatusError):
    """``429`` -- the key exhausted its daily or monthly request quota."""

    @property
    def limit(self) -> Optional[int]:
        """Quota ceiling for the exhausted period."""
        return _as_int(self.details.get("limit"))

    @property
    def period(self) -> Optional[str]:
        """Period that ran out: ``"daily"`` or ``"monthly"``."""
        return _as_str(self.details.get("period"))

    @property
    def reset_at(self) -> Optional[str]:
        """When the exhausted period resets, as an ISO 8601 UTC timestamp.

        The API computes this from the start of the current usage window --
        the next UTC midnight for ``"daily"``, the first of the next month for
        ``"monthly"`` -- and sends it as ``resetAt``, e.g.
        ``"2026-08-23T00:00:00.000Z"``. Kept as the string the API sent rather
        than parsed to a ``datetime``: this package adds no dependencies, and
        ``datetime.fromisoformat`` did not accept a trailing ``Z`` before
        Python 3.11. Parse it with your own date library when you need to
        schedule against it.

        ``None`` when the API did not report a reset time.
        """
        return _as_str(self.details.get("resetAt"))

    @property
    def tier(self) -> Optional[str]:
        """Tier the API resolved for this key."""
        return _as_str(self.details.get("tier"))


class ServerError(APIStatusError):
    """``5xx`` -- the API failed to process an otherwise valid request."""


_STATUS_MAP: Dict[int, Type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    429: RateLimitError,
}


def status_error_class(status_code: int) -> Type[APIStatusError]:
    """Return the :class:`APIStatusError` subclass that models ``status_code``.

    Args:
        status_code: HTTP status code from the API response.

    Returns:
        The most specific ``APIStatusError`` subclass for the status, falling
        back to :class:`ServerError` for ``5xx`` and :class:`APIStatusError`
        for any other unmapped status.
    """
    mapped = _STATUS_MAP.get(status_code)
    if mapped is not None:
        return mapped
    if 500 <= status_code < 600:
        return ServerError
    return APIStatusError


def _as_str(value: Any) -> Optional[str]:
    """Return ``value`` as a string, or ``None`` when it is absent."""
    return None if value is None else str(value)


def _as_int(value: Any) -> Optional[int]:
    """Return ``value`` as an int, or ``None`` when it is absent or not numeric."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except ValueError:
        return None
