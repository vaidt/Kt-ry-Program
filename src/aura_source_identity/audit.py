"""Read-only source audit receipts for external repositories."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import object_sha256
from .inventory import create_manifest, verify_manifest
from .runtime.common import write_json


def audit_source_repository(
    root: Path,
    *,
    repository: str,
    source_ref: str,
    manifest_output: Path,
    receipt_output: Path,
    exclude_names: set[str] | None = None,
    exclude_paths: set[str] | None = None,
) -> dict[str, Any]:
    root = root.resolve(strict=True)
    manifest_path = manifest_output.expanduser().resolve(strict=False)
    receipt_path = receipt_output.expanduser().resolve(strict=False)
    for output in (manifest_path, receipt_path):
        if output == root or root in output.parents:
            raise ValueError("manifest and receipt outputs must be outside the repository under audit")
    if manifest_path == receipt_path:
        raise ValueError("manifest and receipt must be separate files")

    manifest = create_manifest(
        root,
        repository=repository,
        exclude_names=exclude_names,
        exclude_paths=exclude_paths,
    )
    verification = verify_manifest(manifest, root)
    audit_status = (
        "PASS" if verification.get("status") == "EXACT_MATCH"
        else "FAIL" if verification.get("status") == "MISMATCH"
        else "BLOCKED"
    )
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "kind": "ASIG_READ_ONLY_SOURCE_AUDIT_RECEIPT",
        "audit_mode": "READ_ONLY_SOURCE_INVENTORY",
        "target": {
            "repository": repository,
            "requested_ref": source_ref,
            "commit_sha": manifest["git"].get("commit_sha"),
            "tree_sha": manifest["git"].get("tree_sha"),
        },
        "source_inventory": {
            "file_count": manifest["inventory"].get("file_count"),
            "source_tree_sha256": manifest["inventory"].get("source_tree_sha256"),
            "manifest_sha256": manifest.get("manifest_sha256"),
            "manifest_path": str(manifest_path),
        },
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_identity_verification": verification,
        "audit_status": audit_status,
        "protocol_conformance_claimed": False,
        "runtime_tests_executed": False,
        "runtime_identity_observed": False,
        "limitations": [
            "This receipt proves a read-only source inventory comparison for the recorded checkout.",
            "No target repository files were modified by the audit command.",
            "No target test suite or live runtime was executed by this command.",
            "The signature authenticates the CI-generated receipt and workflow provenance; it does not make target code or test claims inherently trustworthy.",
        ],
    }
    receipt["receipt_sha256"] = object_sha256(receipt)
    write_json(manifest_path, manifest)
    write_json(receipt_path, receipt)
    return receipt
