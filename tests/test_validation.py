from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from integration_harness.validation import ValidationError, validate_registry, validate_review


class RegistryValidationTests(unittest.TestCase):
    def write_json(self, payload: dict) -> Path:
        temp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, temp)
        temp.close()
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        return Path(temp.name)

    def donor(self) -> dict:
        return {
            "id": "example",
            "repository": "owner/repo",
            "revision": "a" * 40,
            "license": "MIT",
            "status": "provisional",
            "decision": "wrap",
            "mechanisms": ["memory"],
            "evidence": ["src/memory.py"],
            "notes": "test donor",
        }

    def test_valid_registry(self) -> None:
        path = self.write_json({"schema_version": 1, "donors": [self.donor()]})
        self.assertEqual(validate_registry(path), ["example"])

    def test_duplicate_donor_ids_fail(self) -> None:
        donor = self.donor()
        path = self.write_json({"schema_version": 1, "donors": [donor, dict(donor)]})
        with self.assertRaises(ValidationError):
            validate_registry(path)

    def test_direct_reuse_requires_verified_license(self) -> None:
        donor = self.donor()
        donor["decision"] = "direct_reuse"
        donor["license"] = "verify"
        path = self.write_json({"schema_version": 1, "donors": [donor]})
        with self.assertRaises(ValidationError):
            validate_registry(path)


class ReviewValidationTests(unittest.TestCase):
    def write_json(self, payload: dict) -> Path:
        temp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, temp)
        temp.close()
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        return Path(temp.name)

    def review(self) -> dict:
        return {
            "schema_version": 1,
            "experiment_id": "bootstrap",
            "implementation_revision": "b" * 40,
            "reviewer_role": "adversarial reviewer",
            "verdict": "revise",
            "objections": [
                {
                    "id": "R1",
                    "severity": "high",
                    "status": "open",
                    "claim": "The donor search is incomplete.",
                    "evidence": "No external comparison has been recorded.",
                    "disposition": "Run donor discovery before merge.",
                }
            ],
        }

    def test_revision_review_can_have_open_high_objection(self) -> None:
        path = self.write_json(self.review())
        self.assertEqual(validate_review(path), "bootstrap")

    def test_passing_review_cannot_have_open_high_objection(self) -> None:
        review = self.review()
        review["verdict"] = "pass"
        path = self.write_json(review)
        with self.assertRaises(ValidationError):
            validate_review(path)

    def test_passing_review_accepts_resolved_objection(self) -> None:
        review = self.review()
        review["verdict"] = "pass"
        review["objections"][0]["status"] = "resolved"
        path = self.write_json(review)
        self.assertEqual(validate_review(path), "bootstrap")


if __name__ == "__main__":
    unittest.main()
