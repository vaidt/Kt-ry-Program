from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from aura_source_identity.signatures import verify_cosign_blob, verify_github_attestation


class SignatureBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text('{"manifest_sha256":"example"}\n', encoding="utf-8")
        self.bundle = self.root / "manifest.sigstore.json"
        self.bundle.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_cosign_missing_bundle_is_missing(self) -> None:
        result = verify_cosign_blob(
            self.manifest, self.root / "absent.sigstore.json",
            certificate_identity="expected-workflow",
            certificate_oidc_issuer="https://token.actions.githubusercontent.com",
        )
        self.assertEqual(result["status"], "missing")

    @patch("aura_source_identity.signatures.shutil.which", return_value=None)
    def test_missing_cosign_binary_is_unverifiable(self, _which) -> None:
        result = verify_cosign_blob(
            self.manifest, self.bundle,
            certificate_identity="expected-workflow",
            certificate_oidc_issuer="https://token.actions.githubusercontent.com",
        )
        self.assertEqual(result["status"], "unverifiable")

    @patch("aura_source_identity.signatures.shutil.which", return_value="/usr/bin/cosign")
    @patch("aura_source_identity.signatures.subprocess.run")
    def test_cosign_success_is_valid(self, run, _which) -> None:
        run.return_value = SimpleNamespace(returncode=0, stdout="verified", stderr="")
        result = verify_cosign_blob(
            self.manifest, self.bundle,
            certificate_identity="expected-workflow",
            certificate_oidc_issuer="https://token.actions.githubusercontent.com",
        )
        self.assertEqual(result["status"], "valid")
        self.assertIn("--certificate-identity", run.call_args.args[0])

    @patch("aura_source_identity.signatures.shutil.which", return_value="/usr/bin/cosign")
    @patch("aura_source_identity.signatures.subprocess.run")
    def test_cosign_rejection_is_invalid(self, run, _which) -> None:
        run.return_value = SimpleNamespace(returncode=1, stdout="", stderr="signature verification failed")
        result = verify_cosign_blob(
            self.manifest, self.bundle,
            certificate_identity="expected-workflow",
            certificate_oidc_issuer="https://token.actions.githubusercontent.com",
        )
        self.assertEqual(result["status"], "invalid")

    @patch("aura_source_identity.signatures.shutil.which", return_value="/usr/bin/cosign")
    @patch("aura_source_identity.signatures.subprocess.run")
    def test_cosign_network_error_is_unverifiable(self, run, _which) -> None:
        run.return_value = SimpleNamespace(returncode=1, stdout="", stderr="context deadline exceeded")
        result = verify_cosign_blob(
            self.manifest, self.bundle,
            certificate_identity="expected-workflow",
            certificate_oidc_issuer="https://token.actions.githubusercontent.com",
        )
        self.assertEqual(result["status"], "unverifiable")

    @patch("aura_source_identity.signatures.shutil.which", return_value="/usr/bin/gh")
    @patch("aura_source_identity.signatures.subprocess.run")
    def test_github_attestation_without_match_is_missing(self, run, _which) -> None:
        run.return_value = SimpleNamespace(returncode=1, stdout="", stderr="no attestations found for the specified artifact")
        result = verify_github_attestation(self.manifest, repository="owner/repo")
        self.assertEqual(result["status"], "missing")

    @patch("aura_source_identity.signatures.shutil.which", return_value="/usr/bin/gh")
    @patch("aura_source_identity.signatures.subprocess.run")
    def test_github_attestation_success_is_valid(self, run, _which) -> None:
        run.return_value = SimpleNamespace(returncode=0, stdout="Verified", stderr="")
        result = verify_github_attestation(
            self.manifest, repository="owner/repo", signer_workflow="owner/repo/.github/workflows/ci.yml"
        )
        self.assertEqual(result["status"], "valid")
        self.assertIn("--signer-workflow", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
