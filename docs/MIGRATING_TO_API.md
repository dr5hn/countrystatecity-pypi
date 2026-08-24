# Move from an offline package to the API

The `countrystatecity-*` PyPI packages are versioned offline snapshots: the data
they carry is frozen at release time. They are a good fit for offline use,
development, tests, and repeatable builds. Move production lookups to the
Country State City API when you need regularly updated data, server-side search
or filtering, field-selected responses, fuzzy matching, managed availability, or
support.

The shortest path is the official client, `countrystatecity-api` (imported as
`countrystatecity`).

## 1. Install the client and get a key

```bash
pip install countrystatecity-api
```

[Create a free API key](https://app.countrystatecity.in/?utm_source=github&utm_medium=migration_guide&utm_campaign=python_packages),
then store it in a server-side environment variable:

```bash
export CSC_API_KEY="your-api-key"
```

Never put the key in browser code, mobile applications, logs, or source control.
The client sends it only in the `X-CSCAPI-KEY` header and keeps it out of URLs,
`repr()` output, and exception messages. See the
[authentication guide](https://docs.countrystatecity.in/api/authentication) for
deployment guidance.

## 2. Replace local lookups with client calls

An offline state lookup:

```python
from countrystatecity_countries import get_states_of_country

states = get_states_of_country("IN")
```

becomes:

```python
from countrystatecity import CountryStateCity

csc = CountryStateCity()          # reads CSC_API_KEY

states = csc.get_states_of_country("IN")
```

Construct the client once and reuse it — it holds a connection pool. In an
asyncio service, use `AsyncCountryStateCity`, which has the same method names
and signatures.

The core mappings are:

| Offline operation | Client method | API endpoint |
|---|---|---|
| List countries | `get_countries()` | `GET /v1/countries` |
| Get country details | `get_country(country)` | `GET /v1/countries/{country}` |
| List states in a country | `get_states_of_country(country)` | `GET /v1/countries/{country}/states` |
| Get state details | `get_state(country, state)` | `GET /v1/countries/{country}/states/{state}` |
| List cities in a state | `get_cities_of_state(country, state)` | `GET /v1/countries/{country}/states/{state}/cities` |
| List cities in a country | `get_cities_of_country(country)` | `GET /v1/countries/{country}/cities` |
| Region/subregion lookup | `get_regions()`, `get_subregion(id)` | `GET /v1/regions`, `GET /v1/subregions/{id}` |
| Currency lookup | `get_currency_of_country(country)` | `GET /v1/currency/{country}` |
| Phone code lookup | `get_dial_code_of_country(country)` | `GET /v1/phone/{country}` |
| Timezone lookup | `get_timezone_of_country(country)` | `GET /v1/timezone/{country}` |

The [client README](../python/packages/api/README.md) has the full method table,
and the [API reference](https://docs.countrystatecity.in/api/introduction) covers
every endpoint. You can try requests without writing code at the
[playground](https://playground.countrystatecity.in/).

If you would rather call the API directly:

```bash
curl --fail-with-body \
  --header "X-CSCAPI-KEY: $CSC_API_KEY" \
  https://api.countrystatecity.in/v1/countries/IN/states
```

## 3. Choose the response you need

Available fields and query features depend on the plan. The API supports basic
country/state/city traversal on the free Community plan, with higher tiers adding
extended fields, inline filtering, field selection, sorting, translations, and
fuzzy search:

```python
csc.get_cities_of_country("IN", q="pune")                       # inline search
csc.get_countries(fields=["id", "name", "iso2", "emoji"])       # smaller payloads
csc.get_countries(sort="population:desc")                       # server-side order
csc.fuzzy_search("bangalor", entity="city", country="IN")       # typo tolerance
```

Check the [current pricing and feature table](https://countrystatecity.in/pricing/?utm_source=github&utm_medium=migration_guide&utm_campaign=python_packages)
before relying on a plan-specific field.

API response objects are not identical to the offline Pydantic models: the client
returns plain dicts, and which keys are present depends on your plan's data-access
level and your `fields` selection. `countrystatecity.types` documents the shapes.
Read anything outside your plan's guaranteed set with `.get()`, and validate the
fields your application consumes at its API boundary.

## 4. Handle production failure modes

The client raises a structured exception for each failure, all under
`CountryStateCityError`:

```python
from countrystatecity import (
    CountryStateCity,
    APIConnectionError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
)

csc = CountryStateCity(timeout=10.0)

try:
    states = csc.get_states_of_country("IN")
except NotFoundError:
    states = []
except PermissionDeniedError as exc:
    log.warning("plan restriction on %s — upgrade at %s", exc.feature, exc.upgrade_url)
    raise
except RateLimitError as exc:
    log.warning("%s quota of %s exhausted on %s", exc.period, exc.limit, exc.tier)
    raise
except (APIConnectionError, ServerError):
    raise            # retry on your own schedule
```

Points to cover in production:

- `401` for a missing or invalid API key
- `403` for an endpoint or query feature outside the plan, or a blocked
  domain/IP allow-list entry
- `404` for an unknown location
- `429` for a rate limit — back off, and use `exc.limit` / `exc.period` to decide
  how long
- transient `5xx` and connection failures, with bounded retries and backoff

The client sets a finite timeout (30 seconds by default) and never retries on its
own, so a retry policy you add is the only one consuming your quota.

Monitor usage from the responses you already have:

```python
response = csc.request("/countries")
if response.meta.daily.remaining is not None and response.meta.daily.remaining < 50:
    log.warning("daily quota nearly exhausted on the %s plan", response.meta.plan)
```

Do not log the `X-CSCAPI-KEY` header when recording failed requests. The client
never includes it in the exception text it produces.
