"""Qualification policy for execution and regression evidence."""
from __future__ import annotations

from typing import Any

from .canonical import object_sha256


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def qualify_evidence(evidence: Any, manifest_verification: dict[str, Any]) -> dict[str, Any]:
    """Evaluate evidence without converting unknown or incomplete proof to PASS."""
    failures: list[str] = []
    blockers: list[str] = []

    if not isinstance(evidence, dict):
        return {
            "status": "BLOCKED",
            "failures": [],
            "blockers": ["evidence must be a JSON object"],
            "qualification_sha256": None,
        }
    if evidence.get("schema_version") != 1:
        blockers.append("unsupported or missing evidence schema_version")

    manifest_hash = manifest_verification.get("manifest_sha256")
    expected_manifest_hash = evidence.get("expected_manifest_sha256")
    manifest_status = manifest_verification.get("status")
    if not _is_sha256(expected_manifest_hash):
        blockers.append("expected_manifest_sha256 must be a lowercase SHA-256 digest")
    elif not _is_sha256(manifest_hash):
        blockers.append("verified manifest digest is unavailable")
    elif expected_manifest_hash != manifest_hash:
        failures.append("evidence points to a different source manifest")
    if manifest_status == "MISMATCH":
        failures.append("source identity verification found a mismatch")
    elif manifest_status != "EXACT_MATCH":
        blockers.append("source identity is not established")

    test_plan = evidence.get("test_plan")
    if not isinstance(test_plan, dict):
        blockers.append("test_plan is missing")
        test_plan = {}
    required = test_plan.get("required_test_ids")
    executed = test_plan.get("executed_test_ids")
    if not isinstance(required, list) or not required or any(not isinstance(x, str) or not x for x in required):
        blockers.append("required_test_ids must be a non-empty list of IDs")
        required = []
    if len(set(required)) != len(required):
        failures.append("required_test_ids contains duplicates")
    if not isinstance(executed, list) or any(not isinstance(x, str) or not x for x in executed):
        blockers.append("executed_test_ids must be a list of IDs")
        executed = []
    if len(set(executed)) != len(executed):
        failures.append("executed_test_ids contains duplicates")
    if set(executed) != set(required) or len(executed) != len(required):
        blockers.append("executed test IDs do not exactly match the required test set")
    if test_plan.get("complete") is not True:
        blockers.append("test suite is not explicitly marked complete")

    expected_tests_hash = test_plan.get("expected_test_source_sha256")
    observed_tests_hash = test_plan.get("observed_test_source_sha256")
    if not _is_sha256(expected_tests_hash) or not _is_sha256(observed_tests_hash):
        blockers.append("expected/observed test source hashes must be lowercase SHA-256 digests")
    elif expected_tests_hash != observed_tests_hash:
        failures.append("test source changed between planned and observed execution")

    test_results = evidence.get("test_results")
    if not isinstance(test_results, list):
        blockers.append("test_results must be an array")
        test_results = []
    result_by_id: dict[str, str] = {}
    for row in test_results:
        if not isinstance(row, dict) or not isinstance(row.get("test_id"), str):
            blockers.append("every test result must include test_id")
            continue
        test_id = row["test_id"]
        if test_id in result_by_id:
            failures.append(f"duplicate test result for {test_id}")
        result_by_id[test_id] = row.get("status", "UNKNOWN")
    for test_id in required:
        status = result_by_id.get(test_id)
        if status == "FAIL":
            failures.append(f"required test failed: {test_id}")
        elif status != "PASS":
            blockers.append(f"required test lacks an explicit PASS result: {test_id}")
    extra_ids = sorted(set(result_by_id) - set(required))
    if extra_ids:
        blockers.append("results contain IDs outside the required test plan: " + ", ".join(extra_ids))

    independent = evidence.get("independent_evaluation")
    if not isinstance(independent, dict):
        blockers.append("independent_evaluation is missing")
        independent = {}
    if independent.get("status") == "FAIL":
        failures.append("independent evaluation failed")
    elif independent.get("status") != "PASS":
        blockers.append("independent evaluation is not PASS")
    delivered_hash = independent.get("delivered_artifact_sha256")
    tested_hash = independent.get("tested_artifact_sha256")
    if not _is_sha256(delivered_hash) or not _is_sha256(tested_hash):
        blockers.append("delivered/tested artifact hashes must be lowercase SHA-256 digests")
    elif delivered_hash != tested_hash:
        failures.append("independent evaluator tested a different artifact")

    if failures:
        status = "FAIL"
    elif blockers:
        status = "BLOCKED"
    else:
        status = "PASS"

    result: dict[str, Any] = {
        "schema_version": 1,
        "status": status,
        "source_identity_status": manifest_status,
        "signature_policy": manifest_verification.get("signature_policy", "optional"),
        "signature_status": manifest_verification.get("signature_status", "missing"),
        "signature_valid": manifest_verification.get("signature_valid"),
        "signature_backend": manifest_verification.get("signature_backend"),
        "manifest_sha256": manifest_hash,
        "required_test_count": len(required),
        "executed_test_count": len(executed),
        "independent_evaluation_status": independent.get("status"),
        "failures": failures,
        "blockers": blockers,
    }
    result["qualification_sha256"] = object_sha256(result)
    return result
