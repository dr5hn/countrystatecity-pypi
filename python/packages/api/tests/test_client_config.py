"""Construction is validated up front, and the API key never leaks.

The key is the one secret this package handles. It is checked before any socket
is opened, sent only in the ``X-CSCAPI-KEY`` header, and kept out of every
string this package produces.
"""

from typing import Any

import httpx
import pytest

from countrystatecity import (
    API_KEY_ENV_VAR,
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    AsyncCountryStateCity,
    ConfigurationError,
    CountryStateCity,
    __version__,
)

from .helpers import TEST_API_KEY, Recorder, async_client, run, sync_client

CLIENTS = [CountryStateCity, AsyncCountryStateCity]
CLIENT_IDS = ["sync", "async"]


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep a developer's real key out of the test run."""
    monkeypatch.delenv(API_KEY_ENV_VAR, raising=False)


# -- API key resolution ----------------------------------------------------


@pytest.mark.parametrize("client_cls", CLIENTS, ids=CLIENT_IDS)
def test_missing_key_fails_before_any_network_io(client_cls: Any) -> None:
    with pytest.raises(ConfigurationError) as caught:
        client_cls()

    assert API_KEY_ENV_VAR in str(caught.value)
    assert "app.countrystatecity.in" in str(caught.value)


@pytest.mark.parametrize("client_cls", CLIENTS, ids=CLIENT_IDS)
@pytest.mark.parametrize("blank", ["", "   ", "\t\n"], ids=["empty", "spaces", "ws"])
def test_blank_key_is_rejected(client_cls: Any, blank: str) -> None:
    with pytest.raises(ConfigurationError):
        client_cls(api_key=blank)


@pytest.mark.parametrize("client_cls", CLIENTS, ids=CLIENT_IDS)
def test_blank_env_key_is_rejected(
    client_cls: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(API_KEY_ENV_VAR, "   ")
    with pytest.raises(ConfigurationError):
        client_cls()


@pytest.mark.parametrize(
    "bad_key",
    ["key with spaces", "key\nX-Injected: 1", "key\rmore", "key\x00null"],
    ids=["space", "newline", "carriage-return", "null"],
)
def test_key_with_header_breaking_characters_is_rejected(bad_key: str) -> None:
    """Blocks header injection before httpx ever sees the value."""
    with pytest.raises(ConfigurationError) as caught:
        CountryStateCity(api_key=bad_key)

    assert bad_key not in str(caught.value)


def test_non_string_key_is_rejected() -> None:
    with pytest.raises(ConfigurationError):
        CountryStateCity(api_key=12345)  # type: ignore[arg-type]


def test_key_is_read_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(API_KEY_ENV_VAR, TEST_API_KEY)
    recorder = Recorder(json_body=[])
    with CountryStateCity(transport=httpx.MockTransport(recorder)) as client:
        client.get_countries()

    assert recorder.request.headers["X-CSCAPI-KEY"] == TEST_API_KEY


def test_explicit_key_wins_over_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(API_KEY_ENV_VAR, "environment-key-value")
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        client.get_countries()

    assert recorder.request.headers["X-CSCAPI-KEY"] == TEST_API_KEY


def test_key_is_trimmed_before_use() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder, api_key=f"  {TEST_API_KEY}\n") as client:
        client.get_countries()

    assert recorder.request.headers["X-CSCAPI-KEY"] == TEST_API_KEY


# -- headers ---------------------------------------------------------------


def test_request_carries_the_expected_headers() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        client.get_countries()

    headers = recorder.request.headers
    assert headers["X-CSCAPI-KEY"] == TEST_API_KEY
    assert headers["Accept"] == "application/json"
    assert headers["User-Agent"] == f"countrystatecity-python/{__version__}"


def test_extra_headers_are_sent() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder, headers={"X-Request-Id": "abc123"}) as client:
        client.get_countries()

    assert recorder.request.headers["X-Request-Id"] == "abc123"


@pytest.mark.parametrize("header", ["X-CSCAPI-KEY", "x-cscapi-key"])
def test_api_key_cannot_be_smuggled_through_headers(header: str) -> None:
    """Otherwise the key would bypass validation and the explicit argument."""
    with pytest.raises(ConfigurationError) as caught:
        CountryStateCity(api_key=TEST_API_KEY, headers={header: "other-key"})

    assert "api_key=" in str(caught.value)


@pytest.mark.parametrize("client_cls", CLIENTS, ids=CLIENT_IDS)
@pytest.mark.parametrize(
    "headers",
    [
        [("X-Test", "value")],
        {1: "value"},
        {b"X-CSCAPI-KEY": b"other-key"},
        {"X-Test": 1},
        {"X-Bad\r\nInjected": "value"},
        {"X-Test": "value\r\nInjected: yes"},
    ],
    ids=[
        "not-a-mapping",
        "non-string-name",
        "bytes-key-override",
        "non-string-value",
        "newline-name",
        "newline-value",
    ],
)
def test_invalid_extra_headers_are_rejected_without_echoing_values(
    client_cls: Any, headers: Any
) -> None:
    sentinel = "Injected"
    with pytest.raises(ConfigurationError) as caught:
        client_cls(api_key=TEST_API_KEY, headers=headers)

    assert sentinel not in str(caught.value)


