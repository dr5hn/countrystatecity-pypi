# Changelog

All notable changes to `countrystatecity-api` (imported as
`countrystatecity`) will be documented in this file.

This package is versioned independently of the offline `countrystatecity-*`
data packages: it ships no data, so the weekly upstream data sync does not
change it.

## [0.1.0] - 2026-08-24

### Added
- First release of the official Python client for the Country State City API.
- `CountryStateCity` (synchronous) and `AsyncCountryStateCity` (asyncio), with
  identical method names, signatures, and return payloads. Endpoint routes and
  input validation are defined once and shared by both.
- Coverage of the documented production endpoints: countries, states, cities,
  regions, subregions, timezones, currencies, dial codes and E.164 parsing,
  ISO 3166-1/3166-2 lookup and conversion, and fuzzy search.
- `X-CSCAPI-KEY` authentication from an explicit `api_key` argument or the
  `CSC_API_KEY` environment variable. Missing, blank, and header-unsafe keys are
  rejected at construction, before any network I/O.
- Structured exceptions for transport failures and for HTTP 400, 401, 403, 404,
  429, and 5xx, all under `CountryStateCityError`. `PermissionDeniedError`
  exposes `feature`, `upgrade_url`, `required_tier`, and `current_tier`;
  `RateLimitError` exposes `limit`, `period`, `tier`, `reset_at`, and
  `upgrade_url`. Both of the API's error envelopes are normalised into one
  `details` mapping, and non-JSON error bodies still produce a usable message.
- `ApiResponse`, `ResponseMeta`, and `Quota` expose the plan, daily and monthly
  usage, `X-Cache`, `ETag`, and `Cache-Control` headers through the low-level
  `request()` method, which also serves as an escape hatch for unwrapped routes.
- `TypedDict` payload shapes in `countrystatecity.types` and a `py.typed` marker,
  checked under `mypy --strict`. Every `BIGINT`-backed field -- ids, foreign
  ids, `population`, `gdp` -- is typed `str`, matching the API, which serialises
  bigints as JSON strings so they survive a round trip.
- Trust-boundary validation of path and query inputs mirroring the API's own
  rules, with percent-encoded path segments. The `request()` escape hatch also
  refuses paths that would resolve outside the base URL: `//host`, an embedded
  query or fragment, and `.`/`..` segments including percent-encoded spellings.
- Construction rejects malformed base URLs and header mappings before httpx
  sees them. Raw path and query-parameter validation does not echo caller data.
- Finite request timeouts by default (30 seconds); disabling the timeout is
  refused.

### Notes
- Exception messages and `APIStatusError.url` record the scheme, host, and path
  of a failed request and drop the query string and fragment. Query values are
  caller data -- `/phone/parse?number=` is a phone number, `?q=` is a search
  term -- and exceptions get logged. The request itself is unchanged.
- The client performs no retries. A silent retry would consume a second request
  from the caller's quota.
- No telemetry, and no requests at import time.
- `get_currencies()` calls `GET /currency`. The published OpenAPI contract lists
  this route as `/currencies`, which production does not serve.
- `convert_country_code()` returns the caller's input under the key `input`; the
  contract names that key `value`. Both are declared on the `IsoConvert` type.
