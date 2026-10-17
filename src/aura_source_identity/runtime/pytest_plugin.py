"""Explicit pytest plug-in for ASIG test-scope evidence."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    destination = os.environ.get("ASIG_TEST_REPORT")
    if not destination:
        return
    row = {
        "schema_version": 1,
        "event": "test_result",
        "run_id": os.environ.get("ASIG_RUN_ID"),
        "nodeid": item.nodeid,
        "source_path": str(Path(str(item.path)).resolve()),
        "phase": report.when,
        "outcome": report.outcome.upper(),
        "duration_seconds": float(report.duration),
        "observed_at_monotonic_ns": time.monotonic_ns(),
    }
    try:
        with open(destination, "a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    except OSError:
        return
