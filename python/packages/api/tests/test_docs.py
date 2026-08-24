"""The README's method tables stay in step with the code.

Documentation that names a method the client does not have is worse than no
documentation, so the tables are checked against the real surface.
"""

import re
from pathlib import Path
from typing import List, Set

import pytest

from countrystatecity import AsyncCountryStateCity, CountryStateCity

README = Path(__file__).resolve().parents[1] / "README.md"

#: Matches the first cell of an API-reference table row, e.g.
#: ``| `get_country(country, fields=)` | `GET /countries/{ciso}` |``
_ROW = re.compile(r"^\| `([a-z_]+)\(", re.MULTILINE)


def documented_methods() -> List[str]:
    """Return every method name the README's reference tables list."""
    return sorted(set(_ROW.findall(README.read_text(encoding="utf-8"))))


def test_readme_documents_the_endpoint_methods() -> None:
    """Guards against the regex silently matching nothing."""
    assert len(documented_methods()) >= 24


@pytest.mark.parametrize("name", documented_methods())
def test_documented_method_exists_on_both_clients(name: str) -> None:
    assert callable(getattr(CountryStateCity, name, None)), name
    assert callable(getattr(AsyncCountryStateCity, name, None)), name


def test_every_public_method_is_documented() -> None:
    """A new endpoint must be added to the README in the same change."""
    public: Set[str] = {
        name
        for name in dir(CountryStateCity)
        if not name.startswith("_") and name not in {"close"}
    }
    assert public - set(documented_methods()) == set()
