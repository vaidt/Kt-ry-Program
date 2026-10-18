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
        self.assertEqual(set(choices), {"capture", "verify", "qualify", "audit", "runtime-python", "runtime-node", "runtime-rust"})

    def test_capture_accepts_explicit_jcs_mode(self) -> None:
        args = build_parser().parse_args(["capture", "--output", "../manifest.json", "--canonicalization", "rfc8785"])
        self.assertEqual(args.canonicalization, "rfc8785")

    def test_verify_accepts_required_cosign_signature(self) -> None:
        args = build_parser().parse_args([
            "verify", "--manifest", "../manifest.json", "--require-signature",
            "--signature-bundle", "../manifest.sigstore.json",
            "--certificate-identity", "expected-identity",
            "--certificate-oidc-issuer", "https://token.actions.githubusercontent.com",
        ])
        self.assertTrue(args.require_signature)
        self.assertEqual(args.signature_backend, "cosign-blob")

    def test_verify_accepts_github_dsse_attestation(self) -> None:
        args = build_parser().parse_args([
            "verify", "--manifest", "../manifest.json", "--require-signature",
            "--signature-backend", "github-attestation",
            "--attestation-repository", "owner/repo",
            "--attestation-signer-workflow", "owner/repo/.github/workflows/ci.yml",
        ])
        self.assertEqual(args.signature_backend, "github-attestation")

    def test_report_path_must_be_outside_measured_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            with self.assertRaises(ValueError):
                _ensure_outside_root(root, str(root / "report.json"))
            _ensure_outside_root(root, str(root.parent / "report.json"))


if __name__ == "__main__":
    unittest.main()
