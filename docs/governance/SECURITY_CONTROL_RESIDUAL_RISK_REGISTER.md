# Security Control Residual Risk Register

**Document ID:** ASIG-RISK-REG-001  
**Version:** 0.1  
**Status:** ACTIVE FOR INFRASTRUCTURE PREPARATION · R&D-ONLY RISK ACCEPTANCE  
**Repository:** `vaidt/Kt-ry-Program`  
**Branch:** `infra/ci-updates`  
**Decision date:** 2026-10-17  
**Scope boundary:** non-authoritative R&D only; no promotion/release effect

> This register records limited residual-risk acceptance for the proposed experimental track. It does not waive `main` branch protection, authorize release, close CAPA NC-ASIG-2026-10-17-PR10, or establish AURA Protocol conformance. The `integration` branch is not activated by this register.

## RISK-ASIG-DEP-001 — No dedicated GitHub Dependency Review workflow

| Field | Decision |
|---|---|
| Risk statement | The repository does not yet have a dedicated `.github/workflows/dependency-review.yml` gate that performs dependency-diff review on pull requests. |
| Cause / event | An attempt to add the standalone workflow file through the available GitHub write tool was blocked by the tool safety layer. The exact underlying cause was not established; this register does not attribute the denial to GitHub permissions or organization policy without evidence. |
| Inherent risk | Medium for non-authoritative R&D: a PR-level dependency-diff control is absent, so the change set does not receive that distinct layer of dependency review. |
| Compensating control | `.github/workflows/security-controls.yml` runs the pinned `pip-audit` tool against the local project's declared dependency graph (`.venv/bin/pip-audit . --strict --progress-spinner off`) on push and on pull requests targeting `main` or `integration`. The run on baseline commit `fa5e4254f0770d37480e47033b2c3407fce9cf4b` reported `No known vulnerabilities found`. The separate CodeQL and Gitleaks jobs are complementary controls, not replacements for dependency review. |
| Residual limitation | `pip-audit` audits the Python project's declared dependencies against its configured vulnerability service; it is not a general PR dependency-diff policy and does not review every ecosystem or GitHub Action reference. New non-Python package manifests/lockfiles must not be introduced on the experimental track until corresponding dependency scanning is configured and verified. |
| Treatment | **Temporarily accepted for non-authoritative R&D only**, provided the `python-dependency-audit` check remains required for every relevant experimental pull request and fails closed. |
| Prohibited use | This acceptance does not apply to `main`, production/release promotion, AURA conformance claims, or any change requiring a stronger supply-chain assessment. It cannot be used to waive required human review on `main`. |
| Owner | Repository owner / ASIG control-plane owner |
| Review / expiry | Reassess before the first promotion request to `main`, before adding a non-Python manifest/lockfile, after a material dependency/security incident, and no later than 2026-11-17. Dedicated Dependency Review should be restored when an authorized implementation path is available. |
| Status | ACCEPTED TEMPORARILY — R&D ONLY; implementation/activation gates remain separate. |

### Evidence chronology

