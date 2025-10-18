# Python PyPI vs NPM Package Comparison

Quick reference guide comparing the npm and Python implementations.

---

## Package Naming

| Aspect | NPM | Python |
|--------|-----|--------|
| **Scope** | `@countrystatecity/*` | `countrystatecity-*` |
| **Countries** | `@countrystatecity/countries` | `countrystatecity-countries` |
| **Timezones** | `@countrystatecity/timezones` | `countrystatecity-timezones` |
| **Currencies** | `@countrystatecity/currencies` | `countrystatecity-currencies` |
| **Import Name** | `@countrystatecity/countries` | `countrystatecity_countries` |

---

## Installation

```bash
# NPM
npm install @countrystatecity/countries

# Python
pip install countrystatecity-countries
```

---

## Basic Usage Comparison

### NPM (TypeScript)
```typescript
import { 
  getCountries, 
  getCountryByCode,
  getStatesOfCountry 
} from '@countrystatecity/countries';

const countries = await getCountries();
const usa = await getCountryByCode('US');
const states = await getStatesOfCountry('US');
```

### Python
```python
from countrystatecity_countries import (
    get_countries,
    get_country_by_code,
    get_states_of_country
)

countries = get_countries()
usa = get_country_by_code('US')
states = get_states_of_country('US')
```

---

## Type Systems

### NPM (TypeScript)
```typescript
interface Country {
  id: number;
  name: string;
  iso2: string;
  iso3: string;
  capital?: string;
  currency?: string;
  // ...
}

interface State {
  id: number;
  name: string;
  country_code: string;
  state_code: string;
  // ...
}
```

### Python (Pydantic)
```python
from pydantic import BaseModel, Field
from typing import Optional

class Country(BaseModel):
    id: int
    name: str
    iso2: str = Field(..., min_length=2, max_length=2)
    iso3: str = Field(..., min_length=3, max_length=3)
    capital: Optional[str] = None
    currency: Optional[str] = None
    
    class Config:
        frozen = True  # Immutable

class State(BaseModel):
    id: int
    name: str
    country_code: str
    state_code: str
    
    class Config:
        frozen = True
```

---

## Data Loading

### NPM
```typescript
// Dynamic imports for lazy loading
export async function getCountryByCode(code: string): Promise<Country> {
  const data = await import(`./data/by-country/${code}/meta.json`);
  return data;
}
```

### Python
```python
# LRU cache for lazy loading
from functools import lru_cache
import json

@lru_cache(maxsize=250)
def load_country_metadata(country_code: str) -> dict:
    file_path = Path(__file__).parent / "data" / "by-country" / country_code / "meta.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
```

---

## Project Configuration

### NPM (package.json)
```json
{
  "name": "@countrystatecity/countries",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
  }
}
```

### Python (pyproject.toml)
```toml
[project]
name = "countrystatecity-countries"
version = "1.0.0"
requires-python = ">=3.8"
dependencies = ["pydantic>=2.0.0,<3.0.0"]

[project.urls]
Homepage = "https://github.com/dr5hn/countries-states-cities-database"
Repository = "https://github.com/dr5hn/countries-states-cities-database"
```

---

## Testing

### NPM (Vitest)
```typescript
import { describe, it, expect } from 'vitest';
import { getCountries, getCountryByCode } from '../src';

describe('Countries', () => {
  it('should get all countries', async () => {
    const countries = await getCountries();
    expect(countries.length).toBeGreaterThan(250);
  });

  it('should get country by code', async () => {
    const usa = await getCountryByCode('US');
    expect(usa.name).toBe('United States');
  });
});
```

### Python (pytest)
```python
import pytest
from countrystatecity_countries import get_countries, get_country_by_code

def test_get_countries():
    countries = get_countries()
    assert len(countries) >= 250

def test_get_country_by_code():
    usa = get_country_by_code('US')
    assert usa.name == 'United States'
    assert usa.iso2 == 'US'
```

---

## Build Tools

| Aspect | NPM | Python |
|--------|-----|--------|
| **Package Manager** | pnpm | Poetry |
| **Build Tool** | tsup | setuptools |
| **Bundler** | esbuild | N/A |
| **Type Checker** | tsc | mypy |
| **Linter** | ESLint | ruff |
| **Formatter** | Prettier | black + isort |
| **Test Runner** | Vitest | pytest |

---

## Directory Structure Comparison

### NPM
```
packages/countries/
├── src/
│   ├── index.ts
│   ├── types.ts
│   ├── loaders.ts
│   └── data/
│       ├── countries.json
│       └── by-country/
├── tests/
├── package.json
├── tsconfig.json
└── tsup.config.ts
```

### Python
```
python/packages/countries/
├── countrystatecity_countries/
│   ├── __init__.py
│   ├── models.py
│   ├── loaders.py
│   ├── api.py
│   ├── py.typed
│   └── data/
│       ├── countries.json
│       └── by-country/
├── tests/
│   ├── test_countries.py
│   ├── test_states.py
│   └── test_cities.py
└── pyproject.toml
```

