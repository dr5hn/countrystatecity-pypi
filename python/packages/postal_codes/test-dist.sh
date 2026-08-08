#!/bin/bash
set -e

echo "==> Installing build tool..."
pip install build -q

echo "==> Building package..."
python3 -m build

echo ""
echo "==> Creating isolated virtual environment..."
python3 -m venv /tmp/test-csc-postal-codes
/tmp/test-csc-postal-codes/bin/pip install --quiet dist/*.whl

echo ""
echo "==> Running smoke test against built dist..."
/tmp/test-csc-postal-codes/bin/python - <<'EOF'
from countrystatecity_postal_codes import (
    get_countries_with_postal_data,
    get_postal_info_by_country,
    get_postcodes_of_country,
    get_postcode_by_code,
    search_postcodes,
    validate_postcode,
)

all_c = get_countries_with_postal_data()
assert len(all_c) > 200, "Expected 200+ country entries"
print(f"  get_countries_with_postal_data() -> {len(all_c)} entries")

us = get_postal_info_by_country("US")
assert us.postalCodeRegex
print(f"  get_postal_info_by_country(US)   -> {us.postalCodeFormat} / {us.postalCodeRegex}")

assert validate_postcode("US", "10001") is True
assert validate_postcode("US", "not-a-zip") is False
print("  validate_postcode(US, ...)       -> OK")

ad_postcodes = get_postcodes_of_country("AD")
assert len(ad_postcodes) > 0
print(f"  get_postcodes_of_country(AD)     -> {len(ad_postcodes)} postcodes")

pc = get_postcode_by_code("AD", "AD100")
assert pc is not None
print(f"  get_postcode_by_code(AD, AD100)  -> {pc.localityName}")

results = search_postcodes("AD", "canillo")
assert len(results) > 0
print(f"  search_postcodes(AD, 'canillo')  -> {len(results)} results")

print("")
print("All checks passed. Package is ready to publish.")
EOF

echo ""
echo "==> Cleaning up..."
rm -rf /tmp/test-csc-postal-codes
