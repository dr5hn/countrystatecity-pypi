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
        events = workflow.split("\non:\n", 1)[1].split("\nenv:\n", 1)[0]
        self.assertEqual(
            set(re.findall(r"^  ([\w_]+):", events, re.MULTILINE)),
            {"workflow_dispatch", "workflow_call"},
        )

    def test_release_requires_a_merged_data_update(self):
        """An ordinary dependency PR cannot enter the version-bump job."""
        workflow = (WORKFLOWS / "release.yml").read_text()
        condition = re.search(r"^    if: (.+)$", workflow, re.MULTILINE)
        self.assertIsNotNone(condition)
        self.assertEqual(
            condition.group(1),
            "github.event_name == 'workflow_dispatch' || "
            "(github.event.pull_request.merged == true && "
            "contains(github.event.pull_request.labels.*.name, 'data-update'))",
        )
        self.assertIn(".merged == true and .base.ref == \"main\"", workflow)
        self.assertIn("any(.name == \"data-update\")", workflow)

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
        self.assertIn("    uses: ./.github/workflows/publish.yml\n", job)
        self.assertIn("      package: data\n", job)
        self.assertIn("      ref: ${{ needs.release.outputs.ref }}\n", job)

    def test_no_other_workflow_calls_publish(self):
        """A new automatic caller needs its own reviewed release gate."""
        callers = [
            path.name
            for path in WORKFLOWS.glob("*.yml")
            if "uses: ./.github/workflows/publish.yml" in path.read_text()
        ]
        self.assertEqual(callers, ["release.yml"])


if __name__ == "__main__":
    unittest.main()
