"""Pydantic models for translations."""

from pydantic import BaseModel, ConfigDict


class Translation(BaseModel):
    """Country name translation model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    countryCode: str
    countryName: str
    lang: str
    translation: str
