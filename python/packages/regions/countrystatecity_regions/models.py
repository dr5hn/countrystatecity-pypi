"""Pydantic models for regions."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class CountryRegion(BaseModel):
    """Region/subregion association for a country."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    countryCode: str
    countryName: str
    region: Optional[str] = None
    subregion: Optional[str] = None
