import unittest
from datetime import datetime, timedelta, timezone

from scripts.validate_project_delegations import validate_record


def timestamp(offset_days=0):
    return (datetime.now(timezone.utc) + timedelta(days=offset_days)).isoformat()


def base_record():
    return {
        "schema_version": "1.0",
        "delegation_id": "ASIG-DEL-0001",
        "title": "Add bounded documentation",
        "status": "BLOCKED",
        "request": {
            "objective": "Add a bounded documentation section.",
            "requester": "project-owner",
            "created_at": timestamp()
        },
        "scope": {
            "repositories": [{"repository_full_name": "vaidt/Kt-ry-Program", "ref": "main"}],
            "in_scope": ["docs only"],
            "out_of_scope": ["protocol normative changes"],
            "paths_allowed": ["docs/**"],
            "paths_forbidden": ["src/**", ".github/workflows/**"]
        },
        "execution": {
            "implementation_authorized": False,
            "source_branch": "docs/delegation-0001",
            "target_branch": "main",
            "change_class": "DOCS_ONLY",
            "pull_request_required": True,
            "direct_push_permitted": False,
            "network_side_effects": "NONE"
        },
        "authority": {
            "decision_status": "NOT_PROVEN",
            "issuer": "",
            "current_holder": "",
            "scope": [],
            "effective_from": "",
            "valid_until": "",
            "decision_ref": "",
            "evidence_refs": [],
            "normative_effect": "NONE"
        },
        "verification": {
            "required_tests": ["unit-test"],
            "results": [],
            "reviewer_role": "Independent reviewer",
            "independence_status": "NOT_PROVEN",
            "evidence_refs": []
        },
        "evidence": {"evidence_refs": [], "artifact_names": []},
        "rollback": {
            "plan": "Revert the task branch through a normal pull request.",
            "trigger_conditions": ["A required check fails"]
        }
    }


def authorize_for_rd(record):
    record["status"] = "AUTHORIZED_FOR_R&D"
    record["execution"]["implementation_authorized"] = True
    record["authority"].update({
        "decision_status": "PROVEN",
        "issuer": "documented-competent-issuer",
        "current_holder": "documented-current-holder",
        "scope": ["non-authoritative R&D documentation"],
        "effective_from": timestamp(-1),
        "valid_until": timestamp(5),
        "decision_ref": "governance/decision-001.md",
        "evidence_refs": ["evidence/authority-chain.md"]
    })
    return record


class ProjectDelegationValidationTests(unittest.TestCase):
    def test_blocked_template_record_does_not_grant_authority(self):
        record = base_record()
        self.assertEqual(validate_record(record), [])

    def test_authorized_without_constitutive_evidence_is_rejected(self):
        record = base_record()
        record["status"] = "AUTHORIZED_FOR_R&D"
        record["execution"]["implementation_authorized"] = True
        errors = validate_record(record)
        self.assertTrue(any("authority is NOT_PROVEN" in item for item in errors))

    def test_valid_bounded_rd_authorization_passes(self):
        record = authorize_for_rd(base_record())
        self.assertEqual(validate_record(record), [])

    def test_protocol_normative_work_cannot_be_authorized_by_asig_gate(self):
        record = authorize_for_rd(base_record())
        record["execution"]["change_class"] = "PROTOCOL_NORMATIVE"
        self.assertTrue(any("cannot authorize protocol" in item for item in validate_record(record)))

    def test_verified_requires_pass_results_and_independence(self):
        record = authorize_for_rd(base_record())
        record["status"] = "VERIFIED"
        record["verification"]["results"] = [
            {"test_id": "unit-test", "status": "PASS", "evidence_ref": "actions/run/123"}
        ]
        record["verification"]["evidence_refs"] = ["actions/run/123"]
        record["evidence"]["evidence_refs"] = ["actions/run/123"]
        errors = validate_record(record)
        self.assertTrue(any("proven reviewer independence" in item for item in errors))

    def test_expired_authority_cannot_authorize_execution(self):
        record = authorize_for_rd(base_record())
        record["authority"]["valid_until"] = timestamp(-1)
        errors = validate_record(record)
        self.assertTrue(any("has expired" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
