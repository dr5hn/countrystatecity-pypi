# countrystatecity-api

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-api)](https://pypi.org/project/countrystatecity-api/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-api)](https://pypi.org/project/countrystatecity-api/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)

**The official Python client for the [Country State City API](https://countrystatecity.in/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=api_client).**
Continuously updated geographic data, with sync and async access, typed
payloads, and structured errors.

## 60 seconds to your first request

```bash
pip install countrystatecity-api
```

[Create a free API key](https://app.countrystatecity.in/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=api_client)
(no card required), then:

```bash
export CSC_API_KEY="your-api-key"
```

```python
from countrystatecity import CountryStateCity

csc = CountryStateCity()          # reads CSC_API_KEY

india = csc.get_country("IN")
print(india["emoji"], india["name"], "-", india["capital"])

for state in csc.get_states_of_country("IN"):
    print(state["iso2"], state["name"])
```

That is the whole setup. Reuse one client for the life of your process; it holds
a connection pool.

## Async

The same surface, without blocking the event loop:

```python
import asyncio
from countrystatecity import AsyncCountryStateCity

async def main() -> None:
    async with AsyncCountryStateCity() as csc:
        country, states = await asyncio.gather(
            csc.get_country("IN"),
            csc.get_states_of_country("IN"),
        )
        print(country["name"], len(states), "states")

asyncio.run(main())
```

Both clients take the same arguments, expose the same method names, and return
the same payloads. A test asserts their signatures stay identical.

## Handling failures

Every failure is a subclass of `CountryStateCityError`, so one `except` clause
contains the client. Branch further when you want to act on the reason:

```python
from countrystatecity import (
    CountryStateCity,
    APITimeoutError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)

csc = CountryStateCity(timeout=10.0)

try:
    cities = csc.get_cities_of_state("IN", "MH", q="pune")
except NotFoundError:
    cities = []
except PermissionDeniedError as exc:
    # Endpoint or query feature not included in this plan.
    print(f"{exc.feature} requires an upgrade: {exc.upgrade_url}")
except RateLimitError as exc:
    print(f"{exc.period} limit of {exc.limit} reached on the {exc.tier} plan")
    print(f"Resets at {exc.reset_at}")     # ISO 8601 UTC, or None
    print(f"Raise it at {exc.upgrade_url}")
except APITimeoutError:
    ...  # retry on your own schedule; see "No implicit retries" below
```

| Exception | Raised for |
|---|---|
| `ConfigurationError` | Missing/blank key, bad base URL, non-finite timeout — at construction |
| `ValidationError` | An argument the API would reject; raised before the request is sent |
| `APIConnectionError` | DNS, TLS, refused connection, truncated response |
| `APITimeoutError` | Request exceeded the timeout (subclass of `APIConnectionError`) |
| `BadRequestError` | `400` |
| `AuthenticationError` | `401` — key missing, malformed, or unknown |
| `PermissionDeniedError` | `403` — plan restriction, or a domain/IP allow-list block |
| `NotFoundError` | `404` |
| `RateLimitError` | `429` — daily or monthly quota exhausted |
| `ServerError` | `5xx` |
| `APIResponseError` | A `2xx` body that was not valid JSON |

`APIStatusError` (the parent of the status classes) always carries
`.status_code`, `.details`, `.method`, and `.url`. `.details` normalises both
error envelopes the API emits, so `feature`, `upgradeUrl`, `tier`, `limit`, and
`period` are readable regardless of which layer rejected the request.

## Plan and quota headers

Every `/v1` response reports your tier and usage. Reach them through the
low-level `request()` method, which returns the payload *and* its metadata:

```python
response = csc.request("/countries")

print(response.meta.plan)                 # 'supporter'
print(response.meta.daily.used,
      response.meta.daily.limit,
      response.meta.daily.remaining)      # 42 1000 958
print(response.meta.cache)                # 'HIT' or 'MISS'
print(response.meta.etag)

countries = response.data
```

`request()` doubles as an escape hatch for any endpoint this version does not
wrap yet.

For unlimited plans, `daily.unlimited` is `True` and `limit`/`remaining` are
`None`. On a `401` or `429` the API rejects the request before setting those
headers, so metadata is empty there — a `RateLimitError`'s `.limit`, `.period`,
`.tier`, and `.reset_at` come from the response body instead.

## Search, field selection, and sorting

Paid plans add server-side query features. Ask for less data and the responses
get much smaller:

```python
# Inline search
csc.get_cities_of_country("IN", q="pune")

# Only the fields you use
csc.get_countries(fields=["id", "name", "iso2", "emoji"])

# Server-side ordering
csc.get_countries(sort="population:desc")

# Typo-tolerant search
csc.fuzzy_search("bangalor", entity="city", country="IN", limit=5)
```

`fields` and `sort` accept a comma-separated string or a list of strings.
Requesting a feature your plan does not include raises `PermissionDeniedError`
with the exact `feature` name and an upgrade URL.

## API reference

All methods issue one HTTP `GET`. `country` accepts an ISO 3166-1 alpha-2 code,
an alpha-3 code, or a numeric country id.

### Countries, states, cities

| Method | Endpoint |
|---|---|
| `get_countries(q=, fields=, sort=)` | `GET /countries` |
| `get_country(country, fields=)` | `GET /countries/{ciso}` |
| `get_states(q=, fields=, sort=)` | `GET /states` |
| `get_states_of_country(country, q=, fields=, sort=)` | `GET /countries/{ciso}/states` |
| `get_state(country, state, fields=)` | `GET /countries/{ciso}/states/{siso}` |
| `get_cities_of_country(country, q=, fields=, sort=)` | `GET /countries/{ciso}/cities` |
| `get_cities_of_state(country, state, q=, fields=, sort=)` | `GET /countries/{ciso}/states/{siso}/cities` |

### Regions

| Method | Endpoint |
|---|---|
| `get_regions(q=, fields=, sort=)` | `GET /regions` |
| `get_region(region_id, fields=)` | `GET /regions/{id}` |
| `get_subregions_of_region(region_id, q=, fields=, sort=)` | `GET /regions/{id}/subregions` |
| `get_subregion(subregion_id, fields=)` | `GET /subregions/{id}` |
| `get_countries_of_subregion(subregion_id, q=, fields=, sort=)` | `GET /subregions/{id}/countries` |

### Timezones, currencies, phone

| Method | Endpoint |
|---|---|
| `get_timezone_of_country(country)` | `GET /timezone/{ciso}` |
| `get_timezone_of_state(country, state)` | `GET /timezone/{ciso}/{siso}` |
| `get_timezone_of_city(country, state, city_id)` | `GET /timezone/{ciso}/{siso}/{city_id}` |
| `get_currencies(code=)` | `GET /currency` |
| `get_currency_of_country(country)` | `GET /currency/{ciso}` |
| `get_dial_codes(code=)` | `GET /phone` |
| `get_dial_code_of_country(country)` | `GET /phone/{ciso}` |
| `parse_phone_number(number)` | `GET /phone/parse` |

### ISO lookup and search

| Method | Endpoint |
|---|---|
| `lookup_country_iso(iso2=, iso3=, numeric=)` | `GET /iso/country` |
| `lookup_state_iso(iso)` | `GET /iso/state` |
| `convert_country_code(value, from_format=, to_format=)` | `GET /iso/country/convert` |
| `fuzzy_search(query, entity=, country=, limit=, threshold=)` | `GET /search/fuzzy` |
| `request(path, params=)` | Any `GET` under the base URL |

Full endpoint reference: [docs.countrystatecity.in](https://docs.countrystatecity.in/api/introduction) ·
Try it live: [playground.countrystatecity.in](https://playground.countrystatecity.in/)

## Types

Payloads are plain dicts. `countrystatecity.types` describes their shape with
`TypedDict`s — `Country`, `State`, `City`, `Region`, `Subregion`,
`TimezoneInfo`, `CurrencyInfo`, `DialCode`, `PhoneParsed`, `IsoCountry`,
`IsoState`, `IsoConvert`, and `FuzzyResult`.

Every field is declared optional, because which fields arrive depends on your
plan's data-access level and on the `fields` parameter. `total=False` describes
presence, not value: when a key is there, its declared type is what you get.
The type checker therefore treats *every* key as possibly missing, `id` and
`name` included. Read the ones outside your plan's guaranteed set with `.get()`,
and assert the ones your plan does guarantee at your own boundary:

```python
country = csc.get_country("IN")
name = country["name"]                     # present on every plan; a KeyError
                                           # here means the API changed
population = country.get("population")     # coordinates tier and above
```

**Ids are strings.** Every id, foreign id, `population`, and `gdp` is a 64-bit
`BIGINT` in the API's database, and the API serialises those as JSON strings —
a bigint does not survive a round trip through a JavaScript number. So
`country["id"] == "101"`, not `101`. Convert with `int()` where you need
arithmetic. `level`, `area_sq_km`, and `match_score` are ordinary numbers.

The package ships `py.typed`, so mypy and Pyright see these types with no stub
package.

## Behaviour worth knowing

**Your key stays a secret.** It is sent only in the `X-CSCAPI-KEY` header,
never in a URL. It does not appear in `repr(client)`, in exception messages, or
in `APIStatusError.url`. Keep it in a server-side environment variable — never
in browser code, a mobile app, or source control.

**Request failures are safe to log.** `APIStatusError.url` and transport error
messages carry the scheme, host, and path only — the query string and fragment
are dropped. Raw-path and query-parameter validation errors do not repeat the
rejected input. Query values are your data: `parse_phone_number()` sends a
phone number and `q=` sends a search term, and a failure should not put either
into your logs. The request itself is unaffected; only what the exception
records is trimmed.

**The `request()` escape hatch stays under the base URL.** `//host`, an
embedded `?` or `#`, and `.`/`..` segments (including percent-encoded ones) are
rejected with `ValidationError`, so a path built from untrusted input cannot
walk out of `/v1` and reach another route.

**Nothing happens at import.** Importing the package and constructing a client
open no connections. The first request is the one you make.

**No implicit retries.** A silent retry would spend a second request from your
quota without you asking. Add your own policy where you want one, and back off
on `RateLimitError` — the free Community plan is a small daily allowance.

**Finite timeouts.** The default is 30 seconds per request. `timeout=None` is
rejected: an unbounded read can wedge a worker forever.

**Arguments are validated locally.** Country codes, state codes, ids, search
terms, field lists, and phone numbers are checked against the same rules the API
enforces, so a malformed call raises `ValidationError` instead of spending a
request on a guaranteed `400`. Field *names* are checked for shape only — the
API stays the authority on which columns exist for your plan.

**No telemetry.** The only thing this package reports about itself is a standard
`User-Agent` string.

## Offline packages

The `countrystatecity-*` packages are versioned offline snapshots — no network,
no key, no quota. They suit development, tests, air-gapped builds, and anything
that must be reproducible.

| Package | Contents |
|---|---|
| [countrystatecity-countries](https://pypi.org/project/countrystatecity-countries/) | Countries, states, cities |
| [countrystatecity-timezones](https://pypi.org/project/countrystatecity-timezones/) | IANA timezones and conversion |
| [countrystatecity-currencies](https://pypi.org/project/countrystatecity-currencies/) | Country/currency associations |
| [countrystatecity-translations](https://pypi.org/project/countrystatecity-translations/) | Country names in 19 languages |
| [countrystatecity-phonecodes](https://pypi.org/project/countrystatecity-phonecodes/) | International dialing codes |
| [countrystatecity-regions](https://pypi.org/project/countrystatecity-regions/) | Regions and subregions |
| [countrystatecity-postal-codes](https://pypi.org/project/countrystatecity-postal-codes/) | Postal/ZIP records and validation |

Use this client instead when you need data that is current rather than pinned,
server-side search and filtering, field-selected responses, fuzzy matching,
managed availability, or support.

[Migration guide](https://github.com/dr5hn/countrystatecity-pypi/blob/main/docs/MIGRATING_TO_API.md) ·
[Compare plans](https://countrystatecity.in/pricing/?utm_source=pypi&utm_medium=package&utm_campaign=python_packages&utm_content=api_client)

## Requirements

Python 3.8+ and [httpx](https://www.python-httpx.org/), which provides both the
sync and async transports.

## License

ODbL-1.0 — see [LICENSE](LICENSE). The geographic data this client retrieves
comes from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
