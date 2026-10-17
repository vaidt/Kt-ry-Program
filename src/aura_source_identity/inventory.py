"""Reproducible source inventory and manifest verification."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

from .canonical import object_sha256, sha256_hex

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
    return [item.decode("utf-8", errors="surrogateescape") for item in proc.stdout.split(b"\\0") if item]


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
) -> dict[str, Any]:
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
            "source_tree_sha256": object_sha256(files),
        },
        "scope": {
            "excluded_names": sorted(set(DEFAULT_EXCLUDED_NAMES) | (exclude_names or set())),
            "excluded_paths": sorted(p.strip("/") for p in (exclude_paths or set()) if p.strip("/")),
            "symlinks": "record link text; do not follow targets",
        },
        "hash_contract": "SHA-256 over ASIG metadata only; not Aura Protocol canonicalization",
    }
    body["manifest_sha256"] = object_sha256(body)
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


def verify_manifest(manifest: Any, root: Path) -> dict[str, Any]:
    """Validate manifest integrity and compare it to the current checkout."""
    try:
        _validate_manifest_shape(manifest)
    except ManifestError as exc:
        return {"status": "UNKNOWN", "manifest_integrity": False, "errors": [str(exc)]}

    body = dict(manifest)
    claimed_hash = body.pop("manifest_sha256", None)
    computed_hash = object_sha256(body)
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
        return {"status": "UNKNOWN", "manifest_integrity": integrity_ok, "errors": errors + [str(exc)]}

    source_files_ok = actual_files == manifest["inventory"]["files"]
    actual_tree_sha = object_sha256(actual_files)
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

    can_prove_git = all((current_commit, current_tree, current_clean is not None,
                         recorded_git.get("commit_sha"), recorded_git.get("tree_sha")))
    if not can_prove_git:
        status = "UNKNOWN"
    elif not integrity_ok or not source_files_ok or not commit_ok or not git_tree_ok or not clean_ok or expected_tree_sha != actual_tree_sha:
        status = "MISMATCH"
    else:
        status = "EXACT_MATCH"

    return {
        "status": status,
        "manifest_integrity": integrity_ok,
        "source_files_match": source_files_ok,
        "commit_match": commit_ok,
        "git_tree_match": git_tree_ok,
        "working_tree_clean": current_clean,
        "source_tree_sha256": actual_tree_sha,
        "manifest_sha256": claimed_hash,
        "errors": errors,
    }
