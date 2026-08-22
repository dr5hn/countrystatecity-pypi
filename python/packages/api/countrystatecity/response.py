"""Response metadata read from Country State City API headers.

Every ``/v1/*`` response carries the caller's plan, quota consumption, and
cache disposition in headers. These classes surface them without a second API
call, so an application can log or alarm on quota burn from the response it
already has.
"""

from dataclasses import dataclass, field
from typing import Generic, Mapping, Optional, TypeVar

__all__ = ["ApiResponse", "Quota", "ResponseMeta"]

T = TypeVar("T")

_UNLIMITED = "unlimited"


@dataclass(frozen=True)
class Quota:
    """Usage against one of the plan's request limits.

    Attributes:
        used: Requests consumed in the period, or ``None`` if the API did not
            report it (for example on a ``401``, which is rejected before the
            usage headers are set).
        limit: The ceiling for the period, or ``None`` when the plan is
            unlimited or the API did not report a limit.
        unlimited: ``True`` when the API reported the literal ``"unlimited"``.
    """

    used: Optional[int] = None
    limit: Optional[int] = None
    unlimited: bool = False

    @property
    def remaining(self) -> Optional[int]:
        """Requests left in the period, or ``None`` when it cannot be computed.

        Returns ``None`` for unlimited plans and whenever either ``used`` or
        ``limit`` is missing. Never returns a negative number.
        """
        if self.unlimited or self.used is None or self.limit is None:
            return None
        return max(self.limit - self.used, 0)


@dataclass(frozen=True)
class ResponseMeta:
    """Plan, quota, and cache metadata for a single API response.

    Attributes:
        plan: Value of ``X-CSC-Plan`` -- the tier the API resolved for the key.
        daily: Usage against the daily quota (``X-CSC-Daily-*``).
        monthly: Usage against the monthly quota (``X-CSC-Monthly-*``).
        cache: Value of ``X-Cache`` -- ``"HIT"`` or ``"MISS"``. ``None`` on
            endpoints that do not cache responses, such as ``/phone/parse``.
        etag: Value of ``ETag``, usable as ``If-None-Match`` on a later request.
        cache_control: Value of ``Cache-Control``.
        headers: All response headers, lowercased and case-insensitive on
            lookup via the underlying HTTP library.
    """

    plan: Optional[str] = None
    daily: Quota = field(default_factory=Quota)
    monthly: Quota = field(default_factory=Quota)
    cache: Optional[str] = None
    etag: Optional[str] = None
    cache_control: Optional[str] = None
    headers: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> "ResponseMeta":
        """Build metadata from a response's headers.

        Missing or unparsable headers degrade to ``None`` rather than raising:
        metadata is diagnostic, and a malformed header must never turn a
        successful API response into an application error.

        Args:
            headers: Response headers. Lookup is expected to be
                case-insensitive, as it is for ``httpx.Headers``.

        Returns:
            A populated :class:`ResponseMeta`.
        """
        return cls(
            plan=headers.get("X-CSC-Plan"),
            daily=_quota(headers, "X-CSC-Daily-Used", "X-CSC-Daily-Limit"),
            monthly=_quota(headers, "X-CSC-Monthly-Used", "X-CSC-Monthly-Limit"),
            cache=headers.get("X-Cache"),
            etag=headers.get("ETag"),
            cache_control=headers.get("Cache-Control"),
            headers=headers,
        )


@dataclass(frozen=True)
class ApiResponse(Generic[T]):
    """A decoded API response together with its metadata.

    Returned by the low-level :meth:`~countrystatecity.CountryStateCity.request`
    escape hatch. The typed endpoint methods return :attr:`data` directly.

    Attributes:
        data: The decoded JSON body.
        status_code: HTTP status code (always ``2xx``; other statuses raise).
        meta: Plan, quota, and cache metadata for this response.
    """

    data: T
    status_code: int
    meta: ResponseMeta


def _quota(headers: Mapping[str, str], used_header: str, limit_header: str) -> Quota:
    """Read one used/limit header pair into a :class:`Quota`."""
    raw_limit = headers.get(limit_header)
    unlimited = raw_limit is not None and raw_limit.strip().lower() == _UNLIMITED
    return Quota(
        used=_int_or_none(headers.get(used_header)),
        limit=None if unlimited else _int_or_none(raw_limit),
        unlimited=unlimited,
    )


def _int_or_none(raw: Optional[str]) -> Optional[int]:
    """Parse a header value as an int, returning ``None`` when it is not one."""
    if raw is None:
        return None
    try:
        return int(raw.strip())
    except ValueError:
        return None
