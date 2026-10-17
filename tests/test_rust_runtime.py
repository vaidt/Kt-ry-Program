from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from aura_source_identity.inventory import create_manifest
from aura_source_identity.runtime.rust import run_rust


@unittest.skipUnless(shutil.which("cargo") and shutil.which("rustc"), "Rust toolchain is not installed")
class RustRuntimeTests(unittest.TestCase):
    def test_cargo_receipt_is_bound_but_does_not_claim_runtime_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "crate"
            (root / "src").mkdir(parents=True)
            (root / ".gitignore").write_text("target/\n", encoding="utf-8")
            (root / "Cargo.toml").write_text(
                '[package]\nname = "asig-runtime-test"\nversion = "0.1.0"\nedition = "2021"\n',
                encoding="utf-8",
            )
            (root / "src" / "lib.rs").write_text(
                '#[cfg(test)] mod tests { #[test] fn passes() { assert_eq!(2 + 2, 4); } }\n',
                encoding="utf-8",
            )
            subprocess.run(["cargo", "generate-lockfile", "--manifest-path", str(root / "Cargo.toml")], check=True, capture_output=True)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "asig-test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "ASIG Test"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline crate"], check=True)
            manifest_path = base / "manifest.json"
            manifest_path.write_text(json.dumps(create_manifest(root, repository="test/rust-runtime")), encoding="utf-8")
            receipt = run_rust(
                root,
                ["cargo", "test", "--locked"],
                required_test_ids=["tests::passes"],
                output_path=base / "receipt.json",
                manifest_path=manifest_path,
            )
            self.assertEqual(receipt["source_snapshot"]["status"], "EXACT_MATCH")
            self.assertEqual(receipt["command"]["exit_code"], 0)
            self.assertEqual(receipt["test_scope"]["status"], "COMPLETE_PASS")
            self.assertEqual(receipt["runtime_identity"]["status"], "NOT_OBSERVED")
            self.assertEqual(receipt["qualification_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
