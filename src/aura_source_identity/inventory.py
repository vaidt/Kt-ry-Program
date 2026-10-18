"""Reproducible source inventory and manifest verification."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from .canonical import ASIG_JSON_SORTED_V1, RFC8785_JCS, object_sha256, sha256_hex

SCHEMA_VERSION = 1
MANIFEST_KIND = "AURA_SOURCE_IDENTITY_MANIFEST"
DEFAULT_EXCLUDED_NAMES = frozenset({
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "node_modules", "dist", "build", "htmlcov", "runs",
})


class ManifestError(ValueError):
    """Raised when a source manifest is malformed or unsafe."""


def _git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _working_tree_clean(root: Path) -> bool | None:
    status = _git(root, "status", "--porcelain", "--untracked-files=all")
    if status is None:
        return None
    return status == ""


def _tracked_paths(root: Path) -> list[str] | None:
    """Return Git-index paths when available; ignored local build outputs stay out of the source inventory."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "-z"],
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return [item.decode("utf-8", errors="surrogateescape") for item in proc.stdout.split(b"\0") if item]


def _excluded(relative: str, excluded_names: set[str], excluded_paths: set[str]) -> bool:
    posix = PurePosixPath(relative)
    if any(part in excluded_names for part in posix.parts):
        return True
    return any(relative == item or relative.startswith(item.rstrip("/") + "/") for item in excluded_paths)


