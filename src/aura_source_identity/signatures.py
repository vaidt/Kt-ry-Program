"""Detached Cosign blob and GitHub DSSE artifact-attestation verification."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


_NETWORK_FAILURE_MARKERS = (
    "timeout", "timed out", "context deadline exceeded", "connection refused",
    "connection reset", "network is unreachable", "no route to host",
    "temporary failure", "could not resolve host", "no such host",
    "failed to fetch", "service unavailable", "too many requests",
    "tls handshake timeout", "unexpected eof", "authentication required",
    "requires authentication", "http 401", "http 403", "forbidden",
)


def _result(status: str, backend: str, error: str | None = None) -> dict[str, Any]:
    output: dict[str, Any] = {"status": status, "backend": backend}
    if error:
        output["error"] = error.strip()[:1000]
    return output


def _is_environment_failure(output: str) -> bool:
    lowered = output.lower()
    return any(marker in lowered for marker in _NETWORK_FAILURE_MARKERS)


def verify_cosign_blob(
    manifest_path: Path,
    bundle_path: Path | None,
    *,
    certificate_identity: str | None = None,
    certificate_identity_regexp: str | None = None,
    certificate_oidc_issuer: str | None = None,
    timeout_seconds: float = 60.0,
    binary: str = "cosign",
) -> dict[str, Any]:
    """Verify exact manifest bytes against a Sigstore/Cosign bundle."""
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        return _result("unverifiable", "cosign-blob", "manifest file does not exist")
    if bundle_path is None or not Path(bundle_path).is_file():
        return _result("missing", "cosign-blob", "Cosign signature bundle is missing")
    if not (certificate_identity or certificate_identity_regexp) or not certificate_oidc_issuer:
        return _result(
            "unverifiable", "cosign-blob",
            "keyless verification requires an expected certificate identity and OIDC issuer",
        )
    if shutil.which(binary) is None:
        return _result("unverifiable", "cosign-blob", f"Cosign executable not found: {binary}")

    command = [binary, "verify-blob", str(manifest_path), "--bundle", str(Path(bundle_path))]
    if certificate_identity:
        command.extend(["--certificate-identity", certificate_identity])
    else:
        command.extend(["--certificate-identity-regexp", str(certificate_identity_regexp)])
    command.extend(["--certificate-oidc-issuer", certificate_oidc_issuer])

    try:
        proc = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False, timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return _result("unverifiable", "cosign-blob", "Cosign verification timed out")
    except OSError as exc:
        return _result("unverifiable", "cosign-blob", f"Could not execute Cosign: {exc}")

    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode == 0:
        return _result("valid", "cosign-blob")
    if _is_environment_failure(combined):
        return _result("unverifiable", "cosign-blob", combined)
    return _result("invalid", "cosign-blob", combined or f"Cosign exited with code {proc.returncode}")


def verify_github_attestation(
    manifest_path: Path,
    *,
    repository: str | None,
    signer_workflow: str | None = None,
    timeout_seconds: float = 60.0,
    binary: str = "gh",
) -> dict[str, Any]:
    """Verify a GitHub DSSE/SLSA artifact attestation for a manifest file."""
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        return _result("unverifiable", "github-attestation", "manifest file does not exist")
    if not repository or "/" not in repository:
        return _result(
            "unverifiable", "github-attestation",
            "an expected --attestation-repository in owner/repository form is required",
        )
    if shutil.which(binary) is None:
        return _result("unverifiable", "github-attestation", f"GitHub CLI executable not found: {binary}")

    command = [binary, "attestation", "verify", str(manifest_path), "--repo", repository]
    if signer_workflow:
        command.extend(["--signer-workflow", signer_workflow])
    try:
        proc = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False, timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return _result("unverifiable", "github-attestation", "GitHub attestation verification timed out")
    except OSError as exc:
        return _result("unverifiable", "github-attestation", f"Could not execute GitHub CLI: {exc}")

    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    lowered = combined.lower()
    if proc.returncode == 0:
        return _result("valid", "github-attestation")
    if any(marker in lowered for marker in (
        "no attestations found", "no attestations were found", "could not find attestations",
        "no matching attestations",
    )):
        return _result("missing", "github-attestation", combined)
    if _is_environment_failure(combined):
        return _result("unverifiable", "github-attestation", combined)
    return _result("invalid", "github-attestation", combined or f"GitHub CLI exited with code {proc.returncode}")
