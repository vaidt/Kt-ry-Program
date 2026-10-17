from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from aura_source_identity.inventory import create_manifest, verify_manifest
from aura_source_identity.qualification import qualify_evidence


def git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "asig-test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "ASIG Test"], check=True)
    (root / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "module.py"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline"], check=True)


def evidence_for(manifest: dict) -> dict:
    return {
        "schema_version": 1,
        "evidence_id": "ASIG-TEST-001",
        "expected_manifest_sha256": manifest["manifest_sha256"],
        "test_plan": {
            "required_test_ids": ["TEST-001", "TEST-002"],
            "executed_test_ids": ["TEST-001", "TEST-002"],
            "complete": True,
            "expected_test_source_sha256": "a" * 64,
            "observed_test_source_sha256": "a" * 64,
        },
        "test_results": [
            {"test_id": "TEST-001", "status": "PASS"},
            {"test_id": "TEST-002", "status": "PASS"},
        ],
        "independent_evaluation": {
            "status": "PASS",
            "delivered_artifact_sha256": "b" * 64,
            "tested_artifact_sha256": "b" * 64,
        },
    }


class QualificationTests(unittest.TestCase):
    def test_complete_evidence_qualifies_only_for_exact_source_and_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            git_repo(root)
            manifest = create_manifest(root, repository="test/repo")
            result = qualify_evidence(evidence_for(manifest), verify_manifest(manifest, root))
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["required_test_count"], 2)

    def test_missing_required_test_is_blocked_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            git_repo(root)
            manifest = create_manifest(root, repository="test/repo")
            evidence = evidence_for(manifest)
            evidence["test_plan"]["executed_test_ids"] = ["TEST-001"]
            result = qualify_evidence(evidence, verify_manifest(manifest, root))
            self.assertEqual(result["status"], "BLOCKED")
            self.assertTrue(result["blockers"])

    def test_failed_test_dominates_blocked_conditions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            git_repo(root)
            manifest = create_manifest(root, repository="test/repo")
            evidence = evidence_for(manifest)
            evidence["test_results"][0]["status"] = "FAIL"
            result = qualify_evidence(evidence, verify_manifest(manifest, root))
            self.assertEqual(result["status"], "FAIL")

    def test_unknown_source_identity_is_blocked_not_misreported_as_mismatch(self) -> None:
        manifest_verification = {"status": "UNKNOWN", "manifest_sha256": None}
        result = qualify_evidence(
            {
                "schema_version": 1,
                "expected_manifest_sha256": "a" * 64,
                "test_plan": {},
            },
            manifest_verification,
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["failures"])

    def test_invalid_hash_text_cannot_qualify(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            git_repo(root)
            manifest = create_manifest(root, repository="test/repo")
            evidence = evidence_for(manifest)
            evidence["test_plan"]["expected_test_source_sha256"] = "not-a-hash"
            evidence["test_plan"]["observed_test_source_sha256"] = "not-a-hash"
            result = qualify_evidence(evidence, verify_manifest(manifest, root))
            self.assertEqual(result["status"], "BLOCKED")

    def test_evaluator_must_test_delivered_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            git_repo(root)
            manifest = create_manifest(root, repository="test/repo")
            evidence = evidence_for(manifest)
            evidence["independent_evaluation"]["tested_artifact_sha256"] = "c" * 64
            result = qualify_evidence(evidence, verify_manifest(manifest, root))
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("different artifact" in item for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
