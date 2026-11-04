"""Pydantic models for countries, states, and cities."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
    state_id: Optional[int]
    state_code: Optional[str]
    country_id: int
    country_code: str = Field(..., min_length=2, max_length=2)
    latitude: str
    longitude: str
    county_id: Optional[int] = None
    wikiDataId: Optional[str] = None
    type: Optional[str] = None
    native: Optional[str] = None
    timezone: Optional[str] = None
    population: Optional[int] = None
    population_year: Optional[int] = None


class CountyState(BaseModel):
    """A county's membership in a state, including cross-state counties."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    state_id: int = Field(gt=0)
    state_code: str = Field(min_length=1)


class County(BaseModel):
    """County equivalent with country-specific coverage and state membership."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: int = Field(gt=0)
    name: str
    country_id: int = Field(gt=0)
    country_code: str = Field(pattern=r"^[A-Z]{2}$")
    state_id: Optional[int] = Field(default=None, gt=0)
    state_code: Optional[str] = None
    states: Optional[List[CountyState]] = None
    type: Optional[str] = None
    type_local: Optional[str] = None
    level: Optional[int] = None
    parent_id: Optional[int] = Field(default=None, gt=0)
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    native: Optional[str] = None
    population: Optional[int] = None
    timezone: Optional[str] = None
    translations: Optional[Dict[str, str]] = None
    wikiDataId: Optional[str] = None

    @field_validator("translations", mode="before")
    @classmethod
    def normalize_empty_translations(cls, value: Any) -> Any:
        """The upstream exporter also represents empty translation maps as []."""
        return {} if isinstance(value, list) and not value else value

    @model_validator(mode="after")
    def validate_state_membership(self) -> "County":
        """Do not invent a single state for a cross-state county."""
        if (self.state_id is None) != (self.state_code is None):
            raise ValueError("County state id and code must both be present or null")
        links = self.states or []
        if len({link.state_id for link in links}) != len(links):
            raise ValueError("Duplicate county state membership")
        if len(links) > 1 and self.state_id is not None:
            raise ValueError("Cross-state county must retain a null primary state")
        return self
