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
        """Load countries list (cached)."""
        countries_file = cls._data_dir / "countries.json"
        if not countries_file.exists():
            return []

        with open(countries_file, encoding="utf-8") as f:
            return cast(List[Dict[str, Any]], json.load(f))

    @classmethod
    @lru_cache(maxsize=250)
    def load_country_metadata(cls, country_code: str) -> Dict[str, Any]:
        """Load full country metadata (cached per country)."""
        file_path = cls._data_dir / "by-country" / country_code / "meta.json"
        if not file_path.exists():
            return {}

        with open(file_path, encoding="utf-8") as f:
            return cast(Dict[str, Any], json.load(f))

    @classmethod
    @lru_cache(maxsize=250)
    def load_states(cls, country_code: str) -> List[Dict[str, Any]]:
        """Load states for country (cached per country)."""
        file_path = cls._data_dir / "by-country" / country_code / "states.json"
        if not file_path.exists():
            return []

        try:
            with open(file_path, encoding="utf-8") as f:
                return cast(List[Dict[str, Any]], json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @classmethod
    @lru_cache(maxsize=5000)
    def load_cities(cls, country_code: str, state_code: str) -> List[Dict[str, Any]]:
        """Load cities for state (cached per state)."""
        file_path = (
            cls._data_dir
            / "by-country"
            / country_code
            / "states"
            / state_code
            / "cities.json"
        )
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
        cls.load_country_metadata.cache_clear()
        cls.load_states.cache_clear()
        cls.load_cities.cache_clear()
