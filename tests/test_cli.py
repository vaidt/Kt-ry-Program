from __future__ import annotations

import unittest

from aura_source_identity.cli import build_parser


class CliTests(unittest.TestCase):
    def test_exposes_capture_verify_qualify_commands(self) -> None:
        parser = build_parser()
        self.assertEqual(parser.prog, "aura-source-identity")
        choices = parser._subparsers._group_actions[0].choices
        self.assertEqual(set(choices), {"capture", "verify", "qualify"})


if __name__ == "__main__":
    unittest.main()
