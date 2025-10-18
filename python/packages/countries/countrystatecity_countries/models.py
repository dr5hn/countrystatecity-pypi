"""Pydantic models for countries, states, and cities."""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Country(BaseModel):
    """Country model with full metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: int
    name: str
    iso2: str = Field(..., min_length=2, max_length=2)
    iso3: str = Field(..., min_length=3, max_length=3)
    numeric_code: str
    phone_code: str
    capital: Optional[str] = None
    currency: Optional[str] = None
    currency_name: Optional[str] = None
    currency_symbol: Optional[str] = None
    tld: Optional[str] = None
    native: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    timezones: List[Dict[str, str]] = Field(default_factory=list)
    translations: Dict[str, str] = Field(default_factory=dict)
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    emoji: Optional[str] = None
    emojiU: Optional[str] = None


class State(BaseModel):
    """State/Province model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: int
    name: str
    country_id: int
    country_code: str = Field(..., min_length=2, max_length=2)
    state_code: str
    type: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    iso3166_2: Optional[str] = None
    native: Optional[str] = None
    timezone: Optional[str] = None


class City(BaseModel):
    """City model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: int
    name: str
    state_id: int
    state_code: str
    country_id: int
    country_code: str = Field(..., min_length=2, max_length=2)
    latitude: str
    longitude: str
    wikiDataId: Optional[str] = None
