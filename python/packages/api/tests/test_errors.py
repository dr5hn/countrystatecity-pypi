"""HTTP and transport failures surface as structured, actionable exceptions.

The API answers with two different error envelopes depending on which layer
rejected the request, so every status is exercised in both shapes. Bodies that
are not JSON at all -- Express's HTML 404, a proxy's 502 page -- must still
produce a usable message rather than a decode crash.
"""

from typing import Any, Dict, Type

import httpx
import pytest

from countrystatecity import (
    APIConnectionError,
    APIResponseError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
)

from .helpers import TEST_API_KEY, Recorder, async_client, run, sync_client

#: Envelope emitted by the API's global error handler.
GLOBAL_ENVELOPE = {
    "status": "error",
    "message": "This feature is not available on your current plan.",
    "details": {
        "feature": "bulkStates",
        "upgradeUrl": "https://app.countrystatecity.in/pricing",
    },
}

#: Flat envelope emitted by several controllers and by the OpenAPI contract.
FLAT_ENVELOPE = {
    "error": "This feature is not available on your current plan.",
    "feature": "bulkStates",
    "upgradeUrl": "https://app.countrystatecity.in/pricing",
}

STATUS_CASES = [
    (400, BadRequestError),
    (401, AuthenticationError),
    (403, PermissionDeniedError),
    (404, NotFoundError),
    (429, RateLimitError),
    (500, ServerError),
    (502, ServerError),
    (503, ServerError),
]


@pytest.mark.parametrize("status, expected", STATUS_CASES)
def test_sync_status_maps_to_its_error_class(
    status: int, expected: Type[APIStatusError]
) -> None:
    recorder = Recorder(status_code=status, json_body={"error": "nope"})
    with sync_client(recorder) as client:
        with pytest.raises(expected) as caught:
            client.get_countries()

    assert caught.value.status_code == status
    assert str(caught.value).startswith(f"[{status}] ")


@pytest.mark.parametrize("status, expected", STATUS_CASES)
def test_async_status_maps_to_its_error_class(
    status: int, expected: Type[APIStatusError]
) -> None:
    recorder = Recorder(status_code=status, json_body={"error": "nope"})
    client = async_client(recorder)
    try:
        with pytest.raises(expected) as caught:
            run(client.get_countries())
    finally:
        run(client.aclose())

    assert caught.value.status_code == status


def test_unmapped_status_falls_back_to_the_base_class() -> None:
    recorder = Recorder(status_code=418, json_body={"error": "teapot"})
    with sync_client(recorder) as client:
        with pytest.raises(APIStatusError) as caught:
            client.get_countries()

    assert type(caught.value) is APIStatusError
    assert caught.value.status_code == 418


def test_missing_api_key_message_is_preserved() -> None:
    """Matches the live response from an unauthenticated /v1 request."""
    recorder = Recorder(
        status_code=401,
        json_body={"status": "error", "message": "API key is required"},
    )
    with sync_client(recorder) as client:
        with pytest.raises(AuthenticationError) as caught:
            client.get_countries()

    assert "API key is required" in str(caught.value)
    assert caught.value.details == {}


@pytest.mark.parametrize(
    "body", [GLOBAL_ENVELOPE, FLAT_ENVELOPE], ids=["global-envelope", "flat-envelope"]
)
def test_plan_restriction_exposes_feature_and_upgrade_url(body: Dict[str, Any]) -> None:
    """Both envelopes must yield the same accessors."""
    recorder = Recorder(status_code=403, json_body=body)
    with sync_client(recorder) as client:
        with pytest.raises(PermissionDeniedError) as caught:
            client.get_states()

    error = caught.value
    assert error.feature == "bulkStates"
    assert error.upgrade_url == "https://app.countrystatecity.in/pricing"
    assert "not available on your current plan" in str(error)