def inventory_files(
    root: Path,
    *,
    exclude_names: set[str] | None = None,
    exclude_paths: set[str] | None = None,
) -> list[dict[str, Any]]:
    """List files and symlinks by relative path; never follow symlinks."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ManifestError(f"source root is not a directory: {root}")
    names = set(DEFAULT_EXCLUDED_NAMES)
    if exclude_names:
        names.update(exclude_names)
    paths = {p.strip("/") for p in (exclude_paths or set()) if p.strip("/")}
    entries: list[dict[str, Any]] = []

    tracked = _tracked_paths(root)
    if tracked is None:
        candidates = sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix())
    else:
        candidates = [root / PurePosixPath(relative) for relative in sorted(tracked)]

    for path in candidates:
        relative = path.relative_to(root).as_posix()
        if _excluded(relative, names, paths):
            continue
        if not path.exists() and not path.is_symlink():
            raise ManifestError(f"tracked source path is missing: {relative}")
        if path.is_symlink():
            target = os.readlink(path)
            entries.append({
                "path": relative,
                "kind": "symlink",
                "target": target,
                "sha256": sha256_hex(target.encode("utf-8")),
                "size": len(target.encode("utf-8")),
            })
        elif path.is_file():
            data = path.read_bytes()
            entries.append({
                "path": relative,
                "kind": "file",
                "sha256": sha256_hex(data),
                "size": len(data),
            })
    return entries


def create_manifest(
    root: Path,
    *,
    repository: str | None = None,
    exclude_names: set[str] | None = None,
    exclude_paths: set[str] | None = None,
    canonicalization: str = ASIG_JSON_SORTED_V1,
) -> dict[str, Any]:
    """Capture legacy ASIG or explicitly selected RFC 8785/JCS metadata."""
    if canonicalization not in {ASIG_JSON_SORTED_V1, RFC8785_JCS}:
        raise ManifestError(f"unsupported canonicalization: {canonicalization!r}")
    use_jcs = canonicalization == RFC8785_JCS
    root = root.resolve(strict=True)
    files = inventory_files(root, exclude_names=exclude_names, exclude_paths=exclude_paths)
    commit_sha = _git(root, "rev-parse", "HEAD")
    tree_sha = _git(root, "rev-parse", "HEAD^{tree}")
    clean = _working_tree_clean(root)
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": MANIFEST_KIND,
        "repository": repository,
        "git": {
            "commit_sha": commit_sha,
            "tree_sha": tree_sha,
            "working_tree_clean": clean,
        },
        "inventory": {
            "file_count": len(files),
            "files": files,
            "source_tree_sha256": object_sha256(files, strict_rfc8785=use_jcs),
        },
        "scope": {
            "excluded_names": sorted(set(DEFAULT_EXCLUDED_NAMES) | (exclude_names or set())),
            "excluded_paths": sorted(p.strip("/") for p in (exclude_paths or set()) if p.strip("/")),
            "symlinks": "record link text; do not follow targets",
        },
        "hash_contract": "SHA-256 over ASIG metadata only; not Aura Protocol canonicalization",
    }
    if use_jcs:
        body["canonicalization"] = RFC8785_JCS
    body["manifest_sha256"] = object_sha256(body, strict_rfc8785=use_jcs)
    return body


def _validate_manifest_shape(manifest: Any) -> None:
    if not isinstance(manifest, dict):
        raise ManifestError("manifest must be a JSON object")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ManifestError(f"unsupported schema_version: {manifest.get('schema_version')!r}")
    if manifest.get("kind") != MANIFEST_KIND:
        raise ManifestError("manifest kind is invalid")
    if not isinstance(manifest.get("git"), dict) or not isinstance(manifest.get("inventory"), dict):
        raise ManifestError("manifest is missing git or inventory object")
    canonicalization = manifest.get("canonicalization", ASIG_JSON_SORTED_V1)
    if canonicalization not in {ASIG_JSON_SORTED_V1, RFC8785_JCS}:
        raise ManifestError(f"unsupported canonicalization: {canonicalization!r}")
    files = manifest["inventory"].get("files")
    if not isinstance(files, list):
        raise ManifestError("manifest inventory.files must be an array")
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ManifestError("every inventory item must have a string path")
        path = item["path"]
        if not path or path.startswith("/") or "\\" in path or ".." in PurePosixPath(path).parts:
            raise ManifestError(f"unsafe inventory path: {path!r}")
        if path in seen:
            raise ManifestError(f"duplicate inventory path: {path}")
        seen.add(path)



def _signature_check(
    signature_verifier: Callable[[], Any] | None,
) -> tuple[str, bool | None, str | None, str | None]:
    """Return (status, signature_valid, backend, error), fail-closed on verifier errors."""
    if signature_verifier is None:
        return "missing", None, None, None
    try:
        raw = signature_verifier()
    except Exception as exc:
        return "unverifiable", None, None, f"signature verifier raised: {exc}"[:1000]
    backend = None
    error = None
    if isinstance(raw, bool):
        status = "valid" if raw else "invalid"
    elif isinstance(raw, str):
        status = raw.lower()
    elif isinstance(raw, dict):
        status = str(raw.get("status", "unverifiable")).lower()
        backend_value = raw.get("backend")
        backend = backend_value if isinstance(backend_value, str) else None
        error_value = raw.get("error")
        error = str(error_value)[:1000] if error_value else None
    else:
        return "unverifiable", None, None, "signature verifier returned an unsupported result"
    if status not in {"valid", "missing", "invalid", "unverifiable"}:
        return "unverifiable", None, backend, f"unrecognized signature verifier status: {status!r}"[:1000]
    signature_valid = True if status == "valid" else False if status == "invalid" else None
    return status, signature_valid, backend, error


def _apply_signature_policy(
    result: dict[str, Any],
    *,
    require_signature: bool,
    signature_status: str,
    signature_valid: bool | None,
    signature_backend: str | None,
    signature_error: str | None,
) -> dict[str, Any]:
    source_status = result.get("status", "UNKNOWN")
    result["source_status"] = source_status
    result["signature_policy"] = "required" if require_signature else "optional"
    result["signature_status"] = signature_status
    result["signature_valid"] = signature_valid
    result["signature_backend"] = signature_backend
    if signature_error:
        result["signature_error"] = signature_error
    errors = result.setdefault("errors", [])
    if signature_status == "invalid":
        errors.append("manifest_signature_invalid")
        result["status"] = "MISMATCH"
    elif source_status == "MISMATCH":
        result["status"] = "MISMATCH"
    elif signature_status == "unverifiable":
        errors.append("manifest_signature_unverifiable")
        result["status"] = "UNKNOWN"
    elif require_signature and signature_status == "missing":
        errors.append("manifest_missing_required_signature")
        result["status"] = "UNKNOWN"
    else:
        result["status"] = source_status
    return result


def verify_manifest(
    manifest: Any,
    root: Path,
    *,
    require_signature: bool = False,
    signature_verifier: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    """Verify manifest integrity, current source identity, and optional detached signature.

    Signatures stay in sidecar bundles or GitHub DSSE attestations rather than
    being embedded into the manifest hash input. Legacy manifests without a
    canonicalization field continue to use ASIG_JSON_SORTED_V1.

    Invalid signatures force MISMATCH. Missing signatures under required policy
    and signatures that cannot be verified force UNKNOWN, unless source evidence
    independently requires MISMATCH.
    """
    try:
        _validate_manifest_shape(manifest)
    except ManifestError as exc:
        signature_status = "unverifiable" if signature_verifier is not None else "missing"
        result = {"status": "UNKNOWN", "manifest_integrity": False, "errors": [str(exc)]}
        return _apply_signature_policy(
            result,
            require_signature=require_signature,
            signature_status=signature_status,
            signature_valid=None,
            signature_backend=None,
            signature_error="signature verification skipped because manifest shape is invalid" if signature_verifier else None,
        )

    signature_status, signature_valid, signature_backend, signature_error = _signature_check(signature_verifier)
    canonicalization = manifest.get("canonicalization", ASIG_JSON_SORTED_V1)
    use_jcs = canonicalization == RFC8785_JCS
    body = dict(manifest)
    claimed_hash = body.pop("manifest_sha256", None)
    computed_hash = object_sha256(body, strict_rfc8785=use_jcs)
    integrity_ok = isinstance(claimed_hash, str) and claimed_hash == computed_hash
    errors: list[str] = []
    if not integrity_ok:
        errors.append("manifest_sha256 does not match the manifest content")

    root = root.resolve(strict=True)
    scope = manifest.get("scope") or {}
    excluded_names = set(scope.get("excluded_names", []))
    excluded_paths = set(scope.get("excluded_paths", []))
    try:
        actual_files = inventory_files(root, exclude_names=excluded_names, exclude_paths=excluded_paths)
    except (OSError, ManifestError) as exc:
        result = {
            "status": "UNKNOWN",
            "manifest_integrity": integrity_ok,
            "source_files_match": False,
            "commit_match": False,
            "git_tree_match": False,
            "working_tree_clean": None,
            "source_tree_sha256": None,
            "manifest_sha256": claimed_hash,
            "errors": errors + [str(exc)],
        }
        return _apply_signature_policy(
            result,
            require_signature=require_signature,
            signature_status=signature_status,
            signature_valid=signature_valid,
            signature_backend=signature_backend,
            signature_error=signature_error,
        )

    source_files_ok = actual_files == manifest["inventory"]["files"]
    actual_tree_sha = object_sha256(actual_files, strict_rfc8785=use_jcs)
    expected_tree_sha = manifest["inventory"].get("source_tree_sha256")
    if not source_files_ok:
        errors.append("current source inventory differs from captured inventory")

    current_commit = _git(root, "rev-parse", "HEAD")
    current_tree = _git(root, "rev-parse", "HEAD^{tree}")
    current_clean = _working_tree_clean(root)
    recorded_git = manifest["git"]
    commit_ok = bool(recorded_git.get("commit_sha")) and current_commit == recorded_git.get("commit_sha")
    git_tree_ok = bool(recorded_git.get("tree_sha")) and current_tree == recorded_git.get("tree_sha")
    clean_ok = recorded_git.get("working_tree_clean") is True and current_clean is True

    if recorded_git.get("commit_sha") and not commit_ok:
        errors.append("current Git commit differs from captured commit")
    if recorded_git.get("tree_sha") and not git_tree_ok:
        errors.append("current Git tree differs from captured tree")
    if current_clean is not True:
        errors.append("current working tree is dirty or Git status is unavailable")
    if recorded_git.get("working_tree_clean") is not True:
        errors.append("manifest was not captured from a clean working tree")
    if expected_tree_sha != actual_tree_sha:
        errors.append("source_tree_sha256 does not match the captured file list")

    can_prove_git = all((
        current_commit, current_tree, current_clean is not None,
        recorded_git.get("commit_sha"), recorded_git.get("tree_sha"),
    ))
    if not can_prove_git:
        source_status = "UNKNOWN"
    elif (
        not integrity_ok or not source_files_ok or not commit_ok or not git_tree_ok
        or not clean_ok or expected_tree_sha != actual_tree_sha
    ):
        source_status = "MISMATCH"
    else:
        source_status = "EXACT_MATCH"

    result = {
        "status": source_status,
        "manifest_integrity": integrity_ok,
        "source_files_match": source_files_ok,
        "commit_match": commit_ok,
        "git_tree_match": git_tree_ok,
        "working_tree_clean": current_clean,
        "source_tree_sha256": actual_tree_sha,
        "manifest_sha256": claimed_hash,
        "canonicalization": canonicalization,
        "errors": errors,
    }
    return _apply_signature_policy(
        result,
        require_signature=require_signature,
        signature_status=signature_status,
        signature_valid=signature_valid,
        signature_backend=signature_backend,
        signature_error=signature_error,
    )
