from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from aura_source_identity.inventory import create_manifest
from aura_source_identity.runtime.node import run_node


@unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
class NodeRuntimeTests(unittest.TestCase):
    def test_mapped_commonjs_module_identity_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "repo"
            root.mkdir()
            (root / "probe.cjs").write_text("module.exports = { value: 7 };\n", encoding="utf-8")
            (root / "app.cjs").write_text("const probe = require('./probe.cjs'); if (probe.value !== 7) process.exit(9);\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "asig-test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "ASIG Test"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "node test baseline"], check=True)
            manifest_path = base / "manifest.json"
            manifest_path.write_text(json.dumps(create_manifest(root, repository="test/node-runtime")), encoding="utf-8")
            receipt = run_node(
                root,
                ["node", "app.cjs"],
                {"./probe.cjs": "probe.cjs"},
                output_path=base / "receipt.json",
                manifest_path=manifest_path,
            )
            self.assertEqual(receipt["source_snapshot"]["status"], "EXACT_MATCH")
            self.assertEqual(receipt["command"]["exit_code"], 0)
            self.assertEqual(receipt["module_identity"]["status"], "EXACT_MATCH")
            self.assertEqual(receipt["qualification_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