def test_tier_restriction_exposes_required_and_current_tier() -> None:
    recorder = Recorder(
        status_code=403,
        json_body={
            "status": "error",
            "message": "Your current plan does not include this endpoint.",
            "details": {
                "requiredTier": "supporter",
                "currentTier": "community",
                "upgradeUrl": "https://app.countrystatecity.in/pricing",
            },
        },
    )
    with sync_client(recorder) as client:
        with pytest.raises(PermissionDeniedError) as caught:
            client.get_regions()

    assert caught.value.required_tier == "supporter"
    assert caught.value.current_tier == "community"


@pytest.mark.parametrize(
    "body",
    [
        {
            "status": "error",
            "message": "Daily usage limit exceeded.",
            "details": {
                "limit": 100,
                "period": "daily",
                "tier": "community",
                "upgradeUrl": "https://app.countrystatecity.in/pricing",
            },
        },
        {
            "error": "Daily usage limit exceeded.",
            "limit": 100,
            "period": "daily",
            "tier": "community",
            "upgradeUrl": "https://app.countrystatecity.in/pricing",
        },
    ],
    ids=["global-envelope", "flat-envelope"],
)
def test_rate_limit_exposes_quota_detail(body: Dict[str, Any]) -> None:
    recorder = Recorder(status_code=429, json_body=body)
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError) as caught:
            client.get_countries()

    error = caught.value
    assert error.limit == 100
    assert error.period == "daily"
    assert error.tier == "community"
    assert error.upgrade_url == "https://app.countrystatecity.in/pricing"


def test_rate_limit_detail_survives_a_string_limit() -> None:
    """The limit is coerced, not assumed to already be an int."""
    recorder = Recorder(
        status_code=429, json_body={"error": "too many", "limit": "250"}
    )
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError) as caught:
            client.get_countries()

    assert caught.value.limit == 250


def test_rate_limit_detail_is_none_when_unparsable() -> None:
    recorder = Recorder(
        status_code=429, json_body={"error": "too many", "limit": "lots"}
    )
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError) as caught:
            client.get_countries()

    assert caught.value.limit is None
    assert caught.value.details["limit"] == "lots"


def test_controller_404_uses_the_flat_envelope() -> None:
    """/countries/{ciso} answers 404 as {"error": ...}, not the global shape."""
    recorder = Recorder(status_code=404, json_body={"error": "Country not found."})
    with sync_client(recorder) as client:
        with pytest.raises(NotFoundError) as caught:
            client.get_country("ZZ")

    assert "Country not found." in str(caught.value)


def test_timezone_404_uses_the_global_envelope() -> None:
    """/timezone/* routes 404s through the global handler instead."""
    recorder = Recorder(
        status_code=404,
        json_body={"status": "error", "message": "No timezone data available."},
    )
    with sync_client(recorder) as client:
        with pytest.raises(NotFoundError) as caught:
            client.get_timezone_of_country("ZZ")

    assert "No timezone data available." in str(caught.value)


def test_html_error_body_still_yields_a_message() -> None:
    """An unknown /v1 path returns Express's HTML 404, not JSON."""
    recorder = Recorder(
        status_code=404,
        text="<!DOCTYPE html><html><body><pre>Cannot GET /v1/nope</pre></body></html>",
        headers={"content-type": "text/html; charset=utf-8"},
    )
    with sync_client(recorder) as client:
        with pytest.raises(NotFoundError) as caught:
            client.request("/nope")

    assert "404" in str(caught.value)
    assert "Cannot GET /v1/nope" in str(caught.value)


def test_long_non_json_error_body_is_truncated() -> None:
    recorder = Recorder(status_code=502, text="x" * 5000)
    with sync_client(recorder) as client:
        with pytest.raises(ServerError) as caught:
            client.get_countries()

    assert len(str(caught.value)) < 400
    assert str(caught.value).endswith("...")


