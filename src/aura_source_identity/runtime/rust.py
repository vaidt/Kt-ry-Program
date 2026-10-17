"""Rust/Cargo execution adapter; intentionally reports build-context, not runtime-load identity."""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

from ..canonical import object_sha256
from .common import combine_snapshot_checks, run_process, sha256_file, verify_manifest_binding, write_json


def _version(argv: list[str], cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    try:
        result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=10, check=False)
        return {"argv": argv, "exit_code": result.returncode, "output": (result.stdout + result.stderr).strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"argv": argv, "exit_code": None, "output": f"{type(exc).__name__}: {exc}"}


def run_rust(
    root: Path,
    argv: list[str],
    *,
    required_test_ids: list[str] | None = None,
    timeout_seconds: float = 600,
    output_path: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve(strict=True)
    if output_path is None:
        output_path = Path(tempfile.gettempdir()) / f"asig-rust-{uuid.uuid4().hex}.json"
    output_path = output_path.expanduser().resolve(strict=False)
    if output_path == root or root in output_path.parents:
        raise ValueError("receipt must be outside the measured repository")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    snapshot_before = verify_manifest_binding(root, manifest_path)
    command_result = run_process(list(argv), root, env, timeout_seconds)
    snapshot_after = verify_manifest_binding(root, manifest_path)
    source_snapshot = combine_snapshot_checks(snapshot_before, snapshot_after)

    fingerprints: dict[str, Any] = {}
    for name in ("Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "rust-toolchain"):
        file_path = root / name
        if file_path.is_file():
            fingerprints[name] = sha256_file(file_path)
    versions = {"cargo": _version(["cargo", "--version"], root, env), "rustc": _version(["rustc", "--version"], root, env)}

    combined_output = (command_result.get("stdout") or "") + "\n" + (command_result.get("stderr") or "")
    observed: dict[str, str] = {}
    for match in re.finditer(r"^test (.+?) \.\.\. (ok|FAILED|ignored)$", combined_output, flags=re.MULTILINE):
        status = {"ok": "PASS", "FAILED": "FAIL", "ignored": "NOT_APPLICABLE"}[match.group(2)]
        observed[match.group(1)] = status
    required = list(required_test_ids or [])
    required_set = set(required)
    observed_set = set(observed)
    complete = bool(required) and len(required) == len(required_set) and required_set == observed_set
    failures = sorted(test_id for test_id in required_set if observed.get(test_id) == "FAIL")
    all_pass = complete and not failures and all(observed.get(test_id) == "PASS" for test_id in required_set)
    if command_result["exit_code"] != 0 or failures:
        test_status = "FAIL"
    elif all_pass:
        test_status = "COMPLETE_PASS"
    else:
        test_status = "UNKNOWN"

    qualification_status = "FAIL" if command_result["exit_code"] != 0 or source_snapshot["status"] == "MISMATCH" else "BLOCKED"
    command_receipt = {key: value for key, value in command_result.items() if key not in {"stdout", "stderr"}}
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "qualification_status": qualification_status,
        "kind": "ASIG_RUST_CARGO_RECEIPT",
        "runtime": "rust-cargo",
        "run_id": uuid.uuid4().hex,
        "source_snapshot": source_snapshot,
        "command": command_receipt,
        "build_context": {
            "status": "CAPTURED" if versions["cargo"]["exit_code"] == 0 and versions["rustc"]["exit_code"] == 0 else "UNKNOWN",
            "versions": versions,
            "critical_file_sha256": fingerprints,
        },
        "runtime_identity": {
            "status": "NOT_OBSERVED",
            "assurance": "BUILD_CONTEXT_ONLY",
            "note": "This adapter does not instrument Rust module loading or prove which machine-code instructions executed.",
        },
        "test_scope": {
            "status": test_status,
            "required_test_ids": required,
            "observed_test_ids": sorted(observed),
            "observed_results": observed,
            "complete": complete,
            "failures": failures,
        },
        "scope_limitations": [
            "A passing cargo command proves its reported process outcome, not the identity of loaded Rust source modules.",
            "Only Cargo.toml, Cargo.lock, and selected toolchain files are fingerprinted by this adapter; use the source manifest for the full tree.",
            "Full suite completeness requires a caller-supplied expected test ID set and compatible test output.",
        ],
    }
    receipt["receipt_sha256"] = object_sha256(receipt)
    write_json(output_path, receipt)
    return receipt