---

## CI/CD

### NPM (GitHub Actions)
```yaml
- name: Install dependencies
  run: pnpm install

- name: Build
  run: pnpm build

- name: Test
  run: pnpm test

- name: Type check
  run: pnpm typecheck

- name: Publish
  run: pnpm publish
```

### Python (GitHub Actions)
```yaml
- name: Install Poetry
  run: curl -sSL https://install.python-poetry.org | python3 -

- name: Install dependencies
  run: poetry install

- name: Test
  run: poetry run pytest --cov

- name: Type check
  run: poetry run mypy .

- name: Build
  run: poetry build

- name: Publish
  run: poetry publish
```

---

## API Style Differences

### Function Naming

| NPM (camelCase) | Python (snake_case) |
|-----------------|---------------------|
| `getCountries()` | `get_countries()` |
| `getCountryByCode()` | `get_country_by_code()` |
| `getStatesOfCountry()` | `get_states_of_country()` |
| `getCitiesOfState()` | `get_cities_of_state()` |
| `searchCountries()` | `search_countries()` |

### Async/Await

**NPM:** Uses `async/await` for dynamic imports
```typescript
const countries = await getCountries();
```

**Python:** Synchronous by default (no async needed for file I/O)
```python
countries = get_countries()
```

---

## Framework Integration

### NPM (React Example)
```typescript
import { useEffect, useState } from 'react';
import { getCountries, Country } from '@countrystatecity/countries';

function CountrySelect() {
  const [countries, setCountries] = useState<Country[]>([]);

  useEffect(() => {
    getCountries().then(setCountries);
  }, []);

  return (
    <select>
      {countries.map(c => (
        <option key={c.iso2} value={c.iso2}>{c.name}</option>
      ))}
    </select>
  );
}
```

### Python (Flask Example)
```python
from flask import Flask, jsonify
from countrystatecity_countries import get_countries

app = Flask(__name__)

@app.route('/api/countries')
def api_countries():
    countries = get_countries()
    return jsonify([c.dict() for c in countries])

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Package Size

| Aspect | NPM | Python |
|--------|-----|--------|
| **Initial Bundle** | ~10KB | N/A (not bundled) |
| **Installed Size** | ~50MB | ~50MB |
| **Import Time** | <50ms | <50ms |
| **Memory (Base)** | ~5MB | ~5MB |

---

## Data Structure (Identical)

Both packages use the **same JSON structure**:

```json
{
  "id": 233,
  "name": "United States",
  "iso2": "US",
  "iso3": "USA",
  "numeric_code": "840",
  "phone_code": "+1",
  "capital": "Washington",
  "currency": "USD",
  "currency_name": "United States dollar",
  "currency_symbol": "$",
  "tld": ".us",
  "native": "United States",
  "region": "Americas",
  "subregion": "Northern America",
  "timezones": [...],
  "translations": {...},
  "latitude": "38.00000000",
  "longitude": "-97.00000000",
  "emoji": "🇺🇸",
  "emojiU": "U+1F1FA U+1F1F8"
}
```

---

## Key Similarities

1. ✅ **Same data source** - MySQL database
2. ✅ **Same structure** - Split JSON files
3. ✅ **Lazy loading** - Only load what's needed
4. ✅ **Type safety** - Full type definitions
5. ✅ **Immutable models** - Prevent accidental mutations
6. ✅ **Comprehensive tests** - 80%+ coverage
7. ✅ **Professional packaging** - Modern best practices

---

## Key Differences

### TypeScript vs Python
- **TypeScript:** Compile-time type checking, interfaces
- **Python:** Runtime type validation with Pydantic

### Async Handling
- **TypeScript:** Promises/async-await for dynamic imports
- **Python:** Synchronous with LRU caching

### Package Distribution
- **NPM:** ESM + CJS bundles for browser/Node.js
- **Python:** Wheel + source distribution for Python environments

### Bundle Optimization
- **NPM:** Critical for web apps (tree-shaking, code splitting)
- **Python:** Less critical (server-side, not bandwidth-constrained)

---

## Development Workflow

### NPM
```bash
# Setup
pnpm install

# Develop
pnpm dev

# Test
pnpm test

# Build
pnpm build

# Publish
pnpm publish
```

### Python
```bash
# Setup
poetry install

# Develop (no watch mode needed)

# Test
poetry run pytest

# Build
poetry build

# Publish
poetry publish
```

---

## Summary

Both packages provide **identical functionality** with language-specific optimizations:

- **NPM:** Optimized for modern web development (ESM, tree-shaking, bundle size)
- **Python:** Optimized for server-side and data science (Pydantic, type hints, pip)

The API design is **consistent** across languages, making it easy for developers familiar with one to use the other.