def test_empty_error_body_yields_a_status_message() -> None:
    recorder = Recorder(status_code=503, text="")
    with sync_client(recorder) as client:
        with pytest.raises(ServerError) as caught:
            client.get_countries()

    assert "503" in str(caught.value)


def test_error_records_method_and_url() -> None:
    recorder = Recorder(status_code=404, json_body={"error": "nope"})
    with sync_client(recorder) as client:
        with pytest.raises(NotFoundError) as caught:
            client.get_country("ZZ")

    assert caught.value.method == "GET"
    assert caught.value.url == "https://api.countrystatecity.in/v1/countries/ZZ"


def test_success_with_a_non_json_body_raises_a_response_error() -> None:
    recorder = Recorder(status_code=200, text="not json at all")
    with sync_client(recorder) as client:
        with pytest.raises(APIResponseError) as caught:
            client.get_countries()

    assert caught.value.status_code == 200
    assert "not json at all" in caught.value.body


def test_connection_failure_raises_api_connection_error() -> None:
    cause = httpx.ConnectError("dns failure")
    recorder = Recorder(raises=cause)
    with sync_client(recorder) as client:
        with pytest.raises(APIConnectionError) as caught:
            client.get_countries()

    assert not isinstance(caught.value, APITimeoutError)
    assert caught.value.cause is cause
    assert "https://api.countrystatecity.in/v1/countries" in str(caught.value)


@pytest.mark.parametrize(
    "exc",
    [
        httpx.ConnectTimeout("connect timed out"),
        httpx.ReadTimeout("read timed out"),
        httpx.PoolTimeout("pool timed out"),
    ],
    ids=["connect", "read", "pool"],
)
def test_timeouts_raise_api_timeout_error(exc: httpx.TimeoutException) -> None:
    recorder = Recorder(raises=exc)
    with sync_client(recorder) as client:
        with pytest.raises(APITimeoutError) as caught:
            client.get_countries()

    assert isinstance(caught.value, APIConnectionError)
    assert caught.value.cause is exc


def test_async_timeout_raises_api_timeout_error() -> None:
    exc = httpx.ReadTimeout("read timed out")
    recorder = Recorder(raises=exc)
    client = async_client(recorder)
    try:
        with pytest.raises(APITimeoutError):
            run(client.get_countries())
    finally:
        run(client.aclose())


def test_async_connection_failure_raises_api_connection_error() -> None:
    recorder = Recorder(raises=httpx.ConnectError("refused"))
    client = async_client(recorder)
    try:
        with pytest.raises(APIConnectionError):
            run(client.get_countries())
    finally:
        run(client.aclose())


def test_transport_error_message_never_contains_the_api_key() -> None:
    recorder = Recorder(raises=httpx.ConnectError("refused"))
    with sync_client(recorder) as client:
        with pytest.raises(APIConnectionError) as caught:
            client.get_countries()

    assert TEST_API_KEY not in str(caught.value)


def test_status_error_message_never_contains_the_api_key() -> None:
    recorder = Recorder(status_code=401, json_body={"error": "Invalid API key"})
    with sync_client(recorder) as client:
        with pytest.raises(AuthenticationError) as caught:
            client.get_countries()

    assert TEST_API_KEY not in str(caught.value)
    assert TEST_API_KEY not in repr(caught.value)
    assert TEST_API_KEY not in caught.value.url


def test_client_does_not_retry_a_server_error() -> None:
    """A silent retry would spend a second request from the caller's quota."""
    recorder = Recorder(status_code=500, json_body={"error": "boom"})
    with sync_client(recorder) as client:
        with pytest.raises(ServerError):
            client.get_countries()

    assert len(recorder.requests) == 1


def test_client_does_not_retry_a_rate_limit() -> None:
    recorder = Recorder(status_code=429, json_body={"error": "slow down"})
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError):
            client.get_countries()

    assert len(recorder.requests) == 1


