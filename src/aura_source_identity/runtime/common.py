"""Shared subprocess and receipt helpers for ASIG runtime adapters."""
from __future__ import annotations

import hashlib
import json
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


def add_receipt_digest(receipt: dict[str, Any], digest_fn) -> dict[str, Any]:
    body = dict(receipt)
    body.pop("receipt_sha256", None)
    body["receipt_sha256"] = digest_fn(body)
    return body
