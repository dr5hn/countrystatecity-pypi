#!/bin/bash
set -e

echo "==> Installing build tool..."
pip install build -q

echo "==> Building package..."
python3 -m build

echo ""
echo "==> Creating isolated virtual environment..."
python3 -m venv /tmp/test-csc-regions
/tmp/test-csc-regions/bin/pip install --quiet dist/*.whl

echo ""
echo "==> Running smoke test against built dist..."
/tmp/test-csc-regions/bin/python - <<'EOF'
from countrystatecity_regions import (
    get_all_regions,
    get_region_by_country,
    get_countries_by_region,
    get_countries_by_subregion,
    get_all_region_names,
    search_regions,
)

all_r = get_all_regions()
assert len(all_r) > 200, "Expected 200+ region entries"
print(f"  get_all_regions()               -> {len(all_r)} entries")

us = get_region_by_country("US")
assert us.region == "Americas"
print(f"  get_region_by_country(US)       -> {us.region} / {us.subregion}")

asia = get_countries_by_region("Asia")
assert len(asia) > 1
print(f"  get_countries_by_region(Asia)   -> {len(asia)} countries")

south_asia = get_countries_by_subregion("Southern Asia")
assert len(south_asia) > 1
print(f"  get_countries_by_subregion(...) -> {len(south_asia)} countries")

names = get_all_region_names()
assert "Asia" in names
print(f"  get_all_region_names()          -> {names}")

results = search_regions("southern asia")
assert len(results) > 0
print(f"  search_regions('southern asia') -> {len(results)} results")

print("")
print("All checks passed. Package is ready to publish.")
EOF

echo ""
echo "==> Cleaning up..."
rm -rf /tmp/test-csc-regions