def test_json_string_error_body_is_used_as_the_message() -> None:
    """Some proxies answer with a bare JSON string rather than an object."""
    recorder = Recorder(status_code=503, json_body="upstream unavailable")
    with sync_client(recorder) as client:
        with pytest.raises(ServerError) as caught:
            client.get_countries()

    assert "upstream unavailable" in str(caught.value)


def test_non_string_message_field_falls_back_to_the_status_line() -> None:
    recorder = Recorder(status_code=500, json_body={"message": 42, "error": None})
    with sync_client(recorder) as client:
        with pytest.raises(ServerError) as caught:
            client.get_countries()

    assert "500" in str(caught.value)


def test_rate_limit_accessors_are_none_without_detail() -> None:
    recorder = Recorder(status_code=429, json_body={"error": "slow down"})
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError) as caught:
            client.get_countries()

    error = caught.value
    assert error.limit is None
    assert error.period is None
    assert error.tier is None
    assert error.upgrade_url is None


def test_rate_limit_exposes_the_reset_time() -> None:
    """The API reports resetAt on 429; callers schedule their backoff on it."""
    recorder = Recorder(
        status_code=429,
        json_body={
            "status": "error",
            "message": "Daily usage limit exceeded.",
            "details": {
                "limit": 100,
                "period": "daily",
                "resetAt": "2026-08-23T00:00:00.000Z",
                "tier": "community",
                "upgradeUrl": "https://app.countrystatecity.in/pricing",
            },
        },
    )
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError) as caught:
            client.get_countries()

    assert caught.value.reset_at == "2026-08-23T00:00:00.000Z"


def test_rate_limit_reset_time_survives_the_flat_envelope() -> None:
    """Controllers that answer flat must yield the same accessor."""
    recorder = Recorder(
        status_code=429,
        json_body={
            "error": "Monthly usage limit exceeded.",
            "limit": 5000,
            "period": "monthly",
            "resetAt": "2026-09-01T00:00:00.000Z",
        },
    )
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError) as caught:
            client.get_countries()

    assert caught.value.reset_at == "2026-09-01T00:00:00.000Z"
    assert caught.value.period == "monthly"


def test_rate_limit_reset_time_is_none_when_absent() -> None:
    recorder = Recorder(status_code=429, json_body={"error": "slow down"})
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError) as caught:
            client.get_countries()

    assert caught.value.reset_at is None


# -- query values never reach an exception ---------------------------------
#
# Every query value this client sends is caller data. `/phone/parse?number=` is
# a phone number, `?q=` is whatever a user typed, and a caller can put anything
# through `request(params=...)`. Exceptions get printed, logged, and shipped to
# error trackers, so the recorded URL keeps scheme, host, and path and drops the
# query string entirely. The request itself still carries it.

#: A phone number, a search term, and a token-shaped string -- the three kinds
#: of query value that must not survive into an exception.
SECRET_PHONE = "+14155552671"
SECRET_QUERY = "12 Mornington Crescent"
SECRET_TOKEN = "token-shaped-SENTINEL-abc123"


def wire_form(secret: str) -> str:
    """Return ``secret`` exactly as httpx percent-encodes it into a query.

    Asserting on the raw string alone would be a weak test: " " becomes "+" and
    "+" becomes "%2B" on the wire, so a leaked URL might not contain the secret
    verbatim even though it fully discloses it.
    """
    return str(httpx.QueryParams({"v": secret})).split("=", 1)[1]


def assert_no_leak(secret: str, *renderings: str) -> None:
    """Assert no rendering discloses ``secret`` in raw or percent-encoded form."""
    for rendered in renderings:
        assert secret not in rendered, rendered
        assert wire_form(secret) not in rendered, rendered