1. Security-control run [39042744250](https://github.com/vaidt/Kt-ry-Program/actions/runs/39042744250) on commit `969c3720f739e3b72b93f4bc2c7b11a7930a5721` failed at `pip-audit --local` because the locally installed project distribution `aura-source-identity-gate==0.2.0` is not published on PyPI. The log did not report a vulnerability; it reported that the project package could not be resolved from PyPI.
2. The command was corrected to audit the local project definition, `pip-audit . --strict`, following the tool's documented project-path mode. Reference: [pip-audit usage documentation](https://github.com/pypa/pip-audit#usage).
3. Security-control run [39043042585](https://github.com/vaidt/Kt-ry-Program/actions/runs/39043042585) on commit `fa5e4254f0770d37480e47033b2c3407fce9cf4b` completed successfully. The dependency audit reported `No known vulnerabilities found`; CodeQL completed its analysis and uploaded SARIF; Gitleaks reported `No leaks detected`.
4. The Gitleaks action on a push event scanned the pushed commit range as selected by the action (one commit in that step). A separate redacted full-history scan is now also part of the workflow. On the validated head below it scanned 132 commits / approximately 435.86 KB and reported `no leaks found`.
5. The dedicated Dependency Review workflow is not present. This residual-risk entry records the bounded R&D-only treatment; it does not claim equivalence to Dependency Review.

## RISK-ASIG-SAST-002 — CodeQL threshold rule configured; behavior validation pending

| Field | Decision |
|---|---|
| Risk statement | A successful CodeQL job alone does not mean “zero alerts.” The required CodeQL security-alert severity threshold is now configured in the integration-targeted ruleset, but end-to-end enforcement has not yet been exercised against an existing `integration` ref because that branch has not been created. |
| Evidence | Security-control run [39043855790](https://github.com/vaidt/Kt-ry-Program/actions/runs/39043855790) on commit `7f5562747b264304a615ab8d1277bf15e49d32a8` completed successfully. CodeQL scanned 22/22 Python files, 5/5 GitHub Actions workflow files, and 2/2 JavaScript files; SARIF upload and processing completed. Ruleset [25306960](https://github.com/vaidt/Kt-ry-Program/rules/25306960) was updated and read back on 2026-10-17 with a `code_scanning` rule for `CodeQL`: `security_alerts_threshold = high_or_higher`, `alerts_threshold = none`. |
| Treatment | CONFIGURED / READ-BACK VERIFIED; activation gate remains open pending behavior validation. After `integration` exists and the code-scanning analysis is associated with that ref, validate the native ruleset against the exact target commit and reference. Do not claim prevention of a merge until the branch/ref behavior is empirically verified. |
| Status | CONFIGURATION PASS; ENFORCEMENT BEHAVIOR NOT YET TESTED. Experimental merges remain blocked until the remaining activation criteria are met. |

## Ruleset evidence — future integration ref

A repository ruleset was created and read back on 2026-10-17:

- Ruleset: [ASIG integration — R&D protection](https://github.com/vaidt/Kt-ry-Program/rules/25306960)
- Ruleset ID: `25306960`; enforcement: `active`
- Exact target: `refs/heads/integration`; no bypass actors; read-back reports `current_user_can_bypass = never`
- Active rules: deletion blocked; force pushes blocked; pull request required with zero required human approvals for the solo-developer R&D workflow; conversation resolution required; strict required status checks for `test-and-build (3.11)`, `test-and-build (3.12)`, `test-and-build (3.13)`, `runtime-adapter-integration`, `codeql`, `secret-scan`, and `python-dependency-audit`. All seven check contexts are bound to GitHub Actions app ID `15368`.
- The `integration` branch has **not** been created. The ruleset currently protects the future matching ref only; the CodeQL severity-threshold rule remains outstanding as described above.


## RISK-ASIG-LIC-001 — Validation-only license gate is not the final licensing decision

| Field | Decision |
|---|---|
| Risk statement | The repository's own licensing terms remain undecided. A technical scanner and a test blocked-license list must not be represented as legal approval, a final dependency-policy decision, or a substitute for review of `UPSTREAM_AND_LICENSE.md`. |
| Validation evidence | [License-policy validation record](LICENSE_POLICY_VALIDATION_RECORD.md); isolated [PR #17](https://github.com/vaidt/Kt-ry-Program/pull/17), final head `11564648914309b95f7d30d5340ba90be496816f`; [ASIG CI run 39050856515](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050856515) SUCCESS; [ASIG Security Controls run 39050856436](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050856436) failed as expected at required `python-dependency-audit`, with explicit `LICENSE_POLICY_BANNED` output for synthetic GPLv3 metadata. PR API reported `mergeable_state = blocked`; PR closed without merge, source ref deleted and verified absent. |
| Test-only control | `pip-licenses==5.5.5`, machine-readable `.github/license-policy.json`, and `scripts/check_license_policy.py`. GPL-2.0/GPL-3.0/AGPL-3.0 families are blocked in validation only; LGPL/MPL, missing metadata, and unknown/unrecognized labels fail closed for manual review. The current policy excludes `aura-source-identity-gate` from scanner inventory so the undecided repository license does not self-trigger the test gate. |
| Residual limitation | This test covers one synthetic GPLv3 label and the required status blocking behavior. It does not prove comprehensive license-expression normalization, source-file scanning for license texts, runtime/deployment license obligations, or a legal determination. The blocklist requires separate final review before any production use. |
| Status | NEGATIVE-CONTROL TECHNICAL TEST PASS; FINAL LICENSE POLICY / LEGAL DISPOSITION OPEN; VALIDATION ONLY. |
| Prohibited use | Do not claim repository licensing has been settled, do not change `UPSTREAM_AND_LICENSE.md` on this basis, and do not activate experimental merges or Stage 3. |
| Review / expiry | Reassess before any promotion request to `main` or proposal to activate experimental merges; include legal/licensing review by the responsible authority. |

## Activation constraints

This register alone does not satisfy the policy activation checklist. Before `integration` becomes available for experimental merges:

- `ASIG CI` and `ASIG Security Controls` must pass on the exact candidate head;
- the redacted full-history Gitleaks scan must pass on the exact workflow revision;
- the CodeQL `code_scanning` rule is now configured and read back in ruleset `25306960` (`security_alerts_threshold = high_or_higher`); enforcement behavior still must be validated once the target ref has CodeQL results;
- positive/negative control tests and the remaining activation requirements in `SOLO_DEV_DUAL_TRACK_POLICY.md` must be evidenced;
- `main` branch protection and `enforce_admins = true` must remain unchanged and be independently read back.

**End of register.** The Dependency Review exception is bounded to non-authoritative R&D. The license negative-control technically passed, but final license-policy/legal disposition and applicable artifact-attestation verification remain open. The separate CodeQL alert-enforcement gap described above and the remaining activation controls continue to block experimental merges.

