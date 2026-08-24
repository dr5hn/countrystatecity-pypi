"""Plan, quota, and cache headers are surfaced without a second API call.

The API reports the caller's tier and quota consumption on every ``/v1``
response. Applications should be able to alarm on quota burn from the response
they already have.
"""

import re
from pathlib import Path
from typing import Dict

import pytest

from countrystatecity import Quota, RateLimitError, ResponseMeta, __version__

from .helpers import Recorder, async_client, run, sync_client

FULL_HEADERS: Dict[str, str] = {
    "X-CSC-Plan": "supporter",
    "X-CSC-Daily-Used": "42",
    "X-CSC-Daily-Limit": "1000",
    "X-CSC-Monthly-Used": "850",
    "X-CSC-Monthly-Limit": "30000",
    "X-Cache": "HIT",
    "ETag": '"a3f2b8c1"',
    "Cache-Control": "public, max-age=3600",
}


def test_metadata_is_parsed_from_response_headers() -> None:
    recorder = Recorder(json_body=[], headers=FULL_HEADERS)
    with sync_client(recorder) as client:
        response = client.request("/countries")

    meta = response.meta
    assert response.status_code == 200
    assert meta.plan == "supporter"
    assert meta.daily.used == 42
    assert meta.daily.limit == 1000
    assert meta.daily.remaining == 958
    assert meta.monthly.used == 850
    assert meta.monthly.limit == 30000
    assert meta.monthly.remaining == 29150
    assert meta.cache == "HIT"
    assert meta.etag == '"a3f2b8c1"'
    assert meta.cache_control == "public, max-age=3600"


def test_metadata_is_available_from_the_async_client() -> None:
    recorder = Recorder(json_body=[], headers=FULL_HEADERS)
    client = async_client(recorder)
    try:
        response = run(client.request("/countries"))
    finally:
        run(client.aclose())

    assert response.meta.plan == "supporter"
    assert response.meta.daily.remaining == 958


def test_header_lookup_is_case_insensitive() -> None:
    recorder = Recorder(json_body=[], headers={"x-csc-plan": "business"})
    with sync_client(recorder) as client:
        response = client.request("/countries")

    assert response.meta.plan == "business"
    assert response.meta.headers["X-CSC-Plan"] == "business"


def test_unlimited_plan_is_reported_as_unlimited() -> None:
    recorder = Recorder(
        json_body=[],
        headers={
            "X-CSC-Plan": "custom",
            "X-CSC-Daily-Used": "5",
            "X-CSC-Daily-Limit": "unlimited",
            "X-CSC-Monthly-Limit": "unlimited",
        },
    )
    with sync_client(recorder) as client:
        response = client.request("/countries")

    assert response.meta.daily.unlimited is True
    assert response.meta.daily.limit is None
    assert response.meta.daily.remaining is None
    assert response.meta.monthly.unlimited is True


def test_missing_headers_degrade_to_none() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        response = client.request("/countries")

    meta = response.meta
    assert meta.plan is None
    assert meta.cache is None
    assert meta.etag is None
    assert meta.daily == Quota()
    assert meta.daily.remaining is None


def test_unparsable_quota_headers_do_not_break_the_response() -> None:
    """Metadata is diagnostic; a bad header must not fail a good response."""
    recorder = Recorder(
        json_body=[{"id": "1"}],
        headers={"X-CSC-Daily-Used": "many", "X-CSC-Daily-Limit": "lots"},
    )
    with sync_client(recorder) as client:
        response = client.request("/countries")

    assert response.data == [{"id": "1"}]
    assert response.meta.daily.used is None
    assert response.meta.daily.limit is None


def test_remaining_never_goes_negative() -> None:
    quota = Quota(used=120, limit=100)
    assert quota.remaining == 0


def test_errors_carry_whatever_metadata_the_response_had() -> None:
    recorder = Recorder(
        status_code=429,
        json_body={"error": "limit reached", "limit": 100, "period": "daily"},
        headers={"X-CSC-Plan": "community"},
    )
    with sync_client(recorder) as client:
        with pytest.raises(RateLimitError) as caught:
            client.get_countries()

    assert caught.value.meta.plan == "community"


def test_meta_from_headers_accepts_a_plain_dict() -> None:
    meta = ResponseMeta.from_headers({"X-CSC-Plan": "starter"})
    assert meta.plan == "starter"
    assert meta.daily.used is None


def test_version_matches_pyproject() -> None:
    """The declared version and the runtime version must not drift."""
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    match = re.search(r'^version = "(.+?)"$', pyproject.read_text(), re.MULTILINE)
    assert match is not None, "pyproject.toml has no [project] version"
    assert match.group(1) == __version__


def test_distribution_name_identifies_the_api_client() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    match = re.search(r'^name = "(.+?)"$', pyproject.read_text(), re.MULTILINE)
    assert match is not None
    assert match.group(1) == "countrystatecity-api"


def test_py_typed_marker_ships_with_the_package() -> None:
    marker = Path(__file__).resolve().parents[1] / "countrystatecity" / "py.typed"
    assert marker.is_file()
