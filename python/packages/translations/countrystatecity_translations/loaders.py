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
    def load_translations(cls) -> List[Dict[str, Any]]:
        """Load all translations (cached)."""
        translations_file = cls._data_dir / "translations.json"
        if not translations_file.exists():
            return []

        with open(translations_file, encoding="utf-8") as f:
            return cast(List[Dict[str, Any]], json.load(f))

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all caches."""
        cls.load_translations.cache_clear()
