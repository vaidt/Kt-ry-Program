"""Command-line interface for ASIG."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .audit import audit_source_repository
from .inventory import create_manifest, verify_manifest
from .qualification import qualify_evidence
from .runtime.node import run_node
from .runtime.python import run_python
from .runtime.rust import run_rust


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def _emit(value: Any, output: str | None = None) -> None:
    if output:
        _write_json(Path(output), value)
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))


def _ensure_outside_root(root: Path, output: str | None) -> None:
    if output is None:
        return
    resolved_root = root.resolve(strict=True)
    resolved_output = Path(output).expanduser().resolve(strict=False)
    if resolved_output == resolved_root or resolved_root in resolved_output.parents:
        raise ValueError("manifest and report outputs must be outside the repository under measurement")


def _capture(args: argparse.Namespace) -> int:
    try:
        _ensure_outside_root(Path(args.root), args.output)
        manifest = create_manifest(
            Path(args.root),
            repository=args.repository,
            exclude_names=set(args.exclude_name or []),
            exclude_paths=set(args.exclude_path or []),
        )
        _write_json(Path(args.output), manifest)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    clean = manifest["git"]["working_tree_clean"] is True
    result = {
        "status": "CAPTURED" if clean else "CAPTURED_WITH_WARNING",
        "manifest_path": str(Path(args.output)),
        "manifest_sha256": manifest["manifest_sha256"],
        "commit_sha": manifest["git"]["commit_sha"],
        "tree_sha": manifest["git"]["tree_sha"],
        "working_tree_clean": manifest["git"]["working_tree_clean"],
        "file_count": manifest["inventory"]["file_count"],
        "note": "Write the manifest outside the repository under measurement.",
    }
    _emit(result)
    return 0 if clean else 1


def _verify(args: argparse.Namespace) -> int:
    try:
        _ensure_outside_root(Path(args.root), args.output)
        manifest = _read_json(Path(args.manifest))
        result = verify_manifest(manifest, Path(args.root))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result = {"status": "UNKNOWN", "errors": [str(exc)]}
    _emit(result, args.output)
    return 0 if result.get("status") == "EXACT_MATCH" else 1


def _qualify(args: argparse.Namespace) -> int:
    try:
        _ensure_outside_root(Path(args.root), args.output)
        manifest = _read_json(Path(args.manifest))
        evidence = _read_json(Path(args.evidence))
        source_verification = verify_manifest(manifest, Path(args.root))
        result = qualify_evidence(evidence, source_verification)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result = {
            "schema_version": 1,
            "status": "BLOCKED",
            "failures": [],
            "blockers": [str(exc)],
            "qualification_sha256": None,
        }
    _emit(result, args.output)
    return 0 if result.get("status") == "PASS" else 1



def _parse_mapping(values: list[str], label: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for value in values or []:
        key, separator, path = value.partition("=")
        if not separator or not key or not path:
            raise ValueError(f"{label} entries must have the form NAME=RELATIVE_PATH")
        if key in mapping:
            raise ValueError(f"duplicate {label} key: {key}")
        mapping[key] = path
    return mapping


def _remaining_command(values: list[str]) -> list[str]:
    command = list(values or [])
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("provide a command after --")
    return command


def _audit(args: argparse.Namespace) -> int:
    try:
        root = Path(args.root)
        _ensure_outside_root(root, args.output)
        _ensure_outside_root(root, args.manifest_output)
        receipt = audit_source_repository(
            root,
            repository=args.repository,
            source_ref=args.source_ref,
            manifest_output=Path(args.manifest_output),
            receipt_output=Path(args.output),
            exclude_names=set(args.exclude_name or []),
            exclude_paths=set(args.exclude_path or []),
        )
    except (OSError, ValueError) as exc:
        error = {"kind": "ASIG_READ_ONLY_SOURCE_AUDIT_RECEIPT", "audit_status": "BLOCKED", "error": str(exc)}
        _emit(error)
        return 2
    _emit(receipt)
    return 0 if receipt.get("audit_status") == "PASS" else 1


def _runtime_python(args: argparse.Namespace) -> int:
    try:
        command = _remaining_command(args.command_argv)
        receipt = run_python(
            Path(args.root), command, _parse_mapping(args.module, "module"),
            required_test_ids=args.required_test_id,
            timeout_seconds=args.timeout,
            output_path=Path(args.output),
        )
    except (OSError, ValueError) as exc:
        _emit({"qualification_status": "BLOCKED", "error": str(exc)})
        return 2
    _emit(receipt)
    return 0 if receipt.get("qualification_status") == "PASS" else 1


def _runtime_node(args: argparse.Namespace) -> int:
    try:
        command = _remaining_command(args.command_argv)
        receipt = run_node(
            Path(args.root), command, _parse_mapping(args.specifier, "specifier"),
            timeout_seconds=args.timeout,
            output_path=Path(args.output),
        )
    except (OSError, ValueError) as exc:
        _emit({"qualification_status": "BLOCKED", "error": str(exc)})
        return 2
    _emit(receipt)
    return 0 if receipt.get("qualification_status") == "PASS" else 1


def _runtime_rust(args: argparse.Namespace) -> int:
    try:
        command = _remaining_command(args.command_argv)
        receipt = run_rust(
            Path(args.root), command,
            required_test_ids=args.required_test_id,
            timeout_seconds=args.timeout,
            output_path=Path(args.output),
        )
    except (OSError, ValueError) as exc:
        _emit({"qualification_status": "BLOCKED", "error": str(exc)})
        return 2
    _emit(receipt)
    return 0 if receipt.get("qualification_status") == "PASS" else 1

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aura-source-identity",
        description="Capture and verify source identity evidence for AURA engineering workflows.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture", help="create a source inventory manifest")
    capture.add_argument("--root", default=".", help="repository root to inventory")
    capture.add_argument("--repository", default=None, help="repository identifier, e.g. vaidt/Kt-ry-Program")
    capture.add_argument("--output", required=True, help="manifest path; place it outside the measured repository")
    capture.add_argument("--exclude-name", action="append", default=[], help="extra excluded path component (repeatable)")
    capture.add_argument("--exclude-path", action="append", default=[], help="extra excluded relative path (repeatable)")
    capture.set_defaults(func=_capture)

    verify = sub.add_parser("verify", help="verify manifest integrity and current checkout identity")
    verify.add_argument("--root", default=".", help="repository root to verify")
    verify.add_argument("--manifest", required=True, help="captured manifest JSON")
    verify.add_argument("--output", default=None, help="optional JSON report path")
    verify.set_defaults(func=_verify)

    qualify = sub.add_parser("qualify", help="qualify test evidence against a verified source manifest")
    qualify.add_argument("--root", default=".", help="repository root under evaluation")
    qualify.add_argument("--manifest", required=True, help="captured source manifest JSON")
    qualify.add_argument("--evidence", required=True, help="execution and independent-evaluation evidence JSON")
    qualify.add_argument("--output", default=None, help="optional JSON report path")
    qualify.set_defaults(func=_qualify)

    audit = sub.add_parser("audit", help="capture and verify a read-only source snapshot")
    audit.add_argument("--root", default=".", help="target repository root")
    audit.add_argument("--repository", required=True, help="target repository name, e.g. vaidt/Aura-Guard")
    audit.add_argument("--source-ref", default="refs/heads/main", help="ref requested for the checkout")
    audit.add_argument("--manifest-output", required=True, help="manifest path outside target repository")
    audit.add_argument("--output", required=True, help="receipt path outside target repository")
    audit.add_argument("--exclude-name", action="append", default=[], help="extra excluded path component")
    audit.add_argument("--exclude-path", action="append", default=[], help="extra excluded relative path")
    audit.set_defaults(func=_audit)

    py_run = sub.add_parser("runtime-python", help="observe configured Python imports and pytest node IDs")
    py_run.add_argument("--root", default=".", help="target repository root")
    py_run.add_argument("--module", action="append", default=[], metavar="NAME=RELATIVE_PATH", help="module identity mapping; repeatable")
    py_run.add_argument("--required-test-id", action="append", default=[], help="required pytest node ID; repeatable")
    py_run.add_argument("--timeout", type=float, default=120.0)
    py_run.add_argument("--output", required=True, help="receipt path outside target repository")
    py_run.add_argument("command_argv", nargs=argparse.REMAINDER, help="command to execute after --")
    py_run.set_defaults(func=_runtime_python)

    node_run = sub.add_parser("runtime-node", help="observe explicitly mapped CommonJS/ESM imports")
    node_run.add_argument("--root", default=".", help="target repository root")
    node_run.add_argument("--specifier", action="append", default=[], metavar="SPECIFIER=RELATIVE_PATH", help="module specifier mapping; repeatable")
    node_run.add_argument("--timeout", type=float, default=120.0)
    node_run.add_argument("--output", required=True, help="receipt path outside target repository")
    node_run.add_argument("command_argv", nargs=argparse.REMAINDER, help="command to execute after --")
    node_run.set_defaults(func=_runtime_node)

    rust_run = sub.add_parser("runtime-rust", help="run a Cargo command and capture build context (not loaded-source identity)")
    rust_run.add_argument("--root", default=".", help="target repository root")
    rust_run.add_argument("--required-test-id", action="append", default=[], help="expected Rust test name; repeatable")
    rust_run.add_argument("--timeout", type=float, default=600.0)
    rust_run.add_argument("--output", required=True, help="receipt path outside target repository")
    rust_run.add_argument("command_argv", nargs=argparse.REMAINDER, help="command to execute after --")
    rust_run.set_defaults(func=_runtime_rust)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
