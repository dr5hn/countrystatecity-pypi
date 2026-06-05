#!/bin/bash
set -e

echo "==> Building package..."
python3 -m build

echo ""
echo "==> Creating isolated virtual environment..."
python3 -m venv /tmp/test-csc-currencies
/tmp/test-csc-currencies/bin/pip install --quiet dist/*.whl

echo ""
echo "==> Running smoke test against built dist..."
/tmp/test-csc-currencies/bin/python - <<'EOF'
from countrystatecity_currencies import (
    get_all_currencies,
    get_currency_by_country,
    get_countries_by_currency,
    search_currencies,
)

all_c = get_all_currencies()
assert len(all_c) > 200, "Expected 200+ currencies"
print(f"  get_all_currencies()         -> {len(all_c)} entries")

usd = get_currency_by_country("US")
assert usd.code == "USD" and usd.symbol == "$"
print(f"  get_currency_by_country(US)  -> {usd.symbol} {usd.code} ({usd.name})")

inr = get_currency_by_country("IN")
assert inr.code == "INR" and inr.symbol == "₹"
print(f"  get_currency_by_country(IN)  -> {inr.symbol} {inr.code} ({inr.name})")

euro = get_countries_by_currency("EUR")
assert len(euro) > 1
print(f"  get_countries_by_currency(EUR) -> {len(euro)} countries")

results = search_currencies("dollar")
assert len(results) > 0
print(f"  search_currencies('dollar')  -> {len(results)} results")

print("")
print("All checks passed. Package is ready to publish.")
EOF

echo ""
echo "==> Cleaning up..."
rm -rf /tmp/test-csc-currencies
