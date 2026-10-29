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

## 1 November follow-up

The regular Sunday update runs at 00:00 UTC (05:30 India time). Two additional
date-limited checks run at 06:00 and 12:00 UTC (11:30 and 17:30 India time) on
1 November 2026. They require a published `v5.1.0-export.N`, regenerate all seven
offline packages, validate exact export counts, run tests and strict type checks,
then merge the update and dispatch the data-only release. Missing exports and
failed checks leave the update unreleased. The API client is excluded.
