"""Pydantic models for postal codes."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class CountryPostalInfo(BaseModel):
    """Postal code format metadata for a country."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    countryCode: str
    countryName: str
    postalCodeFormat: Optional[str] = None
    postalCodeRegex: Optional[str] = None
    postcodeCount: int = 0


class Postcode(BaseModel):
    """A single postal code entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str
    countryCode: str
    stateCode: Optional[str] = None
    localityName: Optional[str] = None
    type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
