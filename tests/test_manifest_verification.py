from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from aura_source_identity.canonical import RFC8785_JCS, canonical_json_bytes, object_sha256
from aura_source_identity.inventory import create_manifest, verify_manifest


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "asig-test@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "ASIG Test"], check=True)
    (root / "sample.txt").write_text("baseline\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "sample.txt"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline"], check=True)


class ManifestSignatureAndCanonicalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        init_repo(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_legacy_manifest_remains_exact_match_and_uses_old_hash_contract(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo")
        self.assertNotIn("canonicalization", manifest)
        expected = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        self.assertEqual(manifest["manifest_sha256"], object_sha256(expected))
        result = verify_manifest(manifest, self.root)
        self.assertEqual(result["status"], "EXACT_MATCH")
        self.assertEqual(result["source_status"], "EXACT_MATCH")
        self.assertEqual(result["signature_status"], "missing")
        self.assertIsNone(result["signature_valid"])

    def test_optional_missing_signature_preserves_legacy_status(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo")
        result = verify_manifest(manifest, self.root, require_signature=False)
        self.assertEqual(result["status"], "EXACT_MATCH")
        self.assertEqual(result["signature_status"], "missing")
        self.assertEqual(result["signature_policy"], "optional")

    def test_required_missing_signature_returns_unknown(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo")
        result = verify_manifest(manifest, self.root, require_signature=True)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["source_status"], "EXACT_MATCH")
        self.assertEqual(result["signature_status"], "missing")
        self.assertIn("manifest_missing_required_signature", result["errors"])

    def test_valid_detached_signature_keeps_exact_match(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo")
        result = verify_manifest(
            manifest, self.root, require_signature=True,
            signature_verifier=lambda: {"status": "valid", "backend": "test"},
        )
        self.assertEqual(result["status"], "EXACT_MATCH")
        self.assertEqual(result["signature_status"], "valid")
        self.assertIs(result["signature_valid"], True)

    def test_invalid_signature_forces_mismatch(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo")
        result = verify_manifest(
            manifest, self.root, require_signature=True,
            signature_verifier=lambda: {"status": "invalid", "backend": "test", "error": "bad signature"},
        )
        self.assertEqual(result["status"], "MISMATCH")
        self.assertEqual(result["source_status"], "EXACT_MATCH")
        self.assertEqual(result["signature_status"], "invalid")
        self.assertIs(result["signature_valid"], False)

    def test_unverifiable_signature_returns_unknown_not_invalid(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo")
        result = verify_manifest(
            manifest, self.root, require_signature=True,
            signature_verifier=lambda: {"status": "unverifiable", "backend": "test", "error": "tool missing"},
        )
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["signature_status"], "unverifiable")
        self.assertIsNone(result["signature_valid"])

    def test_verifier_exception_is_unverifiable(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo")
        def broken_verifier():
            raise RuntimeError("simulated verifier outage")
        result = verify_manifest(manifest, self.root, require_signature=True, signature_verifier=broken_verifier)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["signature_status"], "unverifiable")

    def test_source_mismatch_is_not_masked_by_missing_signature(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo")
        (self.root / "sample.txt").write_text("tampered\n", encoding="utf-8")
        result = verify_manifest(manifest, self.root, require_signature=True)
        self.assertEqual(result["status"], "MISMATCH")
        self.assertEqual(result["source_status"], "MISMATCH")
        self.assertEqual(result["signature_status"], "missing")

    @unittest.skipUnless(importlib.util.find_spec("rfc8785"), "optional rfc8785 package not installed")
    def test_jcs_manifest_declares_encoding_and_verifies(self) -> None:
        manifest = create_manifest(self.root, repository="test/repo", canonicalization=RFC8785_JCS)
        self.assertEqual(manifest["canonicalization"], RFC8785_JCS)
        self.assertEqual(verify_manifest(manifest, self.root)["status"], "EXACT_MATCH")
        self.assertEqual(
            canonical_json_bytes({"b": 2, "a": 1}, strict_rfc8785=True),
            canonical_json_bytes({"a": 1, "b": 2}, strict_rfc8785=True),
        )

    def test_jcs_mode_fails_closed_without_optional_encoder(self) -> None:
        if importlib.util.find_spec("rfc8785"):
            self.skipTest("rfc8785 is installed in this test environment")
        with self.assertRaises(ValueError):
            create_manifest(self.root, repository="test/repo", canonicalization=RFC8785_JCS)

    def test_legacy_encoding_bytes_remain_identical_and_deterministic(self) -> None:
        value = {"z": 1, "a": "é"}
        self.assertEqual(
            canonical_json_bytes(value),
            json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"),
        )
        self.assertEqual(object_sha256(value), object_sha256(dict(reversed(list(value.items())))))

    def test_non_finite_json_numbers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            canonical_json_bytes({"n": float("nan")})


if __name__ == "__main__":
    unittest.main()
