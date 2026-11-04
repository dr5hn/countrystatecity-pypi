"""Prepare offline data versions inside PRs and validate them without writing on release."""

import argparse
import datetime
import re
import subprocess
import tomllib
from pathlib import Path

PACKAGES = (
    "countries",
    "timezones",
    "currencies",
    "translations",
    "phonecodes",
    "regions",
    "postal_codes",
)


def version(content):
    """Read a stable semantic version from project metadata."""
    value = tomllib.loads(content)["project"]["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError(f"Invalid release version: {value}")
    return value


def check(root, base):
    """Require all offline versions to increase in the already merged PR."""
    versions = set()
    for package in PACKAGES:
        directory = root / "python/packages" / package
        project = directory / "pyproject.toml"
        current = version(project.read_text())
        previous = version(
            subprocess.check_output(
                ["git", "show", f"{base}:{project.relative_to(root)}"],
                cwd=root,
                text=True,
            )
        )
        if tuple(map(int, current.split("."))) <= tuple(map(int, previous.split("."))):
            raise ValueError(f"{package}: version must increase inside the release PR")
        init = (directory / f"countrystatecity_{package}/__init__.py").read_text()
        if f'__version__ = "{current}"' not in init:
            raise ValueError(f"{package}: module version differs from project metadata")
        if f"## [{current}]" not in (directory / "CHANGELOG.md").read_text():
            raise ValueError(f"{package}: missing release changelog")
        versions.add(current)
    if len(versions) != 1:
        raise ValueError("Offline release versions must match")
    return versions.pop()


def bump(root):
    """Bump the seven offline packages before creating the data PR, never the API."""
    directories = [root / "python/packages" / package for package in PACKAGES]
    versions = {
        version((directory / "pyproject.toml").read_text()) for directory in directories
    }
    if len(versions) != 1:
        raise ValueError("Refusing to bump mixed offline versions")
    old = versions.pop()
    major, minor, patch = map(int, old.split("."))
    new = f"{major}.{minor}.{patch + 1}"
    # Validate every target before changing any file.
    for package, directory in zip(PACKAGES, directories):
        init = directory / f"countrystatecity_{package}/__init__.py"
        if f'__version__ = "{old}"' not in init.read_text():
            raise ValueError(f"{package}: module version differs from metadata")
        if not (directory / "CHANGELOG.md").read_text().startswith("# Changelog\n"):
            raise ValueError(f"{package}: unexpected changelog layout")
    date = datetime.datetime.now(datetime.UTC).date()
    for package, directory in zip(PACKAGES, directories):
        project = directory / "pyproject.toml"
        project.write_text(
            re.sub(
                r'^version = "' + re.escape(old) + r'"$',
                f'version = "{new}"',
                project.read_text(),
                count=1,
                flags=re.MULTILINE,
            )
        )
        init = directory / f"countrystatecity_{package}/__init__.py"
        init.write_text(
            init.read_text().replace(
                f'__version__ = "{old}"', f'__version__ = "{new}"', 1
            )
        )
        changelog = directory / "CHANGELOG.md"
        changelog.write_text(
            changelog.read_text().replace(
                "# Changelog\n",
                f"# Changelog\n\n## [{new}] - {date}\n\n### Changed\n\n- Refresh the pinned upstream export, notices and release provenance.\n",
                1,
            )
        )
    return new


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["bump", "check"])
    parser.add_argument("--base")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    if args.command == "check" and not args.base:
        parser.error("check requires --base")
    print(bump(root) if args.command == "bump" else check(root, args.base))
