from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from aura_source_identity.inventory import create_manifest
from aura_source_identity.runtime.python import run_python


class PythonRuntimeTests(unittest.TestCase):
    def _workspace(self, root: Path, *, alternate: bool = False) -> dict:
        (root / "alternate").mkdir()
        (root / "probe.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "alternate" / "probe.py").write_text("VALUE = 2\n", encoding="utf-8")
        if alternate:
            test_source = (
                "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).parent / 'alternate'))\n"
                "import probe\ndef test_value():\n    assert probe.VALUE == 2\n"
            )
        else:
            test_source = "import probe\ndef test_value():\n    assert probe.VALUE == 1\n"
        (root / "test_probe.py").write_text(test_source, encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "asig-test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "ASIG Test"], check=True)
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "runtime test baseline"], check=True)
        return create_manifest(root, repository="test/python-runtime")

    def test_exact_loaded_source_and_complete_pytest_suite_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "repo"
            root.mkdir()
            manifest = self._workspace(root)
            manifest_path = base / "manifest.json"
            manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")
            receipt = run_python(
                root,
                ["python", "-m", "pytest", "-q", "test_probe.py"],
                {"probe": "probe.py"},
                required_test_ids=["test_probe.py::test_value"],
                output_path=base / "receipt.json",
                manifest_path=manifest_path,
            )
            self.assertEqual(receipt["source_snapshot"]["status"], "EXACT_MATCH")
            self.assertEqual(receipt["module_identity"]["status"], "EXACT_MATCH")
            self.assertEqual(receipt["test_scope"]["status"], "COMPLETE_PASS")
            self.assertEqual(receipt["qualification_status"], "PASS")

    def test_alternate_copy_is_detected_even_when_test_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "repo"
            root.mkdir()
            manifest = self._workspace(root, alternate=True)
            manifest_path = base / "manifest.json"
            manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")
            receipt = run_python(
                root,
                ["python", "-m", "pytest", "-q", "test_probe.py"],
                {"probe": "probe.py"},
                required_test_ids=["test_probe.py::test_value"],
                output_path=base / "receipt.json",
                manifest_path=manifest_path,
            )
            self.assertEqual(receipt["command"]["exit_code"], 0)
            self.assertEqual(receipt["module_identity"]["status"], "MISMATCH")
            self.assertEqual(receipt["qualification_status"], "FAIL")

    def test_missing_expected_test_keeps_qualification_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "repo"
            root.mkdir()
            manifest = self._workspace(root)
            manifest_path = base / "manifest.json"
            manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")
            receipt = run_python(
                root,
                ["python", "-m", "pytest", "-q", "test_probe.py"],
                {"probe": "probe.py"},
                required_test_ids=["test_probe.py::test_value", "test_probe.py::test_missing"],
                output_path=base / "receipt.json",
                manifest_path=manifest_path,
            )
            self.assertEqual(receipt["source_snapshot"]["status"], "EXACT_MATCH")
            self.assertEqual(receipt["module_identity"]["status"], "EXACT_MATCH")
            self.assertEqual(receipt["test_scope"]["status"], "UNKNOWN")
            self.assertEqual(receipt["qualification_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
