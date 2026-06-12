# Scripts

## generate-data.py

Generates `translations.json` from the combined countries data source.

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
curl -L "https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/json-countries%2Bstates%2Bcities.json.gz" \
  -o /tmp/countries-data.json.gz
gunzip /tmp/countries-data.json.gz

python scripts/generate-data.py --source /tmp/countries-data.json
```

### Output

- `countrystatecity_translations/data/translations.json` — one entry per country-language pair across 19 languages

### Data Source

https://github.com/dr5hn/countries-states-cities-database
