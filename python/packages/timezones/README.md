# countrystatecity-timezones

[![PyPI](https://img.shields.io/pypi/v/countrystatecity-timezones)](https://pypi.org/project/countrystatecity-timezones/)
[![Python Version](https://img.shields.io/pypi/pyversions/countrystatecity-timezones)](https://pypi.org/project/countrystatecity-timezones/)
[![License](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](LICENSE)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy.readthedocs.io/)
[![timezones](https://static.pepy.tech/personalized-badge/countrystatecity-timezones?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=timezones)](https://pepy.tech/project/countrystatecity-timezones)
[![timezones](https://static.pepy.tech/personalized-badge/countrystatecity-timezones?period=week&units=international_system&left_color=grey&right_color=brightgreen&left_text=timezones)](https://pepy.tech/project/countrystatecity-timezones)

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

## Other Packages in this Ecosystem

| Package | Description |
|---|---|
| [countrystatecity-countries](https://pypi.org/project/countrystatecity-countries/) | 250+ countries, 5,000+ states, 150,000+ cities |
| [countrystatecity-currencies](https://pypi.org/project/countrystatecity-currencies/) | Currency codes, names, and symbols for every country |
| [countrystatecity-translations](https://pypi.org/project/countrystatecity-translations/) | Country name translations in 18+ languages |
| [countrystatecity-phonecodes](https://pypi.org/project/countrystatecity-phonecodes/) | International phone/dialing codes for 250+ countries |

Data sourced from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database).

---

Made with ❤️ by [dr5hn](https://github.com/dr5hn)
