"""Pydantic models for phonecodes."""

from pydantic import BaseModel, ConfigDict


class PhoneCode(BaseModel):
    """Phone code model with country association."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    phoneCode: str
    countryCode: str
    countryName: str
