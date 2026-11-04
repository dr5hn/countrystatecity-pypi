"""Guard the workflow paths that can publish packages without a manual dispatch."""

import re
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[1] / "workflows"


class PublishSafetyTests(unittest.TestCase):
    """Require an explicit release before an automatic publication."""

    def test_publish_has_no_automatic_event(self):
        """Merging code or dependency changes must not trigger a publication."""
        workflow = (WORKFLOWS / "publish.yml").read_text()
        events = workflow.split("\non:\n", 1)[1].split("\npermissions:\n", 1)[0]
        self.assertEqual(
            set(re.findall(r"^  ([\w_]+):", events, re.MULTILINE)),
            {"workflow_dispatch"},
        )

    def test_release_requires_a_merged_data_update(self):
        """An ordinary dependency PR cannot enter the version-bump job."""
        workflow = (WORKFLOWS / "release.yml").read_text()
        condition = re.search(r"^    if: (.+)$", workflow, re.MULTILINE)
        self.assertIsNotNone(condition)
        self.assertEqual(
            condition.group(1),
            "github.repository == 'dr5hn/countrystatecity-pypi' && "
            "github.ref == 'refs/heads/main' && (github.event_name == 'workflow_dispatch' || "
            "(github.event.pull_request.merged == true && "
            "contains(github.event.pull_request.labels.*.name, 'data-update')))",
        )
        self.assertIn('.merged == true and .base.ref == "main"', workflow)
        self.assertIn('any(.name == "data-update")', workflow)

    def test_publish_requires_a_successful_release_and_exact_ref(self):
        """Skipped, failed, cancelled, and ref-less releases must stay closed."""
        workflow = (WORKFLOWS / "release.yml").read_text()
        job = workflow.split("\n  publish:\n", 1)[1]
        condition = re.search(r"^    if: (.+)$", job, re.MULTILINE)
        self.assertIsNotNone(condition)
        self.assertEqual(
            condition.group(1),
            "needs.release.result == 'success' && needs.release.outputs.ref != ''",
        )
        self.assertIn("    needs: release\n", job)
        self.assertIn("gh workflow run publish.yml", job)
        self.assertIn('--ref main -f package=data -f ref="$RELEASE_REF"', job)
        self.assertIn("RELEASE_REF: ${{ needs.release.outputs.ref }}", job)

    def test_no_other_workflow_calls_publish(self):
        """A new automatic caller needs its own reviewed release gate."""
        callers = [
            path.name
            for path in WORKFLOWS.glob("*.yml")
            if "gh workflow run publish.yml" in path.read_text()
        ]
        self.assertEqual(callers, ["release.yml"])

    def test_external_actions_are_immutable(self):
        """Mutable action tags cannot be introduced into any workflow."""
        for path in WORKFLOWS.glob("*.yml"):
            for action in re.findall(
                r"^\s*(?:- )?uses: (\S+)", path.read_text(), re.MULTILINE
            ):
                with self.subTest(workflow=path.name, action=action):
                    self.assertRegex(action, r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")

    def test_publishing_job_has_no_build_or_checkout(self):
        """OIDC is available only to the artifact-only upload job."""
        workflow = (WORKFLOWS / "publish.yml").read_text()
        job = workflow.split("\n  publish:\n", 1)[1].split("\n  verify:\n", 1)[0]
        self.assertNotIn("checkout@", job)
        self.assertNotIn("run:", job)
        self.assertNotIn("PYPI_TOKEN", workflow)
        self.assertIn("name: pypi", job)
        self.assertIn("attestations: true", job)
        self.assertEqual(workflow.count("id-token: write"), 1)
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn('[ "$SOURCE_REF" = "$GITHUB_SHA" ]', workflow)
        self.assertIn(
            'git merge-base --is-ancestor "$SOURCE_REF" origin/main', workflow
        )

    def test_version_bump_is_reviewed_before_merge(self):
        """The updater stages versions in its PR and cannot auto-merge it."""
        workflow = (WORKFLOWS / "update-data.yml").read_text()
        self.assertIn("data_version.py bump", workflow)
        self.assertNotIn("gh pr merge", workflow)
        updater = workflow.split("\n  validate-pr:\n")[0]
        self.assertNotIn("actions: write", updater)
        self.assertIn("gh workflow run python-ci.yml", workflow)
        self.assertIn('"$ACTUAL_HEAD" = "$EXPECTED_HEAD"', workflow)

    def test_required_gate_cannot_skip_a_matrix_failure(self):
        """One stable protection check covers every package and Python version."""
        workflow = (WORKFLOWS / "python-ci.yml").read_text()
        self.assertIn("name: Release safety gate", workflow)
        self.assertIn("if: always()", workflow)
        self.assertIn("needs: [workflow-safety, test]", workflow)
        self.assertNotIn("    paths:", workflow)

    def test_build_inputs_are_locked(self):
        """Release builds cannot resolve fresh dependencies or isolated build tools."""
        workflow = (WORKFLOWS / "publish.yml").read_text()
        self.assertIn("--require-hashes --only-binary=:all:", workflow)
        self.assertIn("--no-deps --no-build-isolation -e .", workflow)
        self.assertIn("python -m build --no-isolation", workflow)
        build = workflow.split("\n  build:\n", 1)[1].split("\n  publish:\n", 1)[0]
        self.assertNotIn("secrets.", build)
        self.assertNotIn("id-token:", build)
        self.assertIn("persist-credentials: false", build)

    def test_release_preparation_does_not_install_dependencies(self):
        """The version-bump job has write access, so no dependency hooks may run."""
        workflow = (WORKFLOWS / "release.yml").read_text()
        self.assertNotIn("pip install", workflow)
        self.assertNotIn("pytest ", workflow)
        self.assertNotIn("PYPI_TOKEN", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("git push", workflow)
        self.assertIn("data_version.py check --base", workflow)
        self.assertIn("persist-credentials: false", workflow)

    def test_branch_names_are_not_shell_code(self):
        """workflow_run branch names must enter the shell through environment variables."""
        workflow = (WORKFLOWS / "ww-ci-status.yml").read_text()
        self.assertIn("BRANCH: ${{ github.event.workflow_run.head_branch }}", workflow)
        self.assertNotIn('branch="${{', workflow)


if __name__ == "__main__":
    unittest.main()
