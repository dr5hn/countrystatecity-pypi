"""Prove release versions are reviewed in PRs and never changed by release validation."""

import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path

VERSION = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/data_version.py")
)


class DataVersionTests(unittest.TestCase):
    """Exercise version preparation against an isolated temporary Git repository."""

    def setUp(self):
        """Create seven versioned offline packages plus an untouched API sentinel."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for package in (*VERSION["PACKAGES"], "api"):
            directory = self.root / "python/packages" / package
            (directory / f"countrystatecity_{package}").mkdir(parents=True)
            (directory / "pyproject.toml").write_text('[project]\nversion = "3.0.1"\n')
            (directory / f"countrystatecity_{package}/__init__.py").write_text(
                '__version__ = "3.0.1"\n'
            )
            (directory / "CHANGELOG.md").write_text("# Changelog\n\n## [3.0.1]\n")
        self.git("init", "-q")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-qm",
            "baseline",
        )

    def git(self, *arguments):
        """Run Git only inside the test repository."""
        return subprocess.check_output(["git", *arguments], cwd=self.root, text=True)

    def test_bump_and_readonly_validation(self):
        """The bump is a PR diff; validation preserves that diff and excludes API."""
        self.assertEqual(VERSION["bump"](self.root), "3.0.2")
        before = self.git("diff")
        self.assertEqual(VERSION["check"](self.root, "HEAD"), "3.0.2")
        self.assertEqual(before, self.git("diff"))
        self.assertNotIn("packages/api/", before)

    def test_unbumped_release_rejected(self):
        """An unchanged version cannot be published by merging a data-only diff."""
        with self.assertRaisesRegex(ValueError, "increase inside"):
            VERSION["check"](self.root, "HEAD")

    def test_mixed_versions_rejected_without_writes(self):
        """A partial version bump fails before any package is modified."""
        project = self.root / "python/packages/regions/pyproject.toml"
        project.write_text('[project]\nversion = "3.1.0"\n')
        before = self.git("diff")
        with self.assertRaisesRegex(ValueError, "mixed offline"):
            VERSION["bump"](self.root)
        self.assertEqual(before, self.git("diff"))

    def test_missing_changelog_rejected(self):
        """Release metadata includes the reviewed changelog entry."""
        VERSION["bump"](self.root)
        (self.root / "python/packages/regions/CHANGELOG.md").write_text("# Changelog\n")
        with self.assertRaisesRegex(ValueError, "missing release changelog"):
            VERSION["check"](self.root, "HEAD")
