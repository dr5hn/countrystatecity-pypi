#!/bin/bash
set -e

echo "==> Installing build tool..."
pip install build -q

echo "==> Building package..."
python3 -m build

echo ""
echo "==> Creating isolated virtual environment..."
python3 -m venv /tmp/test-csc-timezones
/tmp/test-csc-timezones/bin/pip install --quiet dist/*.whl

echo ""
echo "==> Running smoke test against built dist..."
/tmp/test-csc-timezones/bin/python - <<'EOF'
from datetime import datetime
from countrystatecity_timezones import (
    get_all_timezones,
    get_timezones_by_country,
    get_timezone_by_zone_name,
    get_timezones_by_offset,
    search_timezones,
    convert_time,
)

all_t = get_all_timezones()
assert len(all_t) > 400, "Expected 400+ timezones"
print(f"  get_all_timezones()                    -> {len(all_t)} entries")

us = get_timezones_by_country("US")
assert len(us) > 5
print(f"  get_timezones_by_country(US)           -> {len(us)} timezones")

tz = get_timezone_by_zone_name("Asia/Kolkata")
assert tz.abbreviation == "IST"
print(f"  get_timezone_by_zone_name(Asia/Kolkata) -> {tz.gmtOffsetName} {tz.abbreviation}")

tzs = get_timezones_by_offset(-18000)
assert len(tzs) > 0
print(f"  get_timezones_by_offset(-18000)        -> {len(tzs)} timezones")

results = search_timezones("eastern")
assert len(results) > 0
print(f"  search_timezones('eastern')            -> {len(results)} results")

result = convert_time(datetime(2024, 1, 1, 12, 0), "America/New_York", "Asia/Kolkata")
assert result.hour == 22 and result.minute == 30
print(f"  convert_time(12:00 NY -> Kolkata)      -> {result.strftime('%H:%M')}")

print("")
print("All checks passed. Package is ready to publish.")
EOF

echo ""
echo "==> Cleaning up..."
rm -rf /tmp/test-csc-timezones
