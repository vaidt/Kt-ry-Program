"""Command-line interface for ASIG."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .inventory import create_manifest, verify_manifest
from .qualification import qualify_evidence


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
