# Scripts

This directory contains utility scripts for the countrystatecity-countries package.

## generate-data.py

Generates the split data structure from the combined countries-states-cities-database JSON file.

### Usage

```bash
python scripts/generate-data.py <path-to-combined-json>
```

### Example

```bash
# Download the latest data
curl -L "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/heads/master/json/countries%2Bstates%2Bcities.json.gz" \
  -o /tmp/countries-data.json.gz
gunzip /tmp/countries-data.json.gz

# Generate split data structure
python scripts/generate-data.py /tmp/countries-data.json
```

### Output Structure

The script generates:
- `countrystatecity_countries/data/countries.json` - Lightweight list of all countries
- `countrystatecity_countries/data/by-country/{ISO2}/states.json` - States for each country
- `countrystatecity_countries/data/by-country/{ISO2}/states/{STATE_CODE}/cities.json` - Cities for each state

### Data Source

The script expects data from: https://github.com/dr5hn/countries-states-cities-database

The combined JSON file is available at:
https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/countries%2Bstates%2Bcities.json.gz