def test_api_key_is_never_in_the_request_url() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        client.get_countries(q="india")

    assert TEST_API_KEY not in str(recorder.request.url)


# -- base URL --------------------------------------------------------------


def test_default_base_url_is_production() -> None:
    assert DEFAULT_BASE_URL == "https://api.countrystatecity.in/v1"


@pytest.mark.parametrize(
    "bad_url",
    [
        "",
        "   ",
        "api.countrystatecity.in/v1",
        "ftp://example.test/v1",
        "/v1",
        "https://",
    ],
    ids=["empty", "spaces", "no-scheme", "bad-scheme", "path-only", "no-host"],
)
def test_unusable_base_url_is_rejected(bad_url: str) -> None:
    with pytest.raises(ConfigurationError):
        CountryStateCity(api_key=TEST_API_KEY, base_url=bad_url)


@pytest.mark.parametrize("client_cls", CLIENTS, ids=CLIENT_IDS)
@pytest.mark.parametrize(
    "bad_url",
    [
        "https://user:SENTINEL@example.test/v1",
        "https://example.test:abc/v1",
        "https://example.test/v1?token=SENTINEL",
        "https://example.test/v1#SENTINEL",
        "https://example.test/\nSENTINEL",
        "https://[invalid/v1",
    ],
    ids=["credentials", "bad-port", "query", "fragment", "control", "bad-ipv6"],
)
def test_sensitive_or_malformed_base_urls_are_rejected_without_echoing_values(
    client_cls: Any, bad_url: str
) -> None:
    with pytest.raises(ConfigurationError) as caught:
        client_cls(api_key=TEST_API_KEY, base_url=bad_url)

    assert "SENTINEL" not in str(caught.value)


@pytest.mark.parametrize(
    "base_url",
    ["http://localhost:8000/v1", "https://example.test/custom/root"],
)
def test_valid_custom_base_urls_are_accepted(base_url: str) -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder, base_url=base_url) as client:
        client.get_countries()

    assert str(recorder.request.url).startswith(base_url + "/")


def test_trailing_slashes_are_normalised() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder, base_url="https://example.test/v1///") as client:
        client.get_countries()

    assert str(recorder.request.url) == "https://example.test/v1/countries"


# -- timeout ---------------------------------------------------------------


def test_default_timeout_is_finite() -> None:
    assert DEFAULT_TIMEOUT == 30.0


def test_timeout_is_applied_to_requests() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder, timeout=2.5) as client:
        client.get_countries()

    assert recorder.request.extensions["timeout"] == {
        "connect": 2.5,
        "read": 2.5,
        "write": 2.5,
        "pool": 2.5,
    }


def test_httpx_timeout_object_is_accepted() -> None:
    recorder = Recorder(json_body=[])
    timeout = httpx.Timeout(connect=1.0, read=2.0, write=3.0, pool=4.0)
    with sync_client(recorder, timeout=timeout) as client:
        client.get_countries()

    assert recorder.request.extensions["timeout"]["read"] == 2.0


@pytest.mark.parametrize(
    "bad_timeout",
    [0, -1, float("inf"), float("nan"), None, "30", True],
    ids=["zero", "negative", "inf", "nan", "none", "string", "bool"],
)
def test_unusable_timeout_is_rejected(bad_timeout: Any) -> None:
    with pytest.raises(ConfigurationError):
        CountryStateCity(api_key=TEST_API_KEY, timeout=bad_timeout)


def test_timeout_object_with_a_disabled_phase_is_rejected() -> None:
    """An unbounded read can wedge a worker forever."""
    with pytest.raises(ConfigurationError) as caught:
        CountryStateCity(api_key=TEST_API_KEY, timeout=httpx.Timeout(None))

    assert "finite timeout" in str(caught.value)


# -- repr safety -----------------------------------------------------------


@pytest.mark.parametrize("client_cls", CLIENTS, ids=CLIENT_IDS)
def test_repr_redacts_the_api_key(client_cls: Any) -> None:
    client = client_cls(api_key=TEST_API_KEY)
    text = repr(client)

    assert TEST_API_KEY not in text
    assert "api_key=***" in text
    assert DEFAULT_BASE_URL in text


# -- lifecycle -------------------------------------------------------------


def test_constructing_a_client_sends_nothing() -> None:
    """No request is made until a method is called."""
    recorder = Recorder(json_body=[])
    client = sync_client(recorder)
    try:
        assert recorder.requests == []
    finally:
        client.close()


def test_async_constructing_a_client_sends_nothing() -> None:
    recorder = Recorder(json_body=[])
    client = async_client(recorder)
    try:
        assert recorder.requests == []
    finally:
        run(client.aclose())


def test_client_reuses_one_connection_pool_across_calls() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        client.get_countries()
        client.get_regions()

    assert len(recorder.requests) == 2
