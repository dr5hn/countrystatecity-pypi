"""Shared helpers for the API client test suite.

Every test drives the client through ``httpx.MockTransport``. No test needs a
real API key, and no test opens a socket.
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar

import httpx

from countrystatecity import AsyncCountryStateCity, CountryStateCity

#: A key that is well-formed but obviously fake, so a leak is easy to spot.
TEST_API_KEY = "test-key-0123456789abcdef0123456789abcdef0123456789ab"

T = TypeVar("T")

Handler = Callable[[httpx.Request], httpx.Response]


class Recorder:
    """Captures every request the client sends and replies with a canned response."""

    def __init__(
        self,
        *,
        status_code: int = 200,
        json_body: Any = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        raises: Optional[BaseException] = None,
    ) -> None:
        """Configure the canned reply.

        Args:
            status_code: Status to return.
            json_body: Body to serialise as JSON. Ignored when ``text`` is set.
            text: Raw body, for testing non-JSON responses.
            headers: Response headers.
            raises: Exception to raise instead of replying, for transport tests.
        """
        self.status_code = status_code
        self.json_body = json_body
        self.text = text
        self.headers = headers or {}
        self.raises = raises
        self.requests: List[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        """Record ``request`` and return the configured response."""
        self.requests.append(request)
        if self.raises is not None:
            raise self.raises
        if self.text is not None:
            return httpx.Response(
                self.status_code, text=self.text, headers=self.headers
            )
        return httpx.Response(
            self.status_code, json=self.json_body, headers=self.headers
        )

    @property
    def request(self) -> httpx.Request:
        """The single request that was sent.

        Raises:
            AssertionError: If zero or more than one request was recorded.
        """
        assert len(self.requests) == 1, f"expected 1 request, got {len(self.requests)}"
        return self.requests[0]


def sync_client(recorder: Recorder, **kwargs: Any) -> CountryStateCity:
    """Build a sync client wired to ``recorder``."""
    kwargs.setdefault("api_key", TEST_API_KEY)
    return CountryStateCity(transport=httpx.MockTransport(recorder), **kwargs)


def async_client(recorder: Recorder, **kwargs: Any) -> AsyncCountryStateCity:
    """Build an async client wired to ``recorder``."""
    kwargs.setdefault("api_key", TEST_API_KEY)
    return AsyncCountryStateCity(transport=httpx.MockTransport(recorder), **kwargs)


def run(coro: Awaitable[T]) -> T:
    """Run one coroutine to completion.

    Keeps the suite free of an async test-runner plugin: the async client's
    behaviour is exercised through ordinary sync test functions.

    Args:
        coro: The coroutine to await.

    Returns:
        Whatever the coroutine returned.
    """

    async def _wrapper() -> T:
        return await coro

    return asyncio.run(_wrapper())
