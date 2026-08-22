"""Bad input is rejected locally, and good input is encoded safely.

Two properties matter here. First, a rejected call must never reach the network
-- the caller's quota is finite, and a guaranteed ``400`` should not cost a
request. Second, nothing a caller passes may escape the URL segment it was
given.
"""

from typing import Any, Dict, Tuple

import pytest

from countrystatecity import ValidationError
from countrystatecity._validation import quote_segment

from .helpers import Recorder, async_client, run, sync_client

#: ``(method, args, kwargs)`` calls that must fail before any HTTP request.
REJECTED: Dict[str, Tuple[str, Tuple[Any, ...], Dict[str, Any]]] = {
    "country-empty": ("get_country", ("",), {}),
    "country-too-short": ("get_country", ("I",), {}),
    "country-too-long": ("get_country", ("INDIA",), {}),
    "country-traversal": ("get_country", ("../../admin",), {}),
    "country-slash": ("get_country", ("IN/states",), {}),
    "country-zero-id": ("get_country", (0,), {}),
    "country-huge-id": ("get_country", (1_000_000,), {}),
    "country-bool": ("get_country", (True,), {}),
    "country-float": ("get_country", (1.5,), {}),
    "country-none": ("get_country", (None,), {}),
    "state-too-long": ("get_state", ("IN", "ABCDEFGHIJK"), {}),
    "state-slash": ("get_state", ("IN", "MH/x"), {}),
    "state-space": ("get_state", ("IN", "M H"), {}),
    "city-id-zero": ("get_timezone_of_city", ("IN", "MH", 0), {}),
    "city-id-negative": ("get_timezone_of_city", ("IN", "MH", -3), {}),
    "city-id-text": ("get_timezone_of_city", ("IN", "MH", "abc"), {}),
    "region-id-zero": ("get_region", (0,), {}),
    "region-id-huge": ("get_region", (1_000_000,), {}),
    "subregion-id-text": ("get_subregion", ("fourteen",), {}),
    "q-too-short": ("get_countries", (), {"q": "a"}),
    "q-empty": ("get_countries", (), {"q": ""}),
    "q-too-long": ("get_countries", (), {"q": "x" * 101}),
    "q-not-a-string": ("get_countries", (), {"q": 7}),
    "fields-empty-string": ("get_countries", (), {"fields": ""}),
    "fields-empty-list": ("get_countries", (), {"fields": []}),
    "fields-only-commas": ("get_countries", (), {"fields": ",,"}),
    "fields-injection": ("get_countries", (), {"fields": "id;DROP TABLE"}),
    "fields-non-string-entry": ("get_countries", (), {"fields": [1]}),
    "sort-bad-direction": ("get_countries", (), {"sort": "name:sideways"}),
    "sort-extra-segment": ("get_countries", (), {"sort": "name:asc:extra"}),
    "sort-empty": ("get_countries", (), {"sort": ""}),
    "currency-code-short": ("get_currencies", (), {"code": "US"}),
    "currency-code-digits": ("get_currencies", (), {"code": "US1"}),
    "dial-code-letters": ("get_dial_codes", (), {"code": "abc"}),
    "dial-code-too-long": ("get_dial_codes", (), {"code": "12345"}),
    "phone-missing-plus": ("parse_phone_number", ("14155552671",), {}),
    "phone-too-short": ("parse_phone_number", ("+123",), {}),
    "phone-letters": ("parse_phone_number", ("+1415555267a",), {}),
    "iso-country-none-given": ("lookup_country_iso", (), {}),
    "iso-country-two-given": ("lookup_country_iso", (), {"iso2": "US", "iso3": "USA"}),
    "iso-country-bad-iso2": ("lookup_country_iso", (), {"iso2": "USA"}),
    "iso-country-zero-numeric": ("lookup_country_iso", (), {"numeric": "000"}),
    "iso-state-bad": ("lookup_state_iso", ("USCA",), {}),
    "convert-same-format": (
        "convert_country_code",
        ("US",),
        {"from_format": "iso2", "to_format": "iso2"},
    ),
    "convert-unknown-format": (
        "convert_country_code",
        ("US",),
        {"from_format": "iso2", "to_format": "alpha4"},
    ),
    "convert-value-mismatch": (
        "convert_country_code",
        ("USA",),
        {"from_format": "iso2", "to_format": "iso3"},
    ),
    "fuzzy-unknown-entity": ("fuzzy_search", ("pune",), {"entity": "planet"}),
    "fuzzy-country-with-country-entity": (
        "fuzzy_search",
        ("india",),
        {"entity": "country", "country": "IN"},
    ),
    "fuzzy-limit-zero": ("fuzzy_search", ("pune",), {"limit": 0}),
    "fuzzy-limit-too-big": ("fuzzy_search", ("pune",), {"limit": 51}),
    "fuzzy-limit-bool": ("fuzzy_search", ("pune",), {"limit": True}),
    "fuzzy-threshold-low": ("fuzzy_search", ("pune",), {"threshold": 0.05}),
    "fuzzy-threshold-high": ("fuzzy_search", ("pune",), {"threshold": 1.5}),
    "phone-not-a-string": ("parse_phone_number", (14155552671,), {}),
    "fields-bytes": ("get_countries", (), {"fields": b"id"}),
    "fields-int": ("get_countries", (), {"fields": 123}),
    "fuzzy-threshold-string": ("fuzzy_search", ("pune",), {"threshold": "0.5"}),
    "request-relative-path": ("request", ("countries",), {}),
    "request-path-not-a-string": ("request", (7,), {}),
}


