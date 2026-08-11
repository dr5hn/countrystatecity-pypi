# Scripts

## generate-data.py

Generates the postal-codes package data: `countries.json` (postal format/regex
metadata for every country) and `by-country/{ISO2}/postcodes.json` (individual
postcodes, for the 125 countries that have contribution data upstream).

Unlike the other packages, there is no single combined export to source from —
the upstream project publishes postal format/regex on the countries table, and
postcodes as separate per-country contribution files. Both need to be
downloaded first.

### Usage

```bash
# 1. Download country-level postal format/regex metadata
curl -L "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/countries.json" \
  -o /tmp/upstream-countries.json

# 2. Download per-country postcode contribution files (~350MB total, ~125 files)
mkdir -p /tmp/postcodes-raw
curl -s "https://api.github.com/repos/dr5hn/countries-states-cities-database/contents/contributions/postcodes" \
  | python3 -c "import json,sys; print('\n'.join(f['name'] for f in json.load(sys.stdin)))" \
  > /tmp/postcode_files.txt
cd /tmp/postcodes-raw
xargs -P 8 -I{} curl -sS -f -o "{}" \
  "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/contributions/postcodes/{}" \
  < /tmp/postcode_files.txt
cd -

# 3. Generate the package data
python scripts/generate-data.py \
  --countries-source /tmp/upstream-countries.json \
  --postcodes-dir /tmp/postcodes-raw
```

### Output

- `countrystatecity_postal_codes/data/countries.json` — one entry per country with postal code format, validation regex, and postcode count
- `countrystatecity_postal_codes/data/by-country/{ISO2}/postcodes.json` — individual postcodes for countries with contribution data

After a successful generation, stale `postcodes.json` files are removed when
their country no longer has upstream contribution data.

### Data Source

https://github.com/dr5hn/countries-states-cities-database
