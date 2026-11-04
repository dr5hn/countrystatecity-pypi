"""Inspect built distributions and compare accepted releases with live PyPI files."""

import argparse
import hashlib
import json
import re
import tarfile
import time
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def wheel_identity(wheel):
    """Read distribution identity without importing or installing wheel code."""
    with zipfile.ZipFile(wheel) as archive:
        metadata = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata) != 1:
            raise ValueError("Expected exactly one wheel METADATA file")
        message = BytesParser().parsebytes(archive.read(metadata[0]))
    name, version = message["Name"], message["Version"]
    if not name or not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError("Invalid distribution name")
    if not version or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Expected a stable semantic version")
    return name, version


def distributions(directory):
    """Require precisely one wheel and one source archive, with no extra uploads."""
    files = sorted(directory.iterdir())
    wheels = [path for path in files if path.name.endswith(".whl")]
    sources = [path for path in files if path.name.endswith(".tar.gz")]
    if len(files) != 2 or len(wheels) != 1 or len(sources) != 1:
        raise ValueError("Expected exactly one wheel and one sdist")
    return wheels[0], sources[0]


def check(package):
    """Reject identity drift, install-time hooks, unsafe paths and missing notices."""
    wheel, sdist = distributions(package / "dist")
    project = tomllib.loads((package / "pyproject.toml").read_text())["project"]
    if wheel_identity(wheel) != (project["name"], project["version"]):
        raise ValueError("Wheel identity differs from pyproject.toml")
    module = (
        "countrystatecity"
        if package.name == "api"
        else project["name"].replace("-", "_")
    )
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                raise ValueError(f"Unsafe wheel path: {name}")
            if name.endswith(".pth") or ".data/" in name:
                raise ValueError(f"Unexpected installation hook: {name}")
            if path.parts[0] != module and not path.parts[0].endswith(".dist-info"):
                raise ValueError(f"Unexpected top-level wheel payload: {name}")
        if package.name != "api":
            if f"{module}/data/release.json" not in names:
                raise ValueError("Missing release provenance")
            for notice in package.glob("NOTICE-*.txt"):
                if not any(name.endswith("/" + notice.name) for name in names):
                    raise ValueError(f"Missing wheel notice: {notice.name}")
    with tarfile.open(sdist) as archive:
        members = archive.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or "\\" in member.name:
                raise ValueError(f"Unsafe sdist path: {member.name}")
            if not (member.isfile() or member.isdir()):
                raise ValueError(f"Unexpected sdist special file: {member.name}")
        if package.name != "api":
            for notice in package.glob("NOTICE-*.txt"):
                if not any(
                    member.name.endswith("/" + notice.name) for member in members
                ):
                    raise ValueError(f"Missing sdist notice: {notice.name}")
    print(f'Validated {project["name"]} {project["version"]}: wheel and sdist')


def verify(directory):
    """Fail on partial, yanked or byte-different uploads; retry only propagation errors."""
    files = distributions(directory)
    name, version = wheel_identity(files[0])
    expected = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files
    }
    for attempt in range(12):
        try:
            with urlopen(
                f"https://pypi.org/pypi/{name}/{version}/json", timeout=30
            ) as response:
                release = json.load(response)
            rows = {row["filename"]: row for row in release["urls"]}
            if not set(expected).issubset(rows):
                raise LookupError("PyPI release is not complete yet")
            if set(rows) != set(expected):
                raise ValueError("Unexpected extra files on PyPI")
            for filename, digest in expected.items():
                row = rows[filename]
                if row["yanked"] or row["digests"]["sha256"] != digest:
                    raise ValueError(f"Yanked or hash-mismatched PyPI file: {filename}")
                with urlopen(
                    f"https://pypi.org/integrity/{name}/{version}/{filename}/provenance",
                    timeout=30,
                ) as response:
                    provenance = json.load(response)
                # PyPI verifies attestations on upload. This checks its published
                # publisher identity, not an independent Sigstore signature verification.
                expected_publisher = {
                    "kind": "GitHub",
                    "repository": "dr5hn/countrystatecity-pypi",
                    "workflow": "publish.yml",
                    "environment": "pypi",
                }
                if not any(
                    bundle.get("attestations")
                    and all(
                        bundle.get("publisher", {}).get(key) == value
                        for key, value in expected_publisher.items()
                    )
                    for bundle in provenance.get("attestation_bundles", [])
                ):
                    raise ValueError(
                        f"Unexpected or missing PyPI publisher: {filename}"
                    )
                print(f"Verified {filename}: sha256:{digest}")
            return
        except HTTPError as error:
            if error.code != 404 and error.code != 429 and error.code < 500:
                raise
            last_error = error
        except (URLError, TimeoutError, LookupError) as error:
            last_error = error
        if attempt != 11:
            time.sleep(15)
    raise RuntimeError(
        "PyPI did not expose the complete release within three minutes"
    ) from last_error


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "verify"])
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    (check if args.command == "check" else verify)(args.directory)
