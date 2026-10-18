#!/usr/bin/env python3
"""Validate ASIG project delegation records with standard-library checks.

This is a project-specific invariant checker, not a general JSON Schema engine.
The JSON Schema remains the portable contract for independent validators.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "schema_version", "delegation_id", "title", "status", "request", "scope",
    "execution", "authority", "verification", "evidence", "rollback",
}
STATUSES = {
    "PROPOSED", "BLOCKED", "AUTHORIZED_FOR_R&D", "IN_PROGRESS",
    "VERIFICATION_PENDING", "VERIFIED", "REJECTED", "CLOSED",
}
AUTHORIZED_STATUSES = {
    "AUTHORIZED_FOR_R&D", "IN_PROGRESS", "VERIFICATION_PENDING", "VERIFIED",
}
SAFE_CHANGE_CLASSES = {"DOCS_ONLY", "CI_SECURITY_CONTROL", "NON_AUTHORITATIVE_RND"}
ALL_CHANGE_CLASSES = SAFE_CHANGE_CLASSES | {"PROTOCOL_NORMATIVE", "RUNTIME_TARGET", "RELEASE_PRODUCTION"}
NETWORK_EFFECTS = {"NONE", "READ_ONLY_ONLY", "REQUIRES_SEPARATE_REVIEW"}
TEST_RESULTS = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}
ID_PATTERN = re.compile(r"ASIG-DEL-[0-9]{4,}")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not any(
        marker in value for marker in ("REPLACE_ME", "TODO", "<fill", "<replace")
    )


def parse_time(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be an ISO-8601 timestamp with a timezone")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field} is not a valid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{field} must include a timezone offset")
        return None
    return parsed.astimezone(timezone.utc)


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0 and all(nonempty(item) for item in value)


def validate_schema_definition(schema_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"schema cannot be parsed: {exc}"]
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("schema must declare JSON Schema draft 2020-12")
    if schema.get("type") != "object":
        errors.append("schema root type must be object")
    schema_required = set(schema.get("required", []))
    if schema_required != REQUIRED_TOP_LEVEL:
        errors.append("schema top-level required fields drifted from executable validator")
    schema_properties = schema.get("properties", {})
    if not REQUIRED_TOP_LEVEL.issubset(set(schema_properties)):
        errors.append("schema properties omit one or more required top-level fields")
    if schema.get("additionalProperties") is not False:
        errors.append("schema root must set additionalProperties=false")
    return errors


def validate_record(record: Any, label: str = "<record>") -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{label}: record root must be an object"]

    missing = sorted(REQUIRED_TOP_LEVEL - set(record))
    if missing:
        errors.append(f"{label}: missing top-level fields: {', '.join(missing)}")
        return errors
    extra = sorted(set(record) - REQUIRED_TOP_LEVEL)
    if extra:
        errors.append(f"{label}: unexpected top-level fields: {', '.join(extra)}")

    if record.get("schema_version") != "1.0":
        errors.append(f"{label}: schema_version must equal '1.0'")
    delegation_id = record.get("delegation_id")
    if not isinstance(delegation_id, str) or not ID_PATTERN.fullmatch(delegation_id):
        errors.append(f"{label}: delegation_id must match ASIG-DEL-NNNN")
    if not nonempty(record.get("title")):
        errors.append(f"{label}: title must be a non-placeholder string of at least 8 characters")
    if isinstance(record.get("title"), str) and len(record["title"]) < 8:
        errors.append(f"{label}: title must contain at least 8 characters")
    status = record.get("status")
    if status not in STATUSES:
        errors.append(f"{label}: status is not in the contract status set")

    request = record.get("request")
    if not isinstance(request, dict):
        errors.append(f"{label}: request must be an object")
        request = {}
    for key in ("objective", "requester"):
        if not nonempty(request.get(key)):
            errors.append(f"{label}: request.{key} must be a non-placeholder string")
    created = parse_time(request.get("created_at"), f"{label}: request.created_at", errors)

    scope = record.get("scope")
    if not isinstance(scope, dict):
        errors.append(f"{label}: scope must be an object")
        scope = {}
    for key in ("in_scope", "out_of_scope", "paths_allowed", "paths_forbidden"):
        if not nonempty_list(scope.get(key)):
            errors.append(f"{label}: scope.{key} must be a non-empty array of non-placeholder strings")
    repositories = scope.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        errors.append(f"{label}: scope.repositories must be a non-empty array")
    else:
        for index, item in enumerate(repositories):
            if not isinstance(item, dict):
                errors.append(f"{label}: scope.repositories[{index}] must be an object")
                continue
            full_name = item.get("repository_full_name")
            if not isinstance(full_name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", full_name):
                errors.append(f"{label}: scope.repositories[{index}].repository_full_name must be owner/repo")
            if not nonempty(item.get("ref")):
                errors.append(f"{label}: scope.repositories[{index}].ref must be non-empty")

    execution = record.get("execution")
    if not isinstance(execution, dict):
        errors.append(f"{label}: execution must be an object")
        execution = {}
    authorized = execution.get("implementation_authorized")
    if not isinstance(authorized, bool):
        errors.append(f"{label}: execution.implementation_authorized must be boolean")
    for key in ("source_branch", "target_branch"):
        if not nonempty(execution.get(key)):
            errors.append(f"{label}: execution.{key} must be non-empty")
    if execution.get("source_branch") in {"main", "refs/heads/main"}:
        errors.append(f"{label}: source_branch cannot be main")
    change_class = execution.get("change_class")
    if change_class not in ALL_CHANGE_CLASSES:
        errors.append(f"{label}: execution.change_class is not recognized")
    if execution.get("pull_request_required") is not True:
        errors.append(f"{label}: pull_request_required must remain true")
    if execution.get("direct_push_permitted") is not False:
        errors.append(f"{label}: direct_push_permitted must remain false")
    if execution.get("network_side_effects") not in NETWORK_EFFECTS:
        errors.append(f"{label}: execution.network_side_effects is not recognized")

    authority = record.get("authority")
    if not isinstance(authority, dict):
        errors.append(f"{label}: authority must be an object")
        authority = {}
    decision_status = authority.get("decision_status")
    if decision_status not in {"NOT_PROVEN", "PROVEN"}:
        errors.append(f"{label}: authority.decision_status must be NOT_PROVEN or PROVEN")
    if authority.get("normative_effect") != "NONE":
        errors.append(f"{label}: authority.normative_effect must be NONE")
    evidence_refs = authority.get("evidence_refs")
    if not isinstance(evidence_refs, list) or any(not isinstance(x, str) for x in evidence_refs):
        errors.append(f"{label}: authority.evidence_refs must be an array of strings")
        evidence_refs = []
    authority_scope = authority.get("scope")
    if not isinstance(authority_scope, list) or any(not isinstance(x, str) for x in authority_scope):
        errors.append(f"{label}: authority.scope must be an array of strings")
        authority_scope = []
    effective = expiry = None
    if decision_status == "PROVEN":
        for key in ("issuer", "current_holder", "decision_ref"):
            if not nonempty(authority.get(key)):
                errors.append(f"{label}: authority.{key} is required when authority is PROVEN")
        if not nonempty_list(authority_scope):
            errors.append(f"{label}: authority.scope must be non-empty when authority is PROVEN")
        if not nonempty_list(evidence_refs):
            errors.append(f"{label}: authority.evidence_refs must be non-empty when authority is PROVEN")
        effective = parse_time(authority.get("effective_from"), f"{label}: authority.effective_from", errors)
        expiry = parse_time(authority.get("valid_until"), f"{label}: authority.valid_until", errors)
        now = datetime.now(timezone.utc)
        if effective and effective > now:
            errors.append(f"{label}: authority is not effective yet")
        if expiry and expiry <= now:
            errors.append(f"{label}: authority evidence has expired")
        if effective and expiry and expiry <= effective:
            errors.append(f"{label}: authority.valid_until must be later than effective_from")

    verification = record.get("verification")
    if not isinstance(verification, dict):
        errors.append(f"{label}: verification must be an object")
        verification = {}
    required_tests = verification.get("required_tests")
    if not nonempty_list(required_tests):
        errors.append(f"{label}: verification.required_tests must be a non-empty array")
        required_tests = []
    if len(required_tests) != len(set(required_tests)) if isinstance(required_tests, list) and all(isinstance(x, str) for x in required_tests) else False:
        errors.append(f"{label}: verification.required_tests must not contain duplicates")
    if not nonempty(verification.get("reviewer_role")):
        errors.append(f"{label}: verification.reviewer_role must be non-empty")
    independence = verification.get("independence_status")
    if independence not in {"PROVEN", "NOT_PROVEN", "NOT_APPLICABLE"}:
        errors.append(f"{label}: verification.independence_status is not recognized")
    verification_refs = verification.get("evidence_refs")
    if not isinstance(verification_refs, list) or any(not isinstance(x, str) for x in verification_refs):
        errors.append(f"{label}: verification.evidence_refs must be an array of strings")
        verification_refs = []
    results = verification.get("results")
    if not isinstance(results, list):
        errors.append(f"{label}: verification.results must be an array")
        results = []
    result_by_id: dict[str, dict[str, Any]] = {}
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            errors.append(f"{label}: verification.results[{index}] must be an object")
            continue
        test_id = result.get("test_id")
        if not nonempty(test_id):
            errors.append(f"{label}: verification.results[{index}].test_id must be non-empty")
            continue
        if test_id in result_by_id:
            errors.append(f"{label}: duplicate verification result for {test_id}")
        result_by_id[test_id] = result
        if result.get("status") not in TEST_RESULTS:
            errors.append(f"{label}: verification result {test_id} has an invalid status")
        if not isinstance(result.get("evidence_ref"), str):
            errors.append(f"{label}: verification result {test_id} needs an evidence_ref string")

    evidence = record.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(f"{label}: evidence must be an object")
        evidence = {}
    for key in ("evidence_refs", "artifact_names"):
        value = evidence.get(key)
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            errors.append(f"{label}: evidence.{key} must be an array of strings")

    rollback = record.get("rollback")
    if not isinstance(rollback, dict):
        errors.append(f"{label}: rollback must be an object")
        rollback = {}
    if not nonempty(rollback.get("plan")) or len(str(rollback.get("plan", ""))) < 10:
        errors.append(f"{label}: rollback.plan must describe a concrete action")
    if not nonempty_list(rollback.get("trigger_conditions")):
        errors.append(f"{label}: rollback.trigger_conditions must be a non-empty array")

    if authorized is True:
        if status not in AUTHORIZED_STATUSES:
            errors.append(f"{label}: authorized implementation requires an active authorized lifecycle status")
        if decision_status != "PROVEN":
            errors.append(f"{label}: implementation cannot be authorized while authority is NOT_PROVEN")
        if change_class not in SAFE_CHANGE_CLASSES:
            errors.append(f"{label}: this ASIG R&D gate cannot authorize protocol, target-runtime, release, or production work")
        if execution.get("network_side_effects") == "REQUIRES_SEPARATE_REVIEW":
            errors.append(f"{label}: separately reviewed network side effects cannot be authorized by this record alone")
    elif status in AUTHORIZED_STATUSES:
        errors.append(f"{label}: authorized lifecycle status requires implementation_authorized=true")

    if status == "VERIFIED":
        required_set = set(required_tests) if isinstance(required_tests, list) and all(isinstance(x, str) for x in required_tests) else set()
        passing_set = {
            test_id for test_id, result in result_by_id.items()
            if result.get("status") == "PASS" and nonempty(result.get("evidence_ref"))
        }
        if not required_set or not required_set.issubset(passing_set):
            errors.append(f"{label}: VERIFIED requires a PASS evidence result for every required test")
        if independence != "PROVEN":
            errors.append(f"{label}: VERIFIED requires proven reviewer independence")
        if not nonempty_list(verification_refs):
            errors.append(f"{label}: VERIFIED requires verification evidence references")
        if not nonempty_list(evidence.get("evidence_refs")):
            errors.append(f"{label}: VERIFIED requires general evidence references")
        if authorized is not True or decision_status != "PROVEN":
            errors.append(f"{label}: VERIFIED cannot be claimed without authorized execution and proven authority")

    if status == "AUTHORIZED_FOR_R&D" and change_class not in SAFE_CHANGE_CLASSES:
        errors.append(f"{label}: R&D authorization is limited to documentation, CI/security, and non-authoritative R&D")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-dir", default="governance/delegations/records")
    parser.add_argument("--schema", default="schemas/project-delegation.schema.json")
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    records_dir = Path(args.records_dir)
    schema_path = Path(args.schema)
    all_errors = validate_schema_definition(schema_path)
    results: list[dict[str, Any]] = []

    if records_dir.exists():
        paths = sorted(records_dir.glob("*.json"))
    else:
        paths = []
    seen_ids: set[str] = set()
    for path in paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            message = f"{path}: cannot parse JSON: {exc}"
            all_errors.append(message)
            results.append({"file": str(path), "validation": "FAIL", "errors": [message]})
            continue
        record_errors = validate_record(record, str(path))
        record_id = record.get("delegation_id") if isinstance(record, dict) else None
        if isinstance(record_id, str):
            if record_id in seen_ids:
                record_errors.append(f"{path}: duplicate delegation_id {record_id}")
            seen_ids.add(record_id)
            expected_name = f"{record_id}.json"
            if path.name != expected_name:
                record_errors.append(f"{path}: filename must be {expected_name}")
        all_errors.extend(record_errors)
        results.append({
            "file": str(path),
            "delegation_id": record_id,
            "status": record.get("status") if isinstance(record, dict) else None,
            "implementation_authorized": (
                record.get("execution", {}).get("implementation_authorized")
                if isinstance(record, dict) and isinstance(record.get("execution"), dict) else None
            ),
            "validation": "FAIL" if record_errors else "PASS",
            "errors": record_errors,
        })

    outcome = "FAIL" if all_errors else ("NO_RECORDS" if not paths else "PASS")
    report = {
        "report_version": "1.0",
        "outcome": outcome,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "ref": os.environ.get("GITHUB_REF", "unknown"),
        "event_name": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "record_count": len(paths),
        "authorization_granted_by_validator": False,
        "records": results,
        "errors": all_errors,
        "note": "Structural/invariant validation only. This report never grants authority or protocol status."
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
