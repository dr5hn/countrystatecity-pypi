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
    def load_regions(cls) -> List[Dict[str, Any]]:
        """Load all region entries (cached)."""
        regions_file = cls._data_dir / "regions.json"
        if not regions_file.exists():
            return []

        with open(regions_file, encoding="utf-8") as f:
            return cast(List[Dict[str, Any]], json.load(f))

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all caches."""
        cls.load_regions.cache_clear()
