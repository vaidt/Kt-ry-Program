"""Node.js subprocess adapter using explicit CommonJS and ESM loader hooks."""
from __future__ import annotations

import json
import os
import shlex
import tempfile
import uuid
from pathlib import Path
from typing import Any

from ..canonical import object_sha256
from .common import combine_snapshot_checks, read_jsonl, run_process, verify_manifest_binding, write_json


def run_node(
    root: Path,
    argv: list[str],
    specifiers: dict[str, str],
    *,
    timeout_seconds: float = 120,
    output_path: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve(strict=True)
    if not argv or Path(argv[0]).name not in {"node", "npm", "npx", "pnpm", "yarn"}:
        raise ValueError("Node adapter requires node/npm/npx/pnpm/yarn as the command executable")
    if output_path is None:
        output_path = Path(tempfile.gettempdir()) / f"asig-node-{uuid.uuid4().hex}.json"
    output_path = output_path.expanduser().resolve(strict=False)
    if output_path == root or root in output_path.parents:
        raise ValueError("receipt and observer logs must be outside the measured repository")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = output_path.with_suffix(".runtime.jsonl")
    log_path.unlink(missing_ok=True)

    expected: dict[str, str] = {}
    for specifier, relative in specifiers.items():
        if not specifier or not isinstance(relative, str):
            raise ValueError("specifiers must map non-empty module specifiers to relative paths")
        candidate = (root / relative).resolve(strict=True)
        if root not in candidate.parents and candidate != root:
            raise ValueError(f"monitored module path escapes root: {relative}")
        if not candidate.is_file():
            raise ValueError(f"monitored module path is not a file: {relative}")
        expected[specifier] = str(candidate)

    runtime_dir = Path(__file__).resolve().parent
    cjs = runtime_dir / "node_cjs_observer.cjs"
    esm = runtime_dir / "node_esm_loader.mjs"
    env = os.environ.copy()
    env["ASIG_RUNTIME_LOG"] = str(log_path)
    env["ASIG_EXPECTED_SPECIFIERS"] = json.dumps(expected, sort_keys=True)
    env["ASIG_RUN_ID"] = uuid.uuid4().hex
    additions = f"--require={cjs} --experimental-loader={esm.as_uri()}"
    env["NODE_OPTIONS"] = (env.get("NODE_OPTIONS", "") + " " + additions).strip()

    snapshot_before = verify_manifest_binding(root, manifest_path)
    command_result = run_process(list(argv), root, env, timeout_seconds)
    snapshot_after = verify_manifest_binding(root, manifest_path)
    source_snapshot = combine_snapshot_checks(snapshot_before, snapshot_after)
    records = [row for row in read_jsonl(log_path) if row.get("event") == "module"]
    per_specifier: dict[str, str] = {}
    for specifier in expected:
        matches = [row for row in records if row.get("specifier") == specifier]
        if not matches:
            per_specifier[specifier] = "UNKNOWN"
        elif any(row.get("identity_status") == "MISMATCH" for row in matches):
            per_specifier[specifier] = "MISMATCH"
        elif any(row.get("identity_status") == "UNKNOWN" for row in matches):
            per_specifier[specifier] = "UNKNOWN"
        elif any(row.get("identity_status") == "EQUIVALENT_COPY" for row in matches):
            per_specifier[specifier] = "EQUIVALENT_COPY"
        elif all(row.get("identity_status") == "EXACT_MATCH" for row in matches):
            per_specifier[specifier] = "EXACT_MATCH"
        else:
            per_specifier[specifier] = "UNKNOWN"
    if per_specifier and any(status == "MISMATCH" for status in per_specifier.values()):
        identity_status = "MISMATCH"
    elif per_specifier and all(status == "EXACT_MATCH" for status in per_specifier.values()):
        identity_status = "EXACT_MATCH"
    elif per_specifier and all(status in {"EXACT_MATCH", "EQUIVALENT_COPY"} for status in per_specifier.values()):
        identity_status = "EQUIVALENT_COPY"
    else:
        identity_status = "UNKNOWN"

    qualification_status = (
        "FAIL" if identity_status == "MISMATCH" or command_result["exit_code"] != 0 or source_snapshot["status"] == "MISMATCH"
        else "BLOCKED"
    )
    command_receipt = {key: value for key, value in command_result.items() if key not in {"stdout", "stderr"}}
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "qualification_status": qualification_status,
        "kind": "ASIG_NODE_RUNTIME_RECEIPT",
        "runtime": "node",
        "run_id": env["ASIG_RUN_ID"],
        "source_snapshot": source_snapshot,
        "command": command_receipt,
        "module_identity": {
            "status": identity_status,
            "expected_specifiers": sorted(expected),
            "per_specifier": per_specifier,
            "records": records,
        },
        "test_scope": {
            "status": "NOT_CAPTURED",
            "note": "This adapter captures mapped module identity and process outcome; use a runner-specific test adapter to prove exact suite completeness.",
        },
        "scope_limitations": [
            "Observes only CommonJS require and ESM imports whose specifier exactly matches an explicit mapping.",
            "Custom loaders, native addons, eval/Function, and unconfigured modules are not proven.",
            "NODE_OPTIONS hooks are cooperative instrumentation, not a hostile-process boundary.",
            "An exit code of zero is not proof that the complete intended test suite executed.",
        ],
    }
    receipt["receipt_sha256"] = object_sha256(receipt)
    write_json(output_path, receipt)
    return receipt
