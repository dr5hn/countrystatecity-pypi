"""Official Python client for the Country State City API.

Talks to the managed API at https://api.countrystatecity.in/v1 -- continuously
updated geographic data with server-side search, field selection, sorting, and
fuzzy matching. Authentication is a single header, ``X-CSCAPI-KEY``.

Get a free key at https://app.countrystatecity.in/ and export it:

.. code-block:: bash

    export CSC_API_KEY="your-api-key"

Then:

    >>> from countrystatecity import CountryStateCity
    >>> csc = CountryStateCity()          # reads CSC_API_KEY
    >>> india = csc.get_country("IN")     # doctest: +SKIP
    >>> states = csc.get_states_of_country("IN")  # doctest: +SKIP

The same surface is available without blocking:

    >>> from countrystatecity import AsyncCountryStateCity
    >>> async with AsyncCountryStateCity() as csc:      # doctest: +SKIP
    ...     india = await csc.get_country("IN")

Keep the key in a server-side environment variable. It is never logged, never
placed in a URL, and never included in this package's exception messages or
``repr`` output -- but it does grant access to your quota, so it does not belong
in browser code, mobile apps, or source control.

The offline ``countrystatecity-*`` packages remain available as versioned
snapshots for development and air-gapped builds. This client is the production
path.
"""

from ._core import API_KEY_ENV_VAR, DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from ._version import __version__
from .aio import AsyncCountryStateCity
from .client import CountryStateCity
from .errors import (
    APIConnectionError,
    APIResponseError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConfigurationError,
    CountryStateCityError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .response import ApiResponse, Quota, ResponseMeta
from .types import (
    City,
    Country,
    CurrencyDetail,
    CurrencyInfo,
    DialCode,
    FuzzyResult,
    IsoConvert,
    IsoCountry,
    IsoState,
    PhoneParsed,
    Region,
    State,
    Subregion,
    TimezoneInfo,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "AsyncCountryStateCity",
    "CountryStateCity",
    # Configuration
    "API_KEY_ENV_VAR",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    # Errors
    "APIConnectionError",
    "APIResponseError",
    "APIStatusError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "ConfigurationError",
    "CountryStateCityError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    # Response metadata
    "ApiResponse",
    "Quota",
    "ResponseMeta",
    # Payload types
    "City",
    "Country",
    "CurrencyDetail",
    "CurrencyInfo",
    "DialCode",
    "FuzzyResult",
    "IsoConvert",
    "IsoCountry",
    "IsoState",
    "PhoneParsed",
    "Region",
    "State",
    "Subregion",
    "TimezoneInfo",
]
