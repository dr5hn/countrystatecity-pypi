"""Pydantic models for timezones."""

from pydantic import BaseModel, ConfigDict


class Timezone(BaseModel):
    """Timezone model with country association."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    zoneName: str
    gmtOffset: int
    gmtOffsetName: str
    abbreviation: str
    tzName: str
    countryCode: str
    countryName: str
