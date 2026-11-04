# Offline packages: v5 data migration

The seven offline distributions advance together to version 3.0.0 and use
`v5.0.0-export.1`. The API client stays at 0.2.1 and follows the API's data version.

Back up stored IDs before updating. Use the [upstream migration files and
instructions](https://github.com/dr5hn/countries-states-cities-database/releases/tag/v5.0.0)
to review retired IDs and repaired identities. Do not automatically replace an
administrative unit with the town that serves as its seat.

The snapshot has 250 countries, 5,327 states, 152,378 cities and 725,993 postcodes
across 116 countries. Cities without states keep null `state_id` and `state_code`
values and are included by `get_cities_of_country()` and country-wide search.
Population reference years and the full city export's supported model fields
are retained. Counties, hierarchy levels, parent links, local type labels and
city translations are not a separate supported dataset in these packages.

Country, city, postcode and source-notice inputs are downloaded from the same
pinned export. Every offline package contains `data/release.json`, which records
the source tag, asset checksums and complete snapshot counts. Keep `NOTICE-*.txt`
when redistributing the data.

## November refresh

Version 3.0.1 uses `v5.2.0-export.1`, published on 3 November, at source commit
`9b255c45fc53e02a8dff547d88558d4fe91784d5`. It contains 250 countries,
5,327 states, 156,169 cities and 728,556 postcode/locality records across
117 countries. Compared with 3.0.0, there are 3,791 added city IDs, no retired
city IDs and 31,466 existing cities with corrected supported fields. Postcodes
increase by 2,563 records; distinguish records from distinct country/code pairs
(580,593). The API client remains at 0.2.1. County and hierarchy coverage is
not added by this data-only refresh.

Publication now uses isolated builds and PyPI Trusted Publishing with
attestations, subject to owner approval in the `pypi` environment.

## County support in 3.1.0

Version 3.1.0 adds 14,058 county equivalents across 26 countries to the countries
package, with country/state/ID lookups. Seven counties span multiple states or
regions; retain their null primary state fields and use the complete `states`
membership list. `City.county_id` joins to `County.id`. The pinned export and
existing geography/postcode values remain unchanged from 3.0.1. Provenance now
also includes the county asset checksum and count in all seven offline packages.
Empty county translation arrays are normalized to empty maps; nulls stay null.

The API client stays at 0.2.1. Offline county support does not advertise a new
hosted endpoint. State/city hierarchy fields remain outside the public models.
Versions and changelogs are reviewed inside PRs; release preparation no longer
writes to main. The expired 1 November workflow was retired on 4 November.

## Original 1 November checks

The regular Sunday update runs at 00:00 UTC (05:30 India time). Two additional
date-limited checks run at 06:00 and 12:00 UTC (11:30 and 17:30 India time) on
1 November 2026. They require a published `v5.1.0-export.N`, regenerate all seven
offline packages, validate exact export counts, run tests and strict type checks,
then merge the update and dispatch the data-only release. Missing exports and
failed checks leave the update unreleased. The API client is excluded.
