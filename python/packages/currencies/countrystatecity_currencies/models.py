"""Pydantic models for currencies."""

from pydantic import BaseModel, ConfigDict


class Currency(BaseModel):
    """Currency model with country association."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str
    name: str
    symbol: str
    countryCode: str
    countryName: str
