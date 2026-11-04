"""Test release checks with synthetic archives; never install their contents."""

import hashlib
import io
import json
import runpy
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ARTIFACTS = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/release_artifacts.py")
)


class ReleaseArtifactTests(unittest.TestCase):
    """Reject unsafe or mismatched packages and registry responses."""

    def setUp(self):
        """Create a minimal source tree and two inert distribution archives."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / "api"
        self.dist = self.package / "dist"
        self.dist.mkdir(parents=True)
        (self.package / "pyproject.toml").write_text(
            '[project]\nname="countrystatecity-api"\nversion="1.0.0"\n'
        )
        self.wheel = self.dist / "countrystatecity_api-1.0.0-py3-none-any.whl"
        with zipfile.ZipFile(self.wheel, "w") as archive:
            archive.writestr("countrystatecity/__init__.py", "")
            archive.writestr(
                "countrystatecity_api-1.0.0.dist-info/METADATA",
                "Name: countrystatecity-api\nVersion: 1.0.0\n",
            )
        self.sdist = self.dist / "countrystatecity_api-1.0.0.tar.gz"
        with tarfile.open(self.sdist, "w:gz") as archive:
            archive.addfile(
                tarfile.TarInfo("countrystatecity_api-1.0.0/PKG-INFO"), io.BytesIO()
            )

    def test_valid_archives(self):
        """An ordinary wheel and sdist pass without executing package code."""
        ARTIFACTS["check"](self.package)

    def test_identity_mismatch(self):
        """Package metadata cannot change the distribution identity silently."""
        (self.package / "pyproject.toml").write_text(
            '[project]\nname="other"\nversion="1.0.0"\n'
        )
        with self.assertRaisesRegex(ValueError, "identity"):
            ARTIFACTS["check"](self.package)

    def test_wheel_installation_hooks_and_traversal(self):
        """Reject .pth files, wheel data hooks and paths escaping the package."""
        for name in (
            "evil.pth",
            "x.data/scripts/run",
            "../escape",
            "/absolute",
            "other/payload.py",
        ):
            with self.subTest(name=name):
                with zipfile.ZipFile(self.wheel, "a") as archive:
                    archive.writestr(name, "")
                with self.assertRaises(ValueError):
                    ARTIFACTS["check"](self.package)
                self.setUp()

    def test_sdist_symlink(self):
        """Source archives must not redirect extraction through symlinks."""
        with tarfile.open(self.sdist, "w:gz") as archive:
            member = tarfile.TarInfo("link")
            member.type = tarfile.SYMTYPE
            member.linkname = "/tmp/escape"
            archive.addfile(member)
        with self.assertRaisesRegex(ValueError, "special file"):
            ARTIFACTS["check"](self.package)

    def test_extra_upload(self):
        """A third file cannot slip into the publication directory."""
        (self.dist / "extra.whl").touch()
        with self.assertRaisesRegex(ValueError, "exactly one"):
            ARTIFACTS["distributions"](self.dist)

    def test_registry_hash_mismatch(self):
        """A successful HTTP status does not prove the expected files were uploaded."""
        response = {
            "urls": [
                {"filename": path.name, "yanked": False, "digests": {"sha256": "wrong"}}
                for path in (self.wheel, self.sdist)
            ]
        }
        with patch.dict(
            ARTIFACTS["verify"].__globals__,
            urlopen=lambda *a, **k: io.BytesIO(json.dumps(response).encode()),
        ), self.assertRaisesRegex(ValueError, "hash-mismatched"):
            ARTIFACTS["verify"](self.dist)

    def test_registry_missing_file_times_out(self):
        """Partial uploads must fail after bounded read-after-write retries."""
        with patch.dict(
            ARTIFACTS["verify"].__globals__,
            urlopen=lambda *a, **k: io.BytesIO(b'{"urls":[]}'),
        ), patch("time.sleep"), self.assertRaisesRegex(
            RuntimeError, "complete release"
        ):
            ARTIFACTS["verify"](self.dist)

    def test_registry_requires_expected_publisher(self):
        """Correct hashes without our trusted-publisher identity are insufficient."""
        response = {
            "urls": [
                {
                    "filename": path.name,
                    "yanked": False,
                    "digests": {
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()
                    },
                }
                for path in (self.wheel, self.sdist)
            ]
        }

        def fetch(url, **kwargs):
            """Serve registry metadata and an absent publisher without networking."""
            return io.BytesIO(
                json.dumps(
                    {"attestation_bundles": []}
                    if url.endswith("/provenance")
                    else response
                ).encode()
            )

        with patch.dict(
            ARTIFACTS["verify"].__globals__, urlopen=fetch
        ), self.assertRaisesRegex(ValueError, "publisher"):
            ARTIFACTS["verify"](self.dist)

    def test_verified_registry_and_downloads(self):
        """Verify both remote files and the publisher without executing either file."""
        contents = {
            f"https://files.pythonhosted.org/packages/{path.name}": path.read_bytes()
            for path in (self.wheel, self.sdist)
        }
        rows = [
            {
                "filename": url.rsplit("/", 1)[1],
                "url": url,
                "yanked": False,
                "digests": {"sha256": hashlib.sha256(content).hexdigest()},
            }
            for url, content in contents.items()
        ]

        def fetch(url, **kwargs):
            """Return exact bytes and our trusted publisher from an inert fixture."""
            if url in contents:
                return io.BytesIO(contents[url])
            data = (
                {
                    "attestation_bundles": [
                        {
                            "publisher": {
                                "kind": "GitHub",
                                "repository": "dr5hn/countrystatecity-pypi",
                                "workflow": "publish.yml",
                                "environment": "pypi",
                            },
                            "attestations": [{}],
                        }
                    ]
                }
                if url.endswith("/provenance")
                else {"urls": rows}
            )
            return io.BytesIO(json.dumps(data).encode())

        with patch.dict(ARTIFACTS["verify"].__globals__, urlopen=fetch):
            ARTIFACTS["verify"](self.dist)
