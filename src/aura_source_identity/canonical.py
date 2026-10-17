"""Private deterministic encoding for ASIG's own manifests.

This is NOT Aura Protocol canonical serialization and MUST NOT be used to
compute protocol hashes or replace APS-200's canonical byte contract.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    """Encode JSON-compatible data deterministically for ASIG metadata."""
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


def object_sha256(value: Any) -> str:
    return sha256_hex(canonical_json_bytes(value))
