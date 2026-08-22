"""Asynchronous client for the Country State City API."""

from types import TracebackType
from typing import Any, List, Mapping, Optional, Type, Union, cast

import httpx

from . import _endpoints
from ._core import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    build_headers,
    merge_headers,
    normalize_base_url,
    normalize_timeout,
    process_response,
    redacted_repr,
    resolve_api_key,
    translate_transport_error,
)
from ._endpoints import Endpoint, FieldSelection, Identifier
from .errors import ValidationError
from .response import ApiResponse
from .types import (
    City,
    Country,
    CurrencyInfo,
    DialCode,
    IsoConvert,
    IsoCountry,
    IsoState,
    JsonDict,
    PhoneParsed,
    Region,
    State,
    Subregion,
    TimezoneInfo,
)

__all__ = ["AsyncCountryStateCity"]


class AsyncCountryStateCity:
    """Asynchronous client for the Country State City API.

    Every method issues exactly one HTTP ``GET``. The client never retries: a
    silent retry would spend a second request from the caller's quota without
    the caller asking for it. Wrap calls in your own retry policy if you want
    one, and back off on
    :class:`~countrystatecity.errors.RateLimitError`.

    The client holds a connection pool, so reuse one instance for the life of
    your process rather than constructing one per request. Close it with
    :meth:`aclose`, or use it as an async context manager.

    Example:
        >>> import asyncio
        >>> from countrystatecity import AsyncCountryStateCity
        >>> async def main() -> None:
        ...     async with AsyncCountryStateCity() as csc:   # reads CSC_API_KEY
        ...         for country in await csc.get_countries():
        ...             print(country["iso2"], country["name"])
        >>> asyncio.run(main())                              # doctest: +SKIP

    Args:
        api_key: Your API key. Defaults to the ``CSC_API_KEY`` environment
            variable. Get a free key at https://app.countrystatecity.in/.
        base_url: API root. Defaults to the production ``/v1`` endpoint.
        timeout: Seconds allowed per request, or an ``httpx.Timeout``. Must be
            positive and finite.
        headers: Extra headers to send with every request. The API key header
            cannot be set this way.
        transport: An ``httpx.AsyncBaseTransport`` to send through. Useful for tests
            and for custom proxy or TLS setups.

    Raises:
        ConfigurationError: If the key is missing or blank, the base URL is not
            an absolute http(s) URL, or the timeout is not positive and finite.
            All three are checked at construction, before any network I/O.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: Union[int, float, httpx.Timeout] = DEFAULT_TIMEOUT,
        headers: Optional[Mapping[str, str]] = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        self._base_url = normalize_base_url(base_url)
        self._timeout = normalize_timeout(timeout)
        resolved_key = resolve_api_key(api_key)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=merge_headers(build_headers(resolved_key), headers),
            timeout=self._timeout,
            transport=transport,
        )

    # -- lifecycle ---------------------------------------------------------

    async def aclose(self) -> None:
        """Close the underlying connection pool."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncCountryStateCity":
        """Return the client for use in an ``async with`` block."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Close the connection pool on leaving an ``async with`` block."""
        await self.aclose()

    def __repr__(self) -> str:
        """Return a representation with the API key redacted."""
        return redacted_repr(type(self).__name__, self._base_url, self._timeout)

    # -- transport ---------------------------------------------------------

    async def request(
        self, path: str, *, params: Optional[Mapping[str, Any]] = None
    ) -> ApiResponse[Any]:
        """Send a raw ``GET`` and return the body with its response metadata.

        Use this for endpoints this version does not wrap yet, and whenever you
        need the plan, quota, and cache headers alongside the payload.

        Args:
            path: Path relative to the base URL, starting with ``/``.
            params: Query parameters. Values are URL-encoded by the HTTP layer.

        Returns:
            The decoded body plus plan, quota, and cache metadata.

        Raises:
            ValidationError: If ``path`` is not a string starting with ``/``.
            APIConnectionError: If the request never reached the API.
            APIStatusError: If the API returned a non-2xx status.
        """
        if not isinstance(path, str) or not path.startswith("/"):
            raise ValidationError(
                f"path must be a string starting with '/'; got {path!r}."
            )
        return await self._send(Endpoint(path, dict(params or {})))

    async def _send(self, endpoint: Endpoint) -> ApiResponse[Any]:
        """Send one prepared endpoint and decode the result."""
        request = self._client.build_request(
            "GET", endpoint.path, params=endpoint.params or None
        )
        url = str(request.url)
        try:
            response = await self._client.send(request)
        except httpx.HTTPError as exc:
            raise translate_transport_error(exc, method="GET", url=url) from exc
        return process_response(response, method="GET", url=url)

    async def _data(self, endpoint: Endpoint) -> Any:
        """Send one prepared endpoint and return only the decoded body."""
        return (await self._send(endpoint)).data

    # -- countries, states, cities ----------------------------------------

    async def get_countries(
        self,
        *,
        q: Optional[str] = None,
        fields: Optional[FieldSelection] = None,
        sort: Optional[FieldSelection] = None,
    ) -> List[Country]:
        """List every country.

        Args:
            q: Inline search over name and native name, 2-100 characters.
                Requires a plan with the search feature.
            fields: Fields to return, as ``"id,name"`` or ``["id", "name"]``.
                Requires a plan with field selection.
            sort: Sort terms such as ``"name:asc"`` or ``["population:desc"]``.
                Requires a plan with the sort parameter.

        Returns:
            The countries visible to your plan's data-access level.
        """
        return cast(
            List[Country],
            await self._data(_endpoints.countries(q=q, fields=fields, sort=sort)),
        )

    async def get_country(
        self, country: Identifier, *, fields: Optional[FieldSelection] = None
    ) -> Country:
        """Get one country by ISO 3166-1 code or numeric id.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.
            fields: Fields to return. Requires a plan with field selection.

        Returns:
            The country record.

        Raises:
            NotFoundError: If no country matches.
        """
        return cast(
            Country, await self._data(_endpoints.country(country, fields=fields))
        )

    async def get_states(
        self,
        *,
        q: Optional[str] = None,
        fields: Optional[FieldSelection] = None,
        sort: Optional[FieldSelection] = None,
    ) -> List[State]:
        """List every state worldwide.

        Args:
            q: Inline search over name and native name, 2-100 characters.
            fields: Fields to return.
            sort: Sort terms.

        Returns:
            The states visible to your plan.

        Raises:
            PermissionDeniedError: This bulk endpoint is not on every plan.
        """
        return cast(
            List[State],
            await self._data(_endpoints.states(q=q, fields=fields, sort=sort)),
        )

    async def get_states_of_country(
        self,
        country: Identifier,
        *,
        q: Optional[str] = None,
        fields: Optional[FieldSelection] = None,
        sort: Optional[FieldSelection] = None,
    ) -> List[State]:
        """List the states of one country.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.
            q: Inline search over name and native name.
            fields: Fields to return.
            sort: Sort terms.

        Returns:
            The country's states.
        """
        return cast(
            List[State],
            await self._data(
                _endpoints.states_of_country(country, q=q, fields=fields, sort=sort)
            ),
        )

    async def get_state(
        self,
        country: Identifier,
        state: Identifier,
        *,
        fields: Optional[FieldSelection] = None,
    ) -> State:
        """Get one state within a country.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.
            state: The subdivision code, e.g. ``"MH"``.
            fields: Fields to return.

        Returns:
            The state record.

        Raises:
            NotFoundError: If the country has no state with that code.
        """
        return cast(
            State, await self._data(_endpoints.state(country, state, fields=fields))
        )

    async def get_cities_of_country(
        self,
        country: Identifier,
        *,
        q: Optional[str] = None,
        fields: Optional[FieldSelection] = None,
        sort: Optional[FieldSelection] = None,
    ) -> List[City]:
        """List every city in one country.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.
            q: Inline search over name and native name. Strongly recommended --
               large countries return tens of thousands of cities.
            fields: Fields to return.
            sort: Sort terms.

        Returns:
            The country's cities.

        Raises:
            PermissionDeniedError: This endpoint is not on every plan.
        """
        return cast(
            List[City],
            await self._data(
                _endpoints.cities_of_country(country, q=q, fields=fields, sort=sort)
            ),
        )

    async def get_cities_of_state(
        self,
        country: Identifier,
        state: Identifier,
        *,
        q: Optional[str] = None,
        fields: Optional[FieldSelection] = None,
        sort: Optional[FieldSelection] = None,
    ) -> List[City]:
        """List the cities of one state.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.
            state: The subdivision code, e.g. ``"MH"``.
            q: Inline search over name and native name.
            fields: Fields to return.
            sort: Sort terms.

        Returns:
            The state's cities.
        """
        return cast(
            List[City],
            await self._data(
                _endpoints.cities_of_state(
                    country, state, q=q, fields=fields, sort=sort
                )
            ),
        )

    # -- regions -----------------------------------------------------------

    async def get_regions(
        self,
        *,
        q: Optional[str] = None,
        fields: Optional[FieldSelection] = None,
        sort: Optional[FieldSelection] = None,
    ) -> List[Region]:
        """List the continental regions.

        Args:
            q: Inline search over region name.
            fields: Fields to return.
            sort: Sort terms.

        Returns:
            The regions.

        Raises:
            PermissionDeniedError: The regions API is not on every plan.
        """
        return cast(
            List[Region],
            await self._data(_endpoints.regions(q=q, fields=fields, sort=sort)),
        )

    async def get_region(
        self, region_id: Identifier, *, fields: Optional[FieldSelection] = None
    ) -> Region:
        """Get one region by id.

        Args:
            region_id: The region's numeric id.
            fields: Fields to return.

        Returns:
            The region record.
        """
        return cast(
            Region, await self._data(_endpoints.region(region_id, fields=fields))
        )

    async def get_subregions_of_region(
        self,
        region_id: Identifier,
        *,
        q: Optional[str] = None,
        fields: Optional[FieldSelection] = None,
        sort: Optional[FieldSelection] = None,
    ) -> List[Subregion]:
        """List the subregions of one region.

        Args:
            region_id: The region's numeric id.
            q: Inline search over subregion name.
            fields: Fields to return.
            sort: Sort terms.

        Returns:
            The region's subregions.
        """
        return cast(
            List[Subregion],
            await self._data(
                _endpoints.subregions_of_region(
                    region_id, q=q, fields=fields, sort=sort
                )
            ),
        )

    async def get_subregion(
        self, subregion_id: Identifier, *, fields: Optional[FieldSelection] = None
    ) -> Subregion:
        """Get one subregion by id.

        Args:
            subregion_id: The subregion's numeric id.
            fields: Fields to return.

        Returns:
            The subregion record.
        """
        return cast(
            Subregion,
            await self._data(_endpoints.subregion(subregion_id, fields=fields)),
        )

    async def get_countries_of_subregion(
        self,
        subregion_id: Identifier,
        *,
        q: Optional[str] = None,
        fields: Optional[FieldSelection] = None,
        sort: Optional[FieldSelection] = None,
    ) -> List[Country]:
        """List the countries in one subregion.

        Args:
            subregion_id: The subregion's numeric id.
            q: Inline search over country name and native name.
            fields: Fields to return.
            sort: Sort terms.

        Returns:
            The subregion's countries.
        """
        return cast(
            List[Country],
            await self._data(
                _endpoints.countries_of_subregion(
                    subregion_id, q=q, fields=fields, sort=sort
                )
            ),
        )

    # -- timezones ---------------------------------------------------------

    async def get_timezone_of_country(self, country: Identifier) -> TimezoneInfo:
        """Get a country's canonical timezone.

        The API resolves this from the capital city, falling back to the first
        zone listed for the country.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.

        Returns:
            The timezone with its UTC offsets and current DST state.

        Raises:
            NotFoundError: If the country is unknown or has no timezone data.
        """
        return cast(
            TimezoneInfo, await self._data(_endpoints.timezone_of_country(country))
        )

    async def get_timezone_of_state(
        self, country: Identifier, state: Identifier
    ) -> TimezoneInfo:
        """Get a state's timezone.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.
            state: The subdivision code, e.g. ``"MH"``.

        Returns:
            The timezone with its UTC offsets and current DST state.
        """
        return cast(
            TimezoneInfo, await self._data(_endpoints.timezone_of_state(country, state))
        )

    async def get_timezone_of_city(
        self, country: Identifier, state: Identifier, city_id: Identifier
    ) -> TimezoneInfo:
        """Get a city's timezone.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.
            state: The subdivision code, e.g. ``"MH"``.
            city_id: The city's numeric id. The API verifies the city really
                belongs to that country and state.

        Returns:
            The timezone with its UTC offsets and current DST state.
        """
        return cast(
            TimezoneInfo,
            await self._data(_endpoints.timezone_of_city(country, state, city_id)),
        )

    # -- currencies --------------------------------------------------------

    async def get_currencies(self, *, code: Optional[str] = None) -> List[CurrencyInfo]:
        """List country currencies, optionally filtered to one ISO 4217 code.

        Args:
            code: A 3-letter currency code such as ``"EUR"`` to list only the
                countries that use it.

        Returns:
            One entry per country.

        Raises:
            PermissionDeniedError: The currency API is not on every plan.
        """
        return cast(
            List[CurrencyInfo], await self._data(_endpoints.currencies(code=code))
        )

    async def get_currency_of_country(self, country: Identifier) -> CurrencyInfo:
        """Get one country's currency.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.

        Returns:
            The country's currency code, name, and symbol.

        Raises:
            NotFoundError: If the country is unknown or has no currency code.
        """
        return cast(
            CurrencyInfo, await self._data(_endpoints.currency_of_country(country))
        )

    # -- phone -------------------------------------------------------------

    async def get_dial_codes(self, *, code: Optional[str] = None) -> List[DialCode]:
        """List international dial codes, optionally filtered to one code.

        Args:
            code: A dial code such as ``"+1"``, ``"44"``, or ``"1-246"`` to list
                only the countries that use it.

        Returns:
            One entry per country.

        Raises:
            PermissionDeniedError: The dial-code API is not on every plan.
        """
        return cast(List[DialCode], await self._data(_endpoints.dial_codes(code=code)))

    async def get_dial_code_of_country(self, country: Identifier) -> DialCode:
        """Get one country's dial code.

        Args:
            country: ``"IN"``, ``"IND"``, or a numeric country id.

        Returns:
            The country's dial code, and its area code for NANP territories.
        """
        return cast(
            DialCode, await self._data(_endpoints.dial_code_of_country(country))
        )

    async def parse_phone_number(self, number: str) -> PhoneParsed:
        """Split an E.164 phone number into its country and national parts.

        The response echoes the number back. That is personal data: the API
        marks it ``Cache-Control: no-store``, and it should not be logged.

        Args:
            number: The number in E.164 form, e.g. ``"+14155552671"``.

        Returns:
            The originating country plus the national portion of the number.

        Raises:
            ValidationError: If the number is not ``+`` followed by 5-15 digits.
            NotFoundError: If no country matches the dial code.
        """
        return cast(
            PhoneParsed, await self._data(_endpoints.parse_phone_number(number))
        )

    # -- ISO lookups -------------------------------------------------------

    async def lookup_country_iso(
        self,
        *,
        iso2: Optional[str] = None,
        iso3: Optional[str] = None,
        numeric: Optional[str] = None,
    ) -> IsoCountry:
        """Resolve a country from one ISO 3166-1 code.

        Args:
            iso2: An alpha-2 code such as ``"US"``.
            iso3: An alpha-3 code such as ``"USA"``.
            numeric: A numeric code such as ``"840"``.

        Returns:
            The matching country's id, name, and all three codes.

        Raises:
            ValidationError: If anything other than exactly one code is given.
            NotFoundError: If no country carries that code.
        """
        return cast(
            IsoCountry,
            await self._data(
                _endpoints.lookup_country_iso(iso2=iso2, iso3=iso3, numeric=numeric)
            ),
        )

    async def lookup_state_iso(self, iso: str) -> IsoState:
        """Resolve a state from its ISO 3166-2 code.

        Args:
            iso: A subdivision code such as ``"US-CA"``.

        Returns:
            The matching state's id, name, and codes.

        Raises:
            NotFoundError: If no state carries that code.
        """
        return cast(IsoState, await self._data(_endpoints.lookup_state_iso(iso)))

    async def convert_country_code(
        self, value: str, *, from_format: str, to_format: str
    ) -> IsoConvert:
        """Convert a country code between ISO 3166-1 formats.

        Args:
            value: The code to convert.
            from_format: ``"iso2"``, ``"iso3"``, or ``"numeric"``.
            to_format: A different one of the same three.

        Returns:
            The conversion result. The production API returns the input under
            the key ``"input"``.

        Raises:
            ValidationError: If the formats match or the value does not match
                ``from_format``.
            NotFoundError: If the country has no code in the target format.
        """
        return cast(
            IsoConvert,
            await self._data(
                _endpoints.convert_country_code(
                    value, from_format=from_format, to_format=to_format
                )
            ),
        )

    # -- search ------------------------------------------------------------

    async def fuzzy_search(
        self,
        query: str,
        *,
        entity: str = "city",
        country: Optional[str] = None,
        limit: int = 10,
        threshold: float = 0.3,
    ) -> List[JsonDict]:
        """Search cities, states, or countries with tolerance for typos.

        Args:
            query: The search term, 2-100 characters.
            entity: What to search: ``"city"``, ``"state"``, or ``"country"``.
                Sent to the API as its ``type`` parameter.
            country: Restrict results to one alpha-2 country. Not allowed when
                ``entity="country"``.
            limit: Maximum hits, 1-50.
            threshold: Minimum trigram similarity, 0.1-1.0. Lower is more
                forgiving.

        Returns:
            Hits ordered by descending ``match_score``. Each hit carries the
            matched entity's fields plus ``match_score`` and ``matched_alias``;
            see :class:`countrystatecity.types.FuzzyResult`.

        Raises:
            PermissionDeniedError: Fuzzy search is not on every plan.
        """
        return cast(
            List[JsonDict],
            await self._data(
                _endpoints.fuzzy_search(
                    query,
                    entity=entity,
                    country=country,
                    limit=limit,
                    threshold=threshold,
                )
            ),
        )
