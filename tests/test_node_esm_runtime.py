from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from aura_source_identity.runtime.node import run_node


@unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
class NodeEsmRuntimeTests(unittest.TestCase):
    def test_mapped_esm_module_identity_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "repo"
            root.mkdir()
            (root / "probe.mjs").write_text("export const value = 7;\n", encoding="utf-8")
            (root / "app.mjs").write_text("import { value } from './probe.mjs'; if (value !== 7) process.exit(9);\n", encoding="utf-8")
            receipt = run_node(
                root,
                ["node", "app.mjs"],
                {"./probe.mjs": "probe.mjs"},
                output_path=base / "receipt.json",
            )
            self.assertEqual(receipt["command"]["exit_code"], 0)
            self.assertEqual(receipt["module_identity"]["status"], "EXACT_MATCH")
            self.assertEqual(receipt["qualification_status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
