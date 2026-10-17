"""Shared subprocess and receipt helpers for ASIG runtime adapters."""
from __future__ import annotations

import hashlib
import json
import math
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        try:
            record = json.loads(line)
            if isinstance(record, dict):
                records.append(record)
            else:
                records.append({"event": "malformed_record", "line": number})
        except json.JSONDecodeError:
            records.append({"event": "malformed_record", "line": number})
    return records


def run_process(argv: list[str], cwd: Path, env: dict[str, str], timeout: float) -> dict[str, Any]:
    if not argv or any(not isinstance(item, str) or not item for item in argv):
        raise ValueError("command must be a non-empty argv list of non-empty strings")
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be a positive finite number")
    started = time.monotonic()
    process = subprocess.Popen(
        argv,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
        stderr = (stderr or "") + "\nASIG_TIMEOUT"
    return {
        "argv": argv,
        "cwd": str(cwd.resolve()),
        "exit_code": 124 if timed_out else process.returncode,
        "timed_out": timed_out,
        "duration_seconds": time.monotonic() - started,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_sha256": sha256_hex((stdout or "").encode("utf-8")),
        "stderr_sha256": sha256_hex((stderr or "").encode("utf-8")),
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")



def verify_manifest_binding(root: Path, manifest_path: Path | None) -> dict[str, Any]:
    """Verify a caller-supplied baseline before/after runtime execution."""
    if manifest_path is None:
        return {"status": "NOT_SUPPLIED", "manifest_sha256": None, "errors": ["no source manifest supplied"]}
    try:
        root = root.resolve(strict=True)
        manifest_path = manifest_path.expanduser().resolve(strict=True)
        if manifest_path == root or root in manifest_path.parents:
            return {"status": "UNKNOWN", "manifest_sha256": None, "errors": ["source manifest must be outside the measured repository"]}
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        from ..inventory import verify_manifest
        result = verify_manifest(manifest, root)
        result["manifest_sha256"] = manifest.get("manifest_sha256")
        return result
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {"status": "UNKNOWN", "manifest_sha256": None, "errors": [str(exc)]}


def combine_snapshot_checks(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Require the same bound source state both before and after the run."""
    if before.get("status") == "MISMATCH" or after.get("status") == "MISMATCH":
        status = "MISMATCH"
    elif before.get("status") == "EXACT_MATCH" and after.get("status") == "EXACT_MATCH" and before.get("manifest_sha256") == after.get("manifest_sha256"):
        status = "EXACT_MATCH"
    else:
        status = "UNKNOWN"
    return {
        "status": status,
        "manifest_sha256": before.get("manifest_sha256"),
        "before": before,
        "after": after,
    }

def add_receipt_digest(receipt: dict[str, Any], digest_fn) -> dict[str, Any]:
    body = dict(receipt)
    body.pop("receipt_sha256", None)
    body["receipt_sha256"] = digest_fn(body)
    return body
