#!/usr/bin/env python3
"""Fail-closed evaluator for the validation-only ASIG Python license policy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Match GPL/AGPL identifiers, but not LGPL identifiers.
BANNED_ID_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:AGPL|GPL)-(?:2|3)\.0"
    r"(?:-(?:only|or-later)|\+)?(?![A-Za-z0-9])",
    re.IGNORECASE,
)
BANNED_TEXT_PATTERNS = [
    re.compile(r"\bGNU General Public License\s+(?:version\s+)?v?(?:2|3)(?:\.0)?(?:\+| or later)?\b", re.IGNORECASE),
    re.compile(r"\bGNU Affero General Public License\s+(?:version\s+)?v?3(?:\.0)?(?:\+| or later)?\b", re.IGNORECASE),
    re.compile(r"(?<![A-Za-z])(?:AGPL|GPL)\s*v?(?:2|3)(?:\.0)?(?:\+| or later)?\b", re.IGNORECASE),
]
REVIEW_ID_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:LGPL-(?:2\.0|2\.1|3\.0)(?:-(?:only|or-later))?|MPL-2\.0)(?![A-Za-z0-9])",
    re.IGNORECASE,
)
SPDX_EXPRESSION_SHAPE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9.+:-]*"
    r"(?:\s+(?:AND|OR|WITH)\s+[A-Za-z0-9][A-Za-z0-9.+:-]*)*$",
    re.IGNORECASE,
)
UNKNOWN_VALUES = {"", "UNKNOWN", "NOASSERTION", "NONE", "NOT SPECIFIED", "N/A", "NA"}


def normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def load_policy(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        policy = json.load(stream)
    required = {
        "policy_id",
        "status",
        "banned_spdx_license_ids",
        "banned_human_readable_aliases",
        "review_required_spdx_license_ids",
        "review_required_human_readable_fragments",
        "recognized_human_readable_license_labels",
    }
    missing = sorted(required.difference(policy))
    if missing:
        raise ValueError(f"policy missing required keys: {', '.join(missing)}")
    if policy["status"] != "VALIDATION_ONLY":
        raise ValueError("policy status must remain VALIDATION_ONLY")
    return policy


def license_tokens(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        values = [str(value).strip() for value in raw]
    elif isinstance(raw, str):
        values = [part.strip() for part in raw.split(";")]
    else:
        values = [str(raw).strip()]
    return [value for value in values if value]


def classify_token(token: str, policy: dict[str, Any]) -> tuple[str, str | None]:
    token_norm = normalized(token)
    if token_norm in {normalized(v) for v in policy["review_required_spdx_license_ids"]}:
        return "REVIEW_REQUIRED", "license is explicitly reserved for manual review"
    if token_norm in UNKNOWN_VALUES:
        return "REVIEW_REQUIRED", "license metadata is missing or unresolved"

    for fragment in policy["review_required_human_readable_fragments"]:
        if normalized(fragment) in token_norm:
            return "REVIEW_REQUIRED", "license label is ambiguous or requires manual review"
    if REVIEW_ID_PATTERN.search(token):
        return "REVIEW_REQUIRED", "LGPL/MPL-family license requires manual review"
    if "lesser general public license" in token_norm or "mozilla public license" in token_norm:
        return "REVIEW_REQUIRED", "LGPL/MPL-family license requires manual review"

    banned_aliases = {normalized(v) for v in policy["banned_human_readable_aliases"]}
    banned_ids = {normalized(v) for v in policy["banned_spdx_license_ids"]}
    if token_norm in banned_aliases or token_norm in banned_ids:
        return "BANNED", "license is listed in the validation-only blocked policy"
    if BANNED_ID_PATTERN.search(token) or any(p.search(token) for p in BANNED_TEXT_PATTERNS):
        return "BANNED", "GPL-2.0/GPL-3.0/AGPL-3.0 family match"

    known_labels = {normalized(v) for v in policy["recognized_human_readable_license_labels"]}
    if token_norm in known_labels or SPDX_EXPRESSION_SHAPE.fullmatch(token):
        return "RECOGNIZED", None

    return "REVIEW_REQUIRED", "license label is not recognized by this test policy"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    try:
        policy = load_policy(args.policy)
        with args.report.open(encoding="utf-8") as stream:
            report = json.load(stream)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"LICENSE_POLICY_ERROR: cannot load policy/report: {exc}", file=sys.stderr)
        return 2

    if not isinstance(report, list) or not report:
        print("LICENSE_POLICY_ERROR: license inventory is empty or has an invalid shape", file=sys.stderr)
        return 2

    blocked: list[str] = []
    seen = 0
    for package in report:
        if not isinstance(package, dict):
            blocked.append("LICENSE_POLICY_REVIEW_REQUIRED: malformed package row")
            continue
        name = str(package.get("Name") or package.get("name") or "<unknown-package>")
        version = str(package.get("Version") or package.get("version") or "<unknown-version>")
        raw_license = package.get("License", package.get("license"))
        tokens = license_tokens(raw_license)
        if not tokens:
            blocked.append(
                f"LICENSE_POLICY_REVIEW_REQUIRED: {name} {version}: missing license metadata"
            )
            continue
        for token in tokens:
            seen += 1
            outcome, reason = classify_token(token, policy)
            if outcome == "BANNED":
                blocked.append(
                    f"LICENSE_POLICY_BANNED: {name} {version}: {token!r} — {reason}"
                )
            elif outcome == "REVIEW_REQUIRED":
                blocked.append(
                    f"LICENSE_POLICY_REVIEW_REQUIRED: {name} {version}: {token!r} — {reason}"
                )

    if blocked:
        for finding in blocked:
            print(finding, file=sys.stderr)
        print(
            f"LICENSE_POLICY_FAIL: {len(blocked)} blocking finding(s); "
            f"policy={policy['policy_id']} status={policy['status']}",
            file=sys.stderr,
        )
        return 1

    print(
        f"LICENSE_POLICY_PASS: {len(report)} package(s), {seen} license token(s); "
        f"policy={policy['policy_id']} status={policy['status']}"
    )
    print("Non-SPDX labels not explicitly recognized are fail-closed for manual review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
