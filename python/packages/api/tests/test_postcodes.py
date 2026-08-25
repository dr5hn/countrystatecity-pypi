"""Postcode-specific response behaviour: duplicate matches, nullable fields,
pagination, malformed cursors, plan restrictions, and response metadata.

URL shape and client-side validation are covered in ``test_endpoints.py`` and
``test_validation.py``; this file is about what the client does with the
response body once the request succeeds or fails.
"""

from typing import Any, Dict

import pytest

from countrystatecity import BadRequestError, NotFoundError, PermissionDeniedError

from .helpers import Recorder, async_client, run, sync_client

_LOOKUP_ONE = {
    "data": [
        {
            "id": "1",
            "code": "SW1A 1AA",
            "country_code": "GB",
            "state_code": "ENG",
            "locality_name": "London",
            "type": "full",
        }
    ],
    "meta": {"country_code": "GB", "query": "SW1A 1AA", "match_count": 1},
}

_LOOKUP_DUPLICATE = {
    "data": [
        {
            "id": "101",
            "code": "12345",
            "country_code": "US",
            "state_code": "NY",
            "locality_name": "New York",
            "type": "full",
        },
        {
            "id": "102",
            "code": "12345",
            "country_code": "US",
            "state_code": "NJ",
            "locality_name": "Newark",
            "type": "full",
        },
    ],
    "meta": {"country_code": "US", "query": "12345", "match_count": 2},
}


def test_sync_lookup_returns_every_match_not_just_the_first() -> None:
    """A postcode can map to more than one locality -- PRD §1, §14."""
    recorder = Recorder(json_body=_LOOKUP_DUPLICATE)
    with sync_client(recorder) as client:
        matches = client.get_postcodes_by_code("US", "12345")

    assert len(matches) == 2
    assert [m["id"] for m in matches] == ["101", "102"]
    assert {m["locality_name"] for m in matches} == {"New York", "Newark"}


def test_async_lookup_returns_every_match() -> None:
    recorder = Recorder(json_body=_LOOKUP_DUPLICATE)
    client = async_client(recorder)
    try:
        matches = run(client.get_postcodes_by_code("US", "12345"))
    finally:
        run(client.aclose())

    assert len(matches) == 2


def test_lookup_result_is_a_bare_list_not_an_envelope() -> None:
    """The `meta` envelope key (match_count/query/country_code) is discarded:
    match_count is always len(result), and query/country_code just echo the
    caller's own already-known arguments.
    """
    recorder = Recorder(json_body=_LOOKUP_ONE)
    with sync_client(recorder) as client:
        result = client.get_postcodes_by_code("GB", "SW1A 1AA")

    assert isinstance(result, list)
    assert result[0]["code"] == "SW1A 1AA"


def test_lookup_tolerates_a_missing_data_key() -> None:
    recorder = Recorder(json_body={"meta": {"match_count": 0}})
    with sync_client(recorder) as client:
        assert client.get_postcodes_by_code("GB", "SW1A 1AA") == []


def test_basic_tier_response_has_nullable_fields_absent() -> None:
    """Coordinates/full-tier keys are simply absent from a Basic-plan response
    -- TypedDict's total=False means the type checker already treats every
    key as possibly missing; this asserts the runtime shape matches.
    """
    recorder = Recorder(
        json_body={
            "data": [{"id": "1", "code": "12345", "country_code": "US"}],
            "meta": {"country_code": "US", "query": "12345", "match_count": 1},
        }
    )
    with sync_client(recorder) as client:
        result = client.get_postcodes_by_code("US", "12345")

    postcode = result[0]
    assert "state_code" not in postcode
    assert "latitude" not in postcode
    assert "source" not in postcode


