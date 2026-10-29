"""Fetch one immutable upstream export for all offline packages and its notices."""

import gzip
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "python" / "data"
REPO = "dr5hn/countries-states-cities-database"
PACKAGES = (
    "countries",
    "timezones",
    "currencies",
    "translations",
    "phonecodes",
    "regions",
    "postal_codes",
)


def fetch_bytes(url, token=None):
    """Read a bounded-time HTTPS response, authenticating only GitHub API requests."""
    headers = {
        "User-Agent": "countrystatecity-python",
        "Accept": "application/vnd.github+json",
    }
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=120) as response:
        return response.read()


def join_cities(countries, full_cities):
    """Enrich nested and country-level cities; reject missing or duplicate ids."""
    by_id = {city["id"]: city for city in full_cities}
    seen = set()
    for country in countries:
        groups = [(None, country.get("cities", []))] + [
            (state["id"], state.get("cities", []))
            for state in country.get("states", [])
        ]
        for state_id, cities in groups:
            for city in cities:
                city_id = city["id"]
                if city_id in seen or city_id not in by_id:
                    raise ValueError(f"Missing or duplicate city id: {city_id}")
                seen.add(city_id)
                full = by_id[city_id]
                if full["country_id"] != country["id"]:
                    raise ValueError(f"Country mismatch for city {city_id}")
                if full.get("state_id") != state_id:
                    raise ValueError(f"State mismatch for city {city_id}")
                for field in (
                    "type",
                    "native",
                    "timezone",
                    "population",
                    "population_year",
                    "wikiDataId",
                    "county_id",
                ):
                    city[field] = full.get(field)
    if seen != set(by_id) or len(by_id) != len(full_cities):
        raise ValueError("Combined/full city coverage mismatch")


def main():
    """Stage all release inputs before exposing them to the package generators."""
    token = os.environ.get("GITHUB_TOKEN")
    requested = os.environ.get("CSC_SOURCE_RELEASE") or "latest"
    if requested != "latest" and not re.fullmatch(
        r"v\d+(?:\.\d+)*(?:-export\.\d+)?", requested
    ):
        raise ValueError(f"Unexpected export tag: {requested}")
    endpoint = "latest" if requested == "latest" else f"tags/{requested}"
    release = json.loads(
        fetch_bytes(f"https://api.github.com/repos/{REPO}/releases/{endpoint}", token)
    )
    if (
        release.get("draft")
        or release.get("prerelease")
        or not release.get("published_at")
    ):
        raise ValueError("Only a published stable export can supply package data")
    tag = release["tag_name"]
    if not re.fullmatch(r"v\d+(?:\.\d+)*(?:-export\.\d+)?", tag):
        raise ValueError(f"Unexpected export tag: {tag}")
    assets = {asset["name"]: asset for asset in release["assets"]}
    DATA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".fetch-", dir=DATA) as temp:
        staging = Path(temp)
        checksums = {}

        def download_asset(name, compressed=True):
            """Verify GitHub's compressed asset digest before decoding it."""
            asset = assets[name]
            content = fetch_bytes(asset["browser_download_url"])
            digest = "sha256:" + hashlib.sha256(content).hexdigest()
            if digest != asset.get("digest"):
                raise ValueError(f"Checksum mismatch: {name}")
            checksums[name] = digest
            return gzip.decompress(content) if compressed else content

        countries = json.loads(download_asset("json-countries+states+cities.json.gz"))
        full_cities = json.loads(download_asset("json-cities.json.gz"))
        join_cities(countries, full_cities)
        (staging / "source.json").write_text(
            json.dumps(countries, ensure_ascii=False), encoding="utf-8"
        )
        # Postal format/regex live in the country source, not the combined export.
        metadata = json.loads(
            fetch_bytes(
                f"https://raw.githubusercontent.com/{REPO}/{tag}/contributions/countries/countries.json"
            )
        )
        if {row["id"] for row in metadata} != {row["id"] for row in countries}:
            raise ValueError("Country metadata does not match the pinned export")
        (staging / "countries.json").write_text(
            json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
        )
        grouped = {}
        for row in json.loads(download_asset("json-postcodes.json.gz")):
            code = row["country_code"]
            if not re.fullmatch(r"[A-Z]{2}", code):
                raise ValueError(f"Invalid postcode country: {code!r}")
            grouped.setdefault(code, []).append(row)
        (staging / "postcodes").mkdir()
        for code, rows in grouped.items():
            (staging / "postcodes" / f"{code}.json").write_text(
                json.dumps(rows, ensure_ascii=False), encoding="utf-8"
            )
        notices = [
            name
            for name in assets
            if re.fullmatch(r"NOTICE-[A-Za-z0-9_.-]+\.txt", name)
        ]
        if "NOTICE-SOURCES.txt" not in notices:
            raise ValueError("Release is missing NOTICE-SOURCES.txt")
        for name in notices:
            (staging / name).write_bytes(download_asset(name, compressed=False))
        record = {
            "sourceRelease": tag,
            "sourceCommit": release["target_commitish"],
            "sourceUrl": release["html_url"],
            "checksums": checksums,
            "counts": {
                "countries": len(countries),
                "cities": len(full_cities),
                "postcodes": sum(map(len, grouped.values())),
            },
        }
        (staging / "release.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
        # Replace only this script's generated input files.
        for name in ("source.json", "countries.json", "release.json"):
            shutil.copyfile(staging / name, DATA / name)
        postcodes_dir = DATA / "postcodes"
        backup = DATA / "postcodes.previous"
        if backup.exists():
            if not postcodes_dir.exists():
                backup.rename(postcodes_dir)
            else:
                shutil.rmtree(backup)
        if postcodes_dir.exists():
            postcodes_dir.rename(backup)
        try:
            (staging / "postcodes").rename(postcodes_dir)
        except BaseException:
            if backup.exists():
                backup.rename(postcodes_dir)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        for package in PACKAGES:
            package_dir = ROOT / "python" / "packages" / package
            for name in notices:
                shutil.copyfile(staging / name, package_dir / name)
            shutil.copyfile(
                staging / "release.json",
                package_dir / f"countrystatecity_{package}" / "data" / "release.json",
            )
    print(
        f"Pinned all offline package inputs to {tag}: {len(countries)} countries, {len(full_cities)} cities"
    )


if __name__ == "__main__":
    main()
