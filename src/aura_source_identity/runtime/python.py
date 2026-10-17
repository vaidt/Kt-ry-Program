"""Python subprocess adapter with cooperative import and pytest observation."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

from ..canonical import object_sha256
from .common import read_jsonl, run_process, sha256_file, write_json


def _python_argv(argv: list[str]) -> tuple[list[str], bool]:
    args = list(argv)
    if args and Path(args[0]).name in {"pytest", "py.test"}:
        return [sys.executable, "-B", "-m", "pytest", "-p", "aura_source_identity.runtime.pytest_plugin", *args[1:]], True
    for index in range(len(args) - 1):
        if Path(args[index]).name.startswith("python") and args[index + 1] == "-m" and index + 2 < len(args) and args[index + 2] == "pytest":
            args.insert(index + 3, "-p")
            args.insert(index + 4, "aura_source_identity.runtime.pytest_plugin")
            return args, True
    return args, False


def run_python(
    root: Path,
    argv: list[str],
    modules: dict[str, str],
    *,
    required_test_ids: list[str] | None = None,
    timeout_seconds: float = 120,
    output_path: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")
    if output_path is None:
        output_path = Path(tempfile.gettempdir()) / f"asig-python-{uuid.uuid4().hex}.json"
    output_path = output_path.expanduser().resolve(strict=False)
    if output_path == root or root in output_path.parents:
        raise ValueError("receipt and observer logs must be outside the measured repository")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_log = output_path.with_suffix(".runtime.jsonl")
    test_log = output_path.with_suffix(".tests.jsonl")
    bootstrap_dir = output_path.with_name(output_path.stem + "-bootstrap")
    bootstrap_dir.mkdir(parents=True, exist_ok=True)
    (bootstrap_dir / "sitecustomize.py").write_text(
        "import os\n"
        "if os.environ.get('ASIG_RUNTIME_OBSERVER') == 'python':\n"
        "    from aura_source_identity.runtime import python_observer  # noqa: F401\n",
        encoding="utf-8",
    )
    runtime_log.unlink(missing_ok=True)
    test_log.unlink(missing_ok=True)

    expected: dict[str, str] = {}
    for module, relative in modules.items():
        if not module or not isinstance(relative, str):
            raise ValueError("modules must map non-empty module names to relative file paths")
        candidate = (root / relative).resolve(strict=True)
        if root not in candidate.parents and candidate != root:
            raise ValueError(f"monitored module path escapes root: {relative}")
        if not candidate.is_file():
            raise ValueError(f"monitored module path is not a file: {relative}")
        expected[module] = str(candidate)

    command, is_pytest = _python_argv(argv)
    asig_src = str(Path(__file__).resolve().parents[2])
    env = os.environ.copy()
    env["ASIG_RUNTIME_OBSERVER"] = "python"
    env["ASIG_RUNTIME_LOG"] = str(runtime_log)
    env["ASIG_TEST_REPORT"] = str(test_log)
    env["ASIG_RUN_ID"] = uuid.uuid4().hex
    env["ASIG_EXPECTED_MODULES"] = json.dumps(expected, sort_keys=True)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = os.pathsep.join([str(bootstrap_dir), asig_src, env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    if is_pytest:
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    try:
        command_result = run_process(command, root, env, timeout_seconds)
    finally:
        (bootstrap_dir / "sitecustomize.py").unlink(missing_ok=True)
        try:
            bootstrap_dir.rmdir()
        except OSError:
            pass
    module_records = [row for row in read_jsonl(runtime_log) if row.get("event") in {"module", "module_unobservable"}]
    process_records = [row for row in read_jsonl(runtime_log) if row.get("event") in {"process_start", "process_end", "observer_error", "observer_bootstrap_error"}]
    test_records = [row for row in read_jsonl(test_log) if row.get("event") == "test_result"]

    statuses = {row.get("module"): row.get("identity_status", "UNKNOWN") for row in module_records if row.get("module")}
    module_statuses: dict[str, str] = {}
    for name in expected:
        related = [row for row in module_records if row.get("module") == name]
        if not related:
            module_statuses[name] = "UNKNOWN"
        elif any(row.get("identity_status") == "MISMATCH" for row in related):
            module_statuses[name] = "MISMATCH"
        elif any(row.get("identity_status") == "UNKNOWN" for row in related):
            module_statuses[name] = "UNKNOWN"
        elif any(row.get("identity_status") == "EQUIVALENT_COPY" for row in related):
            module_statuses[name] = "EQUIVALENT_COPY"
        elif all(row.get("identity_status") == "EXACT_MATCH" for row in related):
            module_statuses[name] = "EXACT_MATCH"
        else:
            module_statuses[name] = "UNKNOWN"

    if module_statuses and any(status == "MISMATCH" for status in module_statuses.values()):
        identity_status = "MISMATCH"
    elif module_statuses and all(status == "EXACT_MATCH" for status in module_statuses.values()):
        identity_status = "EXACT_MATCH"
    elif module_statuses and all(status in {"EXACT_MATCH", "EQUIVALENT_COPY"} for status in module_statuses.values()):
        identity_status = "EQUIVALENT_COPY"
    else:
        identity_status = "UNKNOWN"

    observed_ids = [str(row["nodeid"]) for row in test_records if isinstance(row.get("nodeid"), str)]
    required = list(required_test_ids or [])
    result_statuses = {str(row["nodeid"]): str(row.get("outcome", "UNKNOWN")) for row in test_records if isinstance(row.get("nodeid"), str)}
    required_set = set(required)
    observed_set = set(observed_ids)
    tests_complete = bool(required) and len(required) == len(required_set) and required_set == observed_set and len(observed_ids) == len(observed_set)
    failures = sorted(test_id for test_id in required_set if result_statuses.get(test_id) in {"FAILED", "ERROR"})
    all_pass = tests_complete and not failures and all(result_statuses.get(test_id) == "PASSED" for test_id in required_set)
    if failures or command_result["exit_code"] != 0:
        test_scope_status = "FAIL" if failures or command_result["exit_code"] != 0 else "UNKNOWN"
    elif all_pass:
        test_scope_status = "COMPLETE_PASS"
    else:
        test_scope_status = "UNKNOWN"

    qualification_status = (
        "FAIL" if identity_status == "MISMATCH" or test_scope_status == "FAIL"
        else "PASS" if identity_status == "EXACT_MATCH" and test_scope_status == "COMPLETE_PASS"
        else "BLOCKED"
    )
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "qualification_status": qualification_status,
        "kind": "ASIG_PYTHON_RUNTIME_RECEIPT",
        "runtime": "python",
        "run_id": env["ASIG_RUN_ID"],
        "command": command_result,
        "module_identity": {
            "status": identity_status,
            "expected_modules": sorted(expected),
            "per_module": module_statuses,
            "records": module_records,
        },
        "test_scope": {
            "status": test_scope_status,
            "required_test_ids": required,
            "observed_test_ids": sorted(observed_ids),
            "tests_complete": tests_complete,
            "test_source_hash": sha256_file(Path(__file__).resolve().parents[1] / "runtime" / "pytest_plugin.py"),
            "result_log_sha256": sha256_file(test_log) if test_log.is_file() else None,
            "failures": failures,
        },
        "observer_process_events": process_records,
        "scope_limitations": [
            "Cooperative observation of configured filesystem-backed .py modules only.",
            "Custom import hooks, native extensions, hostile processes, and unconfigured imports are not proven.",
            "Unknown or incomplete observations are not a passing identity result.",
            "A test result is not complete unless required_test_ids exactly match observed test node IDs.",
        ],
    }
    receipt["receipt_sha256"] = object_sha256(receipt)
    write_json(output_path, receipt)
    return receipt