def test_full_tier_response_carries_coordinates_and_source() -> None:
    recorder = Recorder(
        json_body={
            "data": [
                {
                    "id": "1",
                    "code": "SW1A 1AA",
                    "country_code": "GB",
                    "state_code": "ENG",
                    "locality_name": "London",
                    "type": "full",
                    "country_id": "232",
                    "state_id": "4",
                    "city_id": "100",
                    "latitude": 51.50101,
                    "longitude": -0.14159,
                    "source": "royal-mail",
                    "wikiDataId": "Q84",
                }
            ],
            "meta": {"country_code": "GB", "query": "SW1A 1AA", "match_count": 1},
        }
    )
    with sync_client(recorder) as client:
        postcode = client.get_postcodes_by_code("GB", "SW1A 1AA")[0]

    # Unlike City/State/Country (NUMERIC columns, stringified), postcodes'
    # latitude/longitude are DOUBLE PRECISION and arrive as native numbers.
    assert postcode["latitude"] == pytest.approx(51.50101)
    assert postcode["longitude"] == pytest.approx(-0.14159)
    assert postcode["source"] == "royal-mail"
    assert postcode["wikiDataId"] == "Q84"


@pytest.mark.parametrize(
    "reason",
    ["country_not_found", "postcode_coverage_unavailable", "postcode_not_found"],
)
def test_404_reasons_are_distinguishable(reason: str) -> None:
    body = {"status": "error", "message": "not found", "details": {"reason": reason}}
    recorder = Recorder(status_code=404, json_body=body)
    with sync_client(recorder) as client:
        with pytest.raises(NotFoundError) as caught:
            client.get_postcodes_by_code("ZZ", "12345")

    assert caught.value.details.get("reason") == reason


def test_search_pagination_round_trips() -> None:
    body = {
        "data": [{"id": "1", "code": "SW1A 1AA", "country_code": "GB"}],
        "pagination": {"limit": 50, "next_cursor": "cGMxLi4u", "has_more": True},
    }
    recorder = Recorder(json_body=body)
    with sync_client(recorder) as client:
        result = client.get_postcodes_of_country("GB", q="SW1A")

    assert result["pagination"]["limit"] == 50
    assert result["pagination"]["next_cursor"] == "cGMxLi4u"
    assert result["pagination"]["has_more"] is True
    assert len(result["data"]) == 1


def test_async_search_pagination_round_trips() -> None:
    body = {
        "data": [],
        "pagination": {"limit": 50, "next_cursor": None, "has_more": False},
    }
    recorder = Recorder(json_body=body)
    client = async_client(recorder)
    try:
        result = run(client.get_postcodes_of_country("GB"))
    finally:
        run(client.aclose())

    assert result["pagination"]["has_more"] is False
    assert result["pagination"]["next_cursor"] is None


def test_search_response_has_no_total_count_key() -> None:
    """PRD §7.4: "No total count is returned." The client passes the body
    through unchanged, so a stray `total` in a mock would still surface --
    this documents that the type intentionally has no such field.
    """
    from countrystatecity.types import PostcodePagination

    assert "total" not in PostcodePagination.__annotations__


def test_empty_search_has_empty_data_and_has_more_false() -> None:
    body = {
        "data": [],
        "pagination": {"limit": 50, "next_cursor": None, "has_more": False},
    }
    recorder = Recorder(json_body=body)
    with sync_client(recorder) as client:
        result = client.get_postcodes_of_country("GB", q="ZZZNOMATCH")

    assert result["data"] == []
    assert result["pagination"]["has_more"] is False


def test_malformed_cursor_rejected_by_server_raises_bad_request() -> None:
    """A cursor that is well-formed client-side (non-empty, <=512 chars) but
    semantically bogus -- wrong version, tampered, stale filter fingerprint --
    is rejected server-side with a 400.
    """
    body = {
        "status": "error",
        "message": "cursor is invalid or has expired",
        "details": {"field": "cursor", "reason": "invalid_cursor"},
    }
    recorder = Recorder(status_code=400, json_body=body)
    with sync_client(recorder) as client:
        with pytest.raises(BadRequestError) as caught:
            client.get_postcodes_of_country("GB", cursor="dGFtcGVyZWQ")

    assert caught.value.details.get("reason") == "invalid_cursor"


def test_search_without_plan_feature_raises_permission_denied() -> None:
    body = {
        "status": "error",
        "message": "This feature is not available on your current plan.",
        "details": {
            "feature": "searchEndpoint",
            "upgradeUrl": (
                "https://app.countrystatecity.in/pricing?utm_source=api&"
                "utm_medium=upgrade_error&utm_campaign=postcodes"
            ),
        },
    }
    recorder = Recorder(status_code=403, json_body=body)
    with sync_client(recorder) as client:
        with pytest.raises(PermissionDeniedError) as caught:
            client.get_postcodes_of_country("GB", q="SW1A")

    assert caught.value.feature == "searchEndpoint"
    assert caught.value.upgrade_url is not None
    assert "utm_campaign=postcodes" in caught.value.upgrade_url


