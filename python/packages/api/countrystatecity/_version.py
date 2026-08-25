"""Single source of truth for the package version.

Kept in its own module so :mod:`countrystatecity._core` can build the
``User-Agent`` string without importing the package root, which would create an
import cycle. ``tests/test_metadata.py`` asserts this stays in step with the
version declared in ``pyproject.toml``.
"""

__version__ = "0.2.0"