#: ``(label, call)`` pairs, each sending one secret as a query value.
LEAK_CALLS = [
    ("phone-parse", lambda c: c.parse_phone_number(SECRET_PHONE), SECRET_PHONE),
    ("search-q", lambda c: c.get_cities_of_country("IN", q=SECRET_QUERY), SECRET_QUERY),
    ("fuzzy-q", lambda c: c.fuzzy_search(SECRET_QUERY), SECRET_QUERY),
    (
        "raw-params",
        lambda c: c.request("/some/future/route", params={"token": SECRET_TOKEN}),
        SECRET_TOKEN,
    ),
]
LEAK_IDS = [case[0] for case in LEAK_CALLS]


@pytest.mark.parametrize("_label, call, secret", LEAK_CALLS, ids=LEAK_IDS)
def test_status_error_never_records_a_query_value(
    _label: str, call: Any, secret: str
) -> None:
    recorder = Recorder(status_code=500, json_body={"error": "boom"})
    with sync_client(recorder) as client:
        with pytest.raises(ServerError) as caught:
            call(client)

    error = caught.value
    assert_no_leak(secret, error.url, str(error), repr(error))
    assert httpx.URL(error.url).query == b"", error.url


@pytest.mark.parametrize("_label, call, secret", LEAK_CALLS, ids=LEAK_IDS)
def test_transport_error_never_records_a_query_value(
    _label: str, call: Any, secret: str
) -> None:
    recorder = Recorder(raises=httpx.ConnectError("refused"))
    with sync_client(recorder) as client:
        with pytest.raises(APIConnectionError) as caught:
            call(client)

    assert_no_leak(secret, str(caught.value), repr(caught.value))


@pytest.mark.parametrize("_label, call, secret", LEAK_CALLS, ids=LEAK_IDS)
def test_async_status_error_never_records_a_query_value(
    _label: str, call: Any, secret: str
) -> None:
    recorder = Recorder(status_code=503, json_body={"error": "boom"})
    client = async_client(recorder)
    try:
        with pytest.raises(ServerError) as caught:
            run(call(client))
    finally:
        run(client.aclose())

    error = caught.value
    assert_no_leak(secret, error.url, str(error))
    assert httpx.URL(error.url).query == b"", error.url


@pytest.mark.parametrize("_label, call, secret", LEAK_CALLS, ids=LEAK_IDS)
def test_async_transport_error_never_records_a_query_value(
    _label: str, call: Any, secret: str
) -> None:
    recorder = Recorder(raises=httpx.ReadTimeout("timed out"))
    client = async_client(recorder)
    try:
        with pytest.raises(APITimeoutError) as caught:
            run(call(client))
    finally:
        run(client.aclose())

    assert_no_leak(secret, str(caught.value))


@pytest.mark.parametrize("_label, call, secret", LEAK_CALLS, ids=LEAK_IDS)
def test_the_request_itself_still_carries_the_query_value(
    _label: str, call: Any, secret: str
) -> None:
    """Redaction is on the recorded URL only -- the API still gets the query."""
    recorder = Recorder(status_code=500, json_body={"error": "boom"})
    with sync_client(recorder) as client:
        with pytest.raises(ServerError):
            call(client)

    # Compared against the decoded params, because the wire form is
    # percent-encoded ("+" -> "%2B", " " -> "+").
    assert secret in dict(recorder.request.url.params).values()


def test_error_url_keeps_the_path_it_dropped_the_query_from() -> None:
    """Dropping the query must not cost the diagnostic value of the URL."""
    recorder = Recorder(status_code=404, json_body={"error": "nope"})
    with sync_client(recorder) as client:
        with pytest.raises(NotFoundError) as caught:
            client.parse_phone_number(SECRET_PHONE)

    assert caught.value.url == "https://api.countrystatecity.in/v1/phone/parse"
    assert caught.value.method == "GET"
    assert "phone/parse" in str(caught.value.url)


def test_error_url_drops_a_fragment_too() -> None:
    """The defensive URL reducer also removes fragments."""
    from countrystatecity._core import loggable_url

    assert loggable_url("https://api.example.test/v1/countries#frag") == (
        "https://api.example.test/v1/countries"
    )
