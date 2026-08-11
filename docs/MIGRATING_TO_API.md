# Move from an offline package to the API

The PyPI packages are a good fit for offline use, development, tests, and
repeatable snapshots. Move production lookups to the Country State City API when
you need regularly updated data, server-side search or filtering, field-selected
responses, managed availability, or support.

## 1. Get an API key

[Create a free API key](https://app.countrystatecity.in/?utm_source=github&utm_medium=migration_guide&utm_campaign=python_packages),
then store it in a server-side environment variable:

```bash
export CSC_API_KEY="your-api-key"
```

Never put the key in browser code, mobile applications, logs, or source control.
See the [authentication guide](https://docs.countrystatecity.in/api/authentication)
for deployment guidance.

## 2. Replace local lookups with API requests

For example, an offline state lookup:

```python
from countrystatecity_countries import get_states_of_country

states = get_states_of_country("IN")
```

maps to this API endpoint:

```bash
curl --fail-with-body \
  --header "X-CSCAPI-KEY: $CSC_API_KEY" \
  https://api.countrystatecity.in/v1/countries/IN/states
```

The core location mappings are:

| Offline operation | API endpoint |
|---|---|
| List countries | `GET /v1/countries` |
| Get country details | `GET /v1/countries/{country}` |
| List states in a country | `GET /v1/countries/{country}/states` |
| Get state details | `GET /v1/countries/{country}/states/{state}` |
| List cities in a state | `GET /v1/countries/{country}/states/{state}/cities` |
| List cities in a country | `GET /v1/countries/{country}/cities` |

See the [API reference](https://docs.countrystatecity.in/api/introduction) for
region, currency, ISO, phone-code, timezone, and search endpoints.

## 3. Choose the response you need

Available fields and query features depend on the plan. The API supports basic
country/state/city traversal on the free Community plan, with higher tiers adding
extended fields, inline filtering, field selection, sorting, translations, and
fuzzy search. Check the [current pricing and feature table](https://countrystatecity.in/pricing/?utm_source=github&utm_medium=migration_guide&utm_campaign=python_packages)
before relying on a plan-specific field.

API response objects are not guaranteed to be identical to the offline Pydantic
models. Validate the fields your application consumes at its API boundary.

## 4. Handle production failure modes

Production clients should set a timeout and handle at least:

- `401` for a missing or invalid API key
- `404` for an unknown location
- `429` for a rate limit, respecting the response's retry guidance
- transient `5xx` failures with bounded retries and backoff

Do not log the `X-CSCAPI-KEY` header when recording failed requests.
