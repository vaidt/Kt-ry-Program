"""Cooperative Python source observer used only by an explicit ASIG run.

This observer establishes identity only for configured filesystem-backed .py
modules which pass through the standard PathFinder. It is not a hostile-process
sandbox and does not claim coverage of native extensions, custom loaders, or
modules outside the configured mapping.
"""
from __future__ import annotations

import atexit
import hashlib
import importlib.abc
import importlib.machinery
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

_MARKER = "_asig_runtime_observer_installed"


def _append(record: dict[str, Any]) -> None:
    destination = os.environ.get("ASIG_RUNTIME_LOG")
    if not destination:
        return
    try:
        with open(destination, "a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    except OSError:
        # Missing or malformed observer evidence is later qualified as UNKNOWN.
        return


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_read(path: Path) -> bytes:
    before = path.stat()
    content = path.read_bytes()
    after = path.stat()
    signature_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    signature_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if signature_before != signature_after or len(content) != after.st_size:
        raise RuntimeError("source changed while being observed")
    return content


def _common(event: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "event": event,
        "run_id": os.environ.get("ASIG_RUN_ID"),
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "interpreter": sys.executable,
        "cwd": os.getcwd(),
        "monotonic_ns": time.monotonic_ns(),
    }


class _CapturedSourceLoader:
    def __init__(self, fullname: str, origin: Path, expected: Path, package: bool):
        self.fullname = fullname
        self.origin = origin
        self.expected = expected
        self.package = package

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        record = {
            **_common("module"),
            "module": self.fullname,
            "origin": str(self.origin),
            "expected_path": str(self.expected),
            "identity_status": "UNKNOWN",
            "loader": "ASIG captured-source loader",
        }
        try:
            if self.origin.suffix != ".py" or not self.origin.is_file():
                record["reason"] = "observed module is not a filesystem-backed Python source file"
                raise ImportError(record["reason"])
            source = _stable_read(self.origin)
            record["loaded_sha256"] = _digest(source)
            expected_source = _stable_read(self.expected)
            record["expected_sha256"] = _digest(expected_source)
            same_path = self.origin.resolve() == self.expected.resolve()
            same_content = record["loaded_sha256"] == record["expected_sha256"]
            record["path_match"] = same_path
            record["content_match"] = same_content
            if same_path and same_content:
                record["identity_status"] = "EXACT_MATCH"
            elif same_content:
                record["identity_status"] = "EQUIVALENT_COPY"
            else:
                record["identity_status"] = "MISMATCH"
            record["bytecode_cache_ignored"] = True
            module.__file__ = str(self.origin)
            module.__cached__ = None
            code = compile(source, str(self.origin), "exec")
            exec(code, module.__dict__)
        except BaseException as exc:
            record.setdefault("reason", f"{type(exc).__name__}: {exc}")
            if record.get("identity_status") == "UNKNOWN":
                record["identity_status"] = "UNKNOWN"
            raise
        finally:
            _append(record)


class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        try:
            expected_map = json.loads(os.environ.get("ASIG_EXPECTED_MODULES", "{}"))
        except json.JSONDecodeError:
            return None
        expected_value = expected_map.get(fullname)
        if not isinstance(expected_value, str):
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or not spec.origin or not isinstance(spec.loader, importlib.machinery.SourceFileLoader):
            _append({
                **_common("module_unobservable"),
                "module": fullname,
                "expected_path": expected_value,
                "identity_status": "UNKNOWN",
                "reason": "module did not resolve through the standard filesystem source loader",
            })
            return None
        origin = Path(spec.origin).resolve()
        expected = Path(expected_value).resolve()
        spec.loader = _CapturedSourceLoader(
            fullname,
            origin,
            expected,
            spec.submodule_search_locations is not None,
        )
        return spec


def install() -> None:
    if os.environ.get("ASIG_RUNTIME_OBSERVER") != "python":
        return
    if getattr(sys, _MARKER, False):
        return
    expected_text = os.environ.get("ASIG_EXPECTED_MODULES", "{}")
    try:
        expected = json.loads(expected_text)
        if not isinstance(expected, dict):
            raise ValueError("ASIG_EXPECTED_MODULES must be a JSON object")
    except (json.JSONDecodeError, ValueError):
        _append({**_common("observer_error"), "reason": "invalid ASIG_EXPECTED_MODULES"})
        return
    finder = _Finder()
    index = next(
        (i for i, item in enumerate(sys.meta_path) if item is importlib.machinery.PathFinder),
        len(sys.meta_path),
    )
    sys.meta_path.insert(index, finder)
    setattr(sys, _MARKER, True)
    _append({**_common("process_start"), "monitored_modules": sorted(expected)})
    atexit.register(lambda: _append(_common("process_end")))


install()