def test_async_search_without_plan_feature_raises_permission_denied() -> None:
    body = {
        "status": "error",
        "message": "upgrade required",
        "details": {"feature": "searchEndpoint"},
    }
    recorder = Recorder(status_code=403, json_body=body)
    client = async_client(recorder)
    try:
        with pytest.raises(PermissionDeniedError) as caught:
            run(client.get_postcodes_of_country("US", q="abc"))
    finally:
        run(client.aclose())

    assert caught.value.feature == "searchEndpoint"


def test_response_metadata_is_available_via_the_request_escape_hatch() -> None:
    """The typed methods discard HTTP-level metadata to stay consistent with
    every other typed method in this client; ``request()`` still exposes it
    for postcode routes exactly as it does for any other route.
    """
    recorder = Recorder(
        json_body=_LOOKUP_ONE,
        headers={
            "X-CSC-Plan": "supporter",
            "X-CSC-Daily-Used": "42",
            "X-CSC-Daily-Limit": "1000",
            "X-Cache": "HIT",
            "ETag": '"abc123"',
        },
    )
    with sync_client(recorder) as client:
        response = client.request("/countries/GB/postcodes/SW1A%201AA")

    assert response.data == _LOOKUP_ONE
    assert response.meta.plan == "supporter"
    assert response.meta.daily.used == 42
    assert response.meta.daily.limit == 1000
    assert response.meta.daily.remaining == 958
    assert response.meta.cache == "HIT"
    assert response.meta.etag == '"abc123"'


def test_postcode_with_reserved_characters_survives_the_round_trip() -> None:
    """URL encoding: a code containing a space and other reserved characters
    reaches the server undamaged and unsplit.
    """
    recorder = Recorder(json_body={"data": [], "meta": {}})
    with sync_client(recorder) as client:
        client.get_postcodes_by_code("GB", "SW1A 1AA")

    assert recorder.request.url.path == "/v1/countries/GB/postcodes/SW1A 1AA"
    assert b"SW1A%201AA" in recorder.request.url.raw_path


def test_postcode_with_a_slash_stays_inside_one_path_segment() -> None:
    """A `/` in the code is within the 1-20 character bound, so this is not a
    rejected case -- `quote_segment` percent-encodes it (like every other
    path segment in this package), so it can never inject an extra path
    segment or a traversal sequence.
    """
    recorder = Recorder(json_body={"data": [], "meta": {}})
    with sync_client(recorder) as client:
        client.get_postcodes_by_code("GB", "AB/../secret")

    assert recorder.request.url.path == "/v1/countries/GB/postcodes/AB/../secret"
    assert recorder.request.url.raw_path == (
        b"/v1/countries/GB/postcodes/AB%2F..%2Fsecret"
    )


CROSS_CLIENT_CALLS: Dict[str, Any] = {
    "lookup": ("get_postcodes_by_code", ("GB", "SW1A 1AA"), {}, _LOOKUP_ONE),
    "search": (
        "get_postcodes_of_country",
        ("GB",),
        {"q": "SW1A"},
        {
            "data": [],
            "pagination": {"limit": 50, "next_cursor": None, "has_more": False},
        },
    ),
}


@pytest.mark.parametrize("case", sorted(CROSS_CLIENT_CALLS))
def test_sync_and_async_clients_decode_the_same_payload(case: str) -> None:
    method, args, kwargs, body = CROSS_CLIENT_CALLS[case]

    sync_recorder = Recorder(json_body=body)
    with sync_client(sync_recorder) as client:
        sync_result = getattr(client, method)(*args, **kwargs)

    async_recorder = Recorder(json_body=body)
    async_cli = async_client(async_recorder)
    try:
        async_result = run(getattr(async_cli, method)(*args, **kwargs))
    finally:
        run(async_cli.aclose())

    assert sync_result == async_result
