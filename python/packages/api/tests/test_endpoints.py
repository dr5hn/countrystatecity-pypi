"""Every endpoint hits the URL the production API actually serves.

One table drives both clients, so the sync and async surfaces cannot drift
apart without a test failing.
"""

import inspect
from typing import Any, Dict, List, Tuple

import pytest

from countrystatecity import AsyncCountryStateCity, CountryStateCity

from .helpers import Recorder, async_client, run, sync_client

Call = Tuple[str, Tuple[Any, ...], Dict[str, Any], str, Dict[str, str]]

#: ``(method, args, kwargs, expected path, expected query)`` for every endpoint.
CALLS: List[Call] = [
    ("get_countries", (), {}, "/v1/countries", {}),
    (
        "get_countries",
        (),
        {"q": "ind", "fields": ["id", "name"], "sort": "name:asc"},
        "/v1/countries",
        {"q": "ind", "fields": "id,name", "sort": "name:asc"},
    ),
    ("get_country", ("IN",), {}, "/v1/countries/IN", {}),
    (
        "get_country",
        (233,),
        {"fields": "id,name"},
        "/v1/countries/233",
        {"fields": "id,name"},
    ),
    ("get_states", (), {}, "/v1/states", {}),
    ("get_states", (), {"q": "maha"}, "/v1/states", {"q": "maha"}),
    ("get_states_of_country", ("IN",), {}, "/v1/countries/IN/states", {}),
    ("get_state", ("IN", "MH"), {}, "/v1/countries/IN/states/MH", {}),
    ("get_state", ("IN", "AN-AMA"), {}, "/v1/countries/IN/states/AN-AMA", {}),
    (
        "get_cities_of_country",
        ("IN",),
        {"q": "pune"},
        "/v1/countries/IN/cities",
        {"q": "pune"},
    ),
    ("get_cities_of_state", ("IN", "MH"), {}, "/v1/countries/IN/states/MH/cities", {}),
    ("get_regions", (), {}, "/v1/regions", {}),
    ("get_region", (3,), {}, "/v1/regions/3", {}),
    ("get_subregions_of_region", (3,), {}, "/v1/regions/3/subregions", {}),
    ("get_subregion", (14,), {}, "/v1/subregions/14", {}),
    ("get_countries_of_subregion", (14,), {}, "/v1/subregions/14/countries", {}),
    ("get_timezone_of_country", ("IN",), {}, "/v1/timezone/IN", {}),
    ("get_timezone_of_state", ("IN", "MH"), {}, "/v1/timezone/IN/MH", {}),
    ("get_timezone_of_city", ("IN", "MH", 57606), {}, "/v1/timezone/IN/MH/57606", {}),
    # The published OpenAPI contract names this route /currencies; production
    # serves /currency, and that is what the client must call.
    ("get_currencies", (), {}, "/v1/currency", {}),
    ("get_currencies", (), {"code": "EUR"}, "/v1/currency", {"code": "EUR"}),
    ("get_currency_of_country", ("IN",), {}, "/v1/currency/IN", {}),
    ("get_dial_codes", (), {}, "/v1/phone", {}),
    ("get_dial_codes", (), {"code": "+91"}, "/v1/phone", {"code": "+91"}),
    ("get_dial_code_of_country", ("IN",), {}, "/v1/phone/IN", {}),
    (
        "parse_phone_number",
        ("+14155552671",),
        {},
        "/v1/phone/parse",
        {"number": "+14155552671"},
    ),
    ("lookup_country_iso", (), {"iso2": "US"}, "/v1/iso/country", {"iso2": "US"}),
    ("lookup_country_iso", (), {"iso3": "USA"}, "/v1/iso/country", {"iso3": "USA"}),
    (
        "lookup_country_iso",
        (),
        {"numeric": "840"},
        "/v1/iso/country",
        {"numeric": "840"},
    ),
    ("lookup_state_iso", ("US-CA",), {}, "/v1/iso/state", {"iso": "US-CA"}),
    (
        "convert_country_code",
        ("US",),
        {"from_format": "iso2", "to_format": "iso3"},
        "/v1/iso/country/convert",
        {"from": "iso2", "to": "iso3", "value": "US"},
    ),
    (
        "fuzzy_search",
        ("bangalor",),
        {},
        "/v1/search/fuzzy",
        {"q": "bangalor", "type": "city", "limit": "10", "threshold": "0.3"},
    ),
    (
        "fuzzy_search",
        ("mahrastra",),
        {"entity": "state", "country": "IN", "limit": 5, "threshold": 0.5},
        "/v1/search/fuzzy",
        {
            "q": "mahrastra",
            "type": "state",
            "country": "IN",
            "limit": "5",
            "threshold": "0.5",
        },
    ),
]

