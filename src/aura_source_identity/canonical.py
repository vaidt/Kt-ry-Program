"""Private deterministic encoding for ASIG's own manifests.

The default encoder is the historical ASIG JSON encoding for compatibility.
RFC 8785/JCS is opt-in and strict: if the optional implementation is not
installed, callers receive an error instead of environment-dependent hashes.

This is NOT Aura Protocol canonical serialization and MUST NOT be used to
compute protocol hashes or replace APS-200's canonical byte contract.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

ASIG_JSON_SORTED_V1 = "ASIG_JSON_SORTED_V1"
RFC8785_JCS = "RFC8785_JCS"


def canonical_json_bytes(value: Any, *, strict_rfc8785: bool = False) -> bytes:
    """Encode JSON-compatible data deterministically for ASIG metadata.

    The default path preserves historical ASIG bytes. Use strict_rfc8785=True
    only when the caller records RFC8785_JCS in the manifest contract.
    This mode never silently falls back to another encoder.
    """
    if strict_rfc8785:
        try:
            import rfc8785
        except ImportError as exc:
            raise ValueError(
                "RFC 8785/JCS was requested but the optional 'rfc8785' package "
                "is not installed; install with: pip install '.[canonical]'"
            ) from exc
        rendered = rfc8785.dumps(value)
        if isinstance(rendered, bytes):
            return rendered
        if isinstance(rendered, str):
            return rendered.encode("utf-8")
        raise TypeError("RFC 8785 encoder returned an unsupported value")

    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return text.encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def object_sha256(value: Any, *, strict_rfc8785: bool = False) -> str:
    return sha256_hex(canonical_json_bytes(value, strict_rfc8785=strict_rfc8785))