@pytest.mark.parametrize("case", sorted(REJECTED), ids=sorted(REJECTED))
def test_sync_rejects_bad_input_without_sending_a_request(case: str) -> None:
    method, args, kwargs = REJECTED[case]
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        with pytest.raises(ValidationError):
            getattr(client, method)(*args, **kwargs)

    assert recorder.requests == []


@pytest.mark.parametrize("case", sorted(REJECTED), ids=sorted(REJECTED))
def test_async_rejects_bad_input_without_sending_a_request(case: str) -> None:
    method, args, kwargs = REJECTED[case]
    recorder = Recorder(json_body=[])
    client = async_client(recorder)
    try:
        with pytest.raises(ValidationError):
            run(getattr(client, method)(*args, **kwargs))
    finally:
        run(client.aclose())

    assert recorder.requests == []


def test_validation_error_is_also_a_value_error() -> None:
    """Callers already catching ValueError keep working."""
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        with pytest.raises(ValueError):
            client.get_country("not-a-country")


def test_phone_validation_error_does_not_echo_the_number() -> None:
    """Phone numbers are personal data; error text ends up in logs."""
    recorder = Recorder(json_body={})
    with sync_client(recorder) as client:
        with pytest.raises(ValidationError) as caught:
            client.parse_phone_number("+9988776655x")

    assert "9988776655" not in str(caught.value)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("IN", "IN"),
        ("AN-AMA", "AN-AMA"),
        ("a/b", "a%2Fb"),
        ("../admin", "..%2Fadmin"),
        ("a b", "a%20b"),
        ("q?x=1&y=2", "q%3Fx%3D1%26y%3D2"),
        ("café", "caf%C3%A9"),
        ("100%", "100%25"),
    ],
)
def test_path_segments_are_percent_encoded(raw: str, expected: str) -> None:
    assert quote_segment(raw) == expected


def test_search_term_with_reserved_characters_survives_the_round_trip() -> None:
    term = "côte d'ivoire &?=#"
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        client.get_countries(q=term)

    assert dict(recorder.request.url.params) == {"q": term}


def test_plus_in_a_phone_number_is_percent_encoded_on_the_wire() -> None:
    """A bare ``+`` would decode server-side as a space; it must be ``%2B``."""
    recorder = Recorder(json_body={})
    with sync_client(recorder) as client:
        client.parse_phone_number("+14155552671")

    assert "number=%2B14155552671" in recorder.request.url.query.decode()


def test_field_and_sort_lists_are_joined() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        client.get_countries(
            fields=["id", "name", "iso2"], sort=["name:asc", "id:desc"]
        )

    params = dict(recorder.request.url.params)
    assert params["fields"] == "id,name,iso2"
    assert params["sort"] == "name:asc,id:desc"


def test_field_and_sort_strings_are_normalised() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        client.get_countries(fields=" id , name ", sort=" name : asc ")

    params = dict(recorder.request.url.params)
    assert params["fields"] == "id,name"
    assert params["sort"] == "name:asc"


@pytest.mark.parametrize("code", ["+91", "91", "1-246", "+1-246"])
def test_accepted_dial_code_forms(code: str) -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        client.get_dial_codes(code=code)

    assert dict(recorder.request.url.params) == {"code": code}


@pytest.mark.parametrize("value", ["IN", "IND", "in", 233, "233", "0233"])
def test_accepted_country_identifier_forms(value: Any) -> None:
    recorder = Recorder(json_body={})
    with sync_client(recorder) as client:
        client.get_country(value)

    assert recorder.request.url.path == f"/v1/countries/{value}"