IDS = [f"{name}-{index}" for index, (name, *_rest) in enumerate(CALLS)]


@pytest.mark.parametrize("method, args, kwargs, path, params", CALLS, ids=IDS)
def test_sync_endpoint_targets_expected_url(
    method: str,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    path: str,
    params: Dict[str, str],
) -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder) as client:
        getattr(client, method)(*args, **kwargs)

    request = recorder.request
    assert request.method == "GET"
    assert request.url.host == "api.countrystatecity.in"
    assert request.url.path == path
    assert dict(request.url.params) == params


@pytest.mark.parametrize("method, args, kwargs, path, params", CALLS, ids=IDS)
def test_async_endpoint_targets_the_same_url(
    method: str,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    path: str,
    params: Dict[str, str],
) -> None:
    recorder = Recorder(json_body=[])
    client = async_client(recorder)
    try:
        run(getattr(client, method)(*args, **kwargs))
    finally:
        run(client.aclose())

    request = recorder.request
    assert request.method == "GET"
    assert request.url.path == path
    assert dict(request.url.params) == params


def test_clients_expose_the_same_public_surface() -> None:
    """Only the close/aclose lifecycle differs between the two clients."""
    sync_names = {n for n in dir(CountryStateCity) if not n.startswith("_")}
    async_names = {n for n in dir(AsyncCountryStateCity) if not n.startswith("_")}
    assert sync_names - {"close"} == async_names - {"aclose"}


@pytest.mark.parametrize("name", sorted({call[0] for call in CALLS}))
def test_endpoint_signatures_match_across_clients(name: str) -> None:
    """Same parameters, same defaults -- swapping clients cannot change a call."""
    sync_sig = inspect.signature(getattr(CountryStateCity, name))
    async_sig = inspect.signature(getattr(AsyncCountryStateCity, name))
    assert sync_sig.parameters == async_sig.parameters


def test_sync_returns_the_decoded_payload() -> None:
    # Production shape: `id` is a BIGINT column and the API serialises it as a
    # string. See tests/test_types.py.
    payload = [{"id": "101", "name": "India", "iso2": "IN"}]
    recorder = Recorder(json_body=payload)
    with sync_client(recorder) as client:
        assert client.get_countries() == payload


def test_async_returns_the_decoded_payload() -> None:
    payload = {"id": "101", "name": "India", "iso2": "IN"}
    recorder = Recorder(json_body=payload)
    client = async_client(recorder)
    try:
        assert run(client.get_country("IN")) == payload
    finally:
        run(client.aclose())


def test_async_context_manager_closes_the_pool() -> None:
    recorder = Recorder(json_body=[])

    async def scenario() -> Any:
        async with async_client(recorder) as client:
            return await client.get_regions()

    assert run(scenario()) == []
    assert recorder.request.url.path == "/v1/regions"


def test_request_escape_hatch_reaches_unwrapped_paths() -> None:
    recorder = Recorder(json_body={"ok": True})
    with sync_client(recorder) as client:
        response = client.request("/some/future/route", params={"limit": 5})

    assert response.data == {"ok": True}
    assert recorder.request.url.path == "/v1/some/future/route"
    assert dict(recorder.request.url.params) == {"limit": "5"}


def test_async_request_escape_hatch_reaches_unwrapped_paths() -> None:
    recorder = Recorder(json_body={"ok": True})
    client = async_client(recorder)
    try:
        response = run(client.request("/some/future/route"))
    finally:
        run(client.aclose())

    assert response.data == {"ok": True}
    assert recorder.request.url.path == "/v1/some/future/route"


def test_custom_base_url_is_honoured() -> None:
    recorder = Recorder(json_body=[])
    with sync_client(recorder, base_url="https://staging.example.test/v1/") as client:
        client.get_countries()

    assert str(recorder.request.url) == "https://staging.example.test/v1/countries"
