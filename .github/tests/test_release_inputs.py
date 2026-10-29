"""Protect the v5 export join from silently omitting country-level cities."""

import runpy
import unittest
from pathlib import Path

JOIN = runpy.run_path(
    str(Path(__file__).resolve().parents[2] / "python/scripts/fetch-release.py")
)["join_cities"]


class ReleaseInputsTests(unittest.TestCase):
    """Require complete and unique city coverage in the immutable snapshot."""

    def test_country_level_city_keeps_its_population_year(self):
        """Cities without states participate in the same enrichment as other cities."""
        countries = [{"id": 1, "states": [], "cities": [{"id": 7}]}]
        JOIN(
            countries,
            [{"id": 7, "country_id": 1, "population": 10, "population_year": 2024}],
        )
        self.assertEqual(countries[0]["cities"][0]["population_year"], 2024)

    def test_missing_country_city_rejects_the_export(self):
        """A missing row in the combined export cannot become an incomplete package."""
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            JOIN([{"id": 1, "states": []}], [{"id": 7, "country_id": 1}])

    def test_city_in_the_wrong_state_rejects_the_export(self):
        """A complete city set must also preserve its actual state associations."""
        countries = [{"id": 1, "states": [{"id": 2, "cities": [{"id": 7}]}]}]
        with self.assertRaisesRegex(ValueError, "State mismatch"):
            JOIN(countries, [{"id": 7, "country_id": 1, "state_id": 3}])
