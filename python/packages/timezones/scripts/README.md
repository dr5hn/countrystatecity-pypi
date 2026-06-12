# Scripts

This directory contains utility scripts for the countrystatecity-timezones package.

## generate-data.py

Generates `timezones.json` from the combined countries-states-cities-database JSON file.

### Usage

```bash
python scripts/generate-data.py
```

Or point to a custom source file:

```bash
python scripts/generate-data.py --source /tmp/countries-data.json
```

### Example — download latest and regenerate

```bash
# Download the latest data
curl -L "https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/json-countries%2Bstates%2Bcities.json.gz" \
  -o /tmp/countries-data.json.gz
gunzip /tmp/countries-data.json.gz

# Regenerate timezones.json
python scripts/generate-data.py --source /tmp/countries-data.json
```

### Output

The script generates:
- `countrystatecity_timezones/data/timezones.json` — 432 timezone entries with country associations

### Data Source

https://github.com/dr5hn/countries-states-cities-database
