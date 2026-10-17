from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aura_source_identity.cli import _ensure_outside_root, build_parser


class CliTests(unittest.TestCase):
    def test_exposes_capture_verify_qualify_commands(self) -> None:
        parser = build_parser()
        self.assertEqual(parser.prog, "aura-source-identity")
        choices = parser._subparsers._group_actions[0].choices
        self.assertEqual(set(choices), {"capture", "verify", "qualify"})

    def test_report_path_must_be_outside_measured_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            with self.assertRaises(ValueError):
                _ensure_outside_root(root, str(root / "report.json"))
            _ensure_outside_root(root, str(root.parent / "report.json"))


if __name__ == "__main__":
    unittest.main()
