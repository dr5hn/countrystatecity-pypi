# countrystatecity-timezones

[![PyPI version](https://badge.fury.io/py/countrystatecity-timezones.svg)](https://badge.fury.io/py/countrystatecity-timezones)
[![Python versions](https://img.shields.io/pypi/pyversions/countrystatecity-timezones.svg)](https://pypi.org/project/countrystatecity-timezones/)

Official Python package for timezone data — 400+ IANA timezones with country associations, GMT offsets, and time conversion utilities. Part of the [countrystatecity](https://github.com/dr5hn/countrystatecity-pypi) ecosystem.

## Installation

```bash
pip install countrystatecity-timezones
```

## Quick Start

```python
from countrystatecity_timezones import (
    get_all_timezones,
    get_timezones_by_country,
    get_timezone_by_zone_name,
    get_timezones_by_offset,
    search_timezones,
    convert_time,
)
from datetime import datetime

# Get all timezones
timezones = get_all_timezones()
# [Timezone(zoneName="Africa/Abidjan", gmtOffset=0, ...), ...]

# Get timezones for a country
us_timezones = get_timezones_by_country("US")
# [Timezone(zoneName="America/Adak", countryCode="US", ...), ...]

# Lookup by IANA zone name
tz = get_timezone_by_zone_name("America/New_York")
# Timezone(zoneName="America/New_York", gmtOffset=-18000, gmtOffsetName="UTC-05:00", ...)

# Filter by GMT offset (seconds)
utc_minus_5 = get_timezones_by_offset(-18000)

# Search by name or abbreviation
results = search_timezones("Eastern")

# Convert time between timezones
dt = datetime(2024, 1, 1, 12, 0, 0)
converted = convert_time(dt, "America/New_York", "Asia/Kolkata")
# datetime(2024, 1, 1, 22, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
```

## Data Model

```python
class Timezone(BaseModel):
    zoneName: str        # IANA timezone name (e.g., "America/New_York")
    gmtOffset: int       # GMT offset in seconds (e.g., -18000)
    gmtOffsetName: str   # Human-readable offset (e.g., "UTC-05:00")
    abbreviation: str    # Timezone abbreviation (e.g., "EST")
    tzName: str          # Full timezone name (e.g., "Eastern Standard Time")
    countryCode: str     # ISO2 country code (e.g., "US")
    countryName: str     # Country name (e.g., "United States")
```

## API Reference

| Function | Description |
|---|---|
| `get_all_timezones()` | Get all timezone entries |
| `get_timezones_by_country(code)` | Get timezones for an ISO2 country code |
| `get_timezone_by_zone_name(name)` | Lookup by IANA zone name |
| `get_timezones_by_offset(seconds)` | Filter by GMT offset in seconds |
| `search_timezones(query)` | Search by zone name, full name, or abbreviation |
| `convert_time(dt, from_tz, to_tz)` | Convert datetime between IANA timezones |

## License

ODbL-1.0 — see [LICENSE](LICENSE).
