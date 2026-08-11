"""Lazy data loader with caching."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, cast


class DataLoader:
    """Lazy data loader with caching."""

    _data_dir = Path(__file__).parent / "data"

    @classmethod
    @lru_cache(maxsize=1)
    def load_countries(cls) -> List[Dict[str, Any]]:
        """Load country postal metadata (cached)."""
        countries_file = cls._data_dir / "countries.json"
        if not countries_file.exists():
            return []

        with open(countries_file, encoding="utf-8") as f:
            return cast(List[Dict[str, Any]], json.load(f))

    @classmethod
    @lru_cache(maxsize=8)
    def load_postcodes(cls, country_code: str) -> List[Dict[str, Any]]:
        """Load postcodes for a country (cached per country)."""
        country_code = country_code.upper()
        if (
            len(country_code) != 2
            or not country_code.isascii()
            or not country_code.isalpha()
        ):
            return []

        file_path = cls._data_dir / "by-country" / country_code / "postcodes.json"
        if not file_path.exists():
            return []

        try:
            with open(file_path, encoding="utf-8") as f:
                return cast(List[Dict[str, Any]], json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all caches."""
        cls.load_countries.cache_clear()
        cls.load_postcodes.cache_clear()
