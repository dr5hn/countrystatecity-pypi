# Scripts

## Generate the pinned geography snapshot

Run from the repository root after installing the reviewed release dependencies and the local countries package:

```bash
CSC_SOURCE_RELEASE=v5.2.0-export.1 python python/scripts/fetch-release.py
python python/packages/countries/scripts/generate-data.py python/data/source.json python/data/counties.json
python python/scripts/check-release.py
```

The fetcher verifies release-asset digests and pins country metadata to the resolved source commit. Do not mix a mutable latest URL with county data from a different tag.

The generator writes `countries.json` and lazy files under `by-country/{ISO2}/`: `states.json`, `counties.json`, optional country-level `cities.json`, and `states/{STATE_CODE}/cities.json`. Counties are validated before their files are replaced; retired county files are removed only within this generated subtree. Cross-state memberships remain explicit. Empty county translation arrays become empty maps; other source fields retain their values.

The update workflow prepares version/changelog changes in its PR. Release preparation validates that PR without pushing to main.
