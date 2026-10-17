from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from aura_source_identity.inventory import create_manifest, verify_manifest


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "asig-test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "ASIG Test"], check=True)
    (root / "sample.txt").write_text("baseline\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "sample.txt"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline"], check=True)


class InventoryTests(unittest.TestCase):
    def test_manifest_is_repeatable_and_verifies_exact_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            init_repo(root)
            manifest = create_manifest(root, repository="test/repo")
            duplicate = create_manifest(root, repository="test/repo")
            self.assertEqual(manifest, duplicate)
            self.assertEqual(verify_manifest(manifest, root)["status"], "EXACT_MATCH")

    def test_source_mutation_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            init_repo(root)
            manifest = create_manifest(root, repository="test/repo")
            (root / "sample.txt").write_text("mutated\n", encoding="utf-8")
            result = verify_manifest(manifest, root)
            self.assertEqual(result["status"], "MISMATCH")
            self.assertFalse(result["source_files_match"])

    def test_manifest_content_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            init_repo(root)
            manifest = create_manifest(root, repository="test/repo")
            damaged = json.loads(json.dumps(manifest))
            damaged["repository"] = "attacker/changed"
            result = verify_manifest(damaged, root)
            self.assertFalse(result["manifest_integrity"])
            self.assertNotEqual(result["status"], "EXACT_MATCH")

    def test_symlinks_are_recorded_without_following(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            init_repo(root)
            (root / "link.txt").symlink_to("sample.txt")
            subprocess.run(["git", "-C", str(root), "add", "link.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "add symlink"], check=True)
            manifest = create_manifest(root, repository="test/repo")
            entry = next(item for item in manifest["inventory"]["files"] if item["path"] == "link.txt")
            self.assertEqual(entry["kind"], "symlink")
            self.assertEqual(entry["target"], "sample.txt")


if __name__ == "__main__":
    unittest.main()
