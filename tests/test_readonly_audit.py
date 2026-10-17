from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from aura_source_identity.audit import audit_source_repository


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "asig-test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "ASIG Test"], check=True)
    (root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "app.py"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline"], check=True)


class ReadOnlyAuditTests(unittest.TestCase):
    def test_audit_emits_source_only_receipt_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "target"
            root.mkdir()
            init_repo(root)
            manifest_path = base / "manifest.json"
            receipt_path = base / "receipt.json"
            receipt = audit_source_repository(
                root,
                repository="test/target",
                source_ref="refs/heads/main",
                manifest_output=manifest_path,
                receipt_output=receipt_path,
            )
            self.assertEqual(receipt["audit_status"], "PASS")
            self.assertFalse(receipt["protocol_conformance_claimed"])
            self.assertFalse(receipt["runtime_tests_executed"])
            self.assertTrue(manifest_path.is_file())
            self.assertTrue(receipt_path.is_file())
            self.assertEqual(json.loads(receipt_path.read_text())["receipt_sha256"], receipt["receipt_sha256"])

    def test_audit_refuses_to_write_inside_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "target"
            root.mkdir()
            init_repo(root)
            with self.assertRaises(ValueError):
                audit_source_repository(
                    root,
                    repository="test/target",
                    source_ref="main",
                    manifest_output=root / "manifest.json",
                    receipt_output=base / "receipt.json",
                )


if __name__ == "__main__":
    unittest.main()
