from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from integration_harness.validation import ValidationError, validate_review_gate


class ReviewGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.reviews = self.root / "reviews"
        self.reviews.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_review(self, *, verdict: str = "pass", revision: str = "a" * 40) -> None:
        payload = {
            "schema_version": 1,
            "experiment_id": "gate-test",
            "implementation_revision": revision,
            "reviewer_role": "adversarial reviewer",
            "verdict": verdict,
            "objections": [],
        }
        (self.reviews / "gate-test.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    @staticmethod
    def ancestor_true(revision: str, head: str, root: Path) -> bool:
        return True

    @staticmethod
    def ancestor_false(revision: str, head: str, root: Path) -> bool:
        return False

    def test_passes_when_only_review_artifacts_follow_reviewed_revision(self) -> None:
        self.write_review()

        def changed(revision: str, head: str, root: Path) -> list[str]:
            return ["reviews/gate-test.json"]

        result = validate_review_gate(
            self.reviews,
            "b" * 40,
            self.root,
            is_ancestor=self.ancestor_true,
            changed_paths=changed,
        )
        self.assertEqual(result, "gate-test")

    def test_fails_when_substantive_code_changes_follow_review(self) -> None:
        self.write_review()

        def changed(revision: str, head: str, root: Path) -> list[str]:
            return ["reviews/gate-test.json", "src/integration_harness/runtime.py"]

        with self.assertRaises(ValidationError):
            validate_review_gate(
                self.reviews,
                "b" * 40,
                self.root,
                is_ancestor=self.ancestor_true,
                changed_paths=changed,
            )

    def test_fails_when_reviewed_revision_is_not_ancestor(self) -> None:
        self.write_review()
        with self.assertRaises(ValidationError):
            validate_review_gate(
                self.reviews,
                "b" * 40,
                self.root,
                is_ancestor=self.ancestor_false,
                changed_paths=lambda revision, head, root: [],
            )

    def test_nonpassing_review_does_not_cover_head(self) -> None:
        self.write_review(verdict="revise")
        with self.assertRaises(ValidationError):
            validate_review_gate(
                self.reviews,
                "b" * 40,
                self.root,
                is_ancestor=self.ancestor_true,
                changed_paths=lambda revision, head, root: ["reviews/gate-test.json"],
            )

    def test_nested_nonartifact_file_is_not_allowed_after_review(self) -> None:
        self.write_review()

        def changed(revision: str, head: str, root: Path) -> list[str]:
            return ["reviews/archive/gate-test.json"]

        with self.assertRaises(ValidationError):
            validate_review_gate(
                self.reviews,
                "b" * 40,
                self.root,
                is_ancestor=self.ancestor_true,
                changed_paths=changed,
            )


if __name__ == "__main__":
    unittest.main()
