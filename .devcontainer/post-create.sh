#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check --upgrade pip
.venv/bin/python -m pip install --disable-pip-version-check build
.venv/bin/python -m pip install --disable-pip-version-check -e .

echo
echo "ASIG workspace provisioned."
echo "Run 'make doctor' to inspect tool versions."
echo "Run 'make ci-local' to execute local contract/unit/build checks."
