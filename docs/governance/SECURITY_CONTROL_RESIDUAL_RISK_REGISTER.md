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

## RISK-ASIG-SAST-002 — CodeQL run status is not yet severity-threshold enforcement

| Field | Decision |
|---|---|
| Risk statement | The `codeql` status check currently proves that the analysis job ran successfully and uploaded SARIF, but the integration-targeted ruleset does not yet have GitHub's separate `code_scanning` rule with an explicit severity threshold. A successful job alone must not be interpreted as “zero alerts.” |
| Evidence | On commit `5dae7b275277c92dc6f0173e6e74948256b4f370`, CodeQL scanned 22/22 Python files, 5/5 GitHub Actions workflow files, and 2/2 JavaScript files; SARIF upload and analysis processing completed successfully. Alert severity inventory was not independently reconciled as part of this run. |
| Treatment | OPEN — activation blocker for experimental merges. After `integration` exists and has CodeQL results attached to that ref, add a `code_scanning` ruleset rule for CodeQL with an explicit security-alert threshold and a code-alert threshold, then read it back. Keep the branch unavailable for experimental merges until this gate is in place. |
| Status | NOT ACCEPTED for merge exposure; block experimental merges until closed. |

## Ruleset evidence — future integration ref

A repository ruleset was created and read back on 2026-10-17:

- Ruleset: [ASIG integration — R&D protection](https://github.com/vaidt/Kt-ry-Program/rules/25306960)
- Ruleset ID: `25306960`; enforcement: `active`
- Exact target: `refs/heads/integration`; no bypass actors; read-back reports `current_user_can_bypass = never`
- Active rules: deletion blocked; force pushes blocked; pull request required with zero required human approvals for the solo-developer R&D workflow; conversation resolution required; strict required status checks for `test-and-build (3.11)`, `test-and-build (3.12)`, `test-and-build (3.13)`, `runtime-adapter-integration`, `codeql`, `secret-scan`, and `python-dependency-audit`. All seven check contexts are bound to GitHub Actions app ID `15368`.
- The `integration` branch has **not** been created. The ruleset currently protects the future matching ref only; the CodeQL severity-threshold rule remains outstanding as described above.

## Activation constraints

This register alone does not satisfy the policy activation checklist. Before `integration` becomes available for experimental merges:

- `ASIG CI` and `ASIG Security Controls` must pass on the exact candidate head;
- the redacted full-history Gitleaks scan must pass on the exact workflow revision;
- the CodeQL `code_scanning` severity-threshold rule must be added after the branch has a valid analysis for its ref and verified by read-back;
- positive/negative control tests and the remaining activation requirements in `SOLO_DEV_DUAL_TRACK_POLICY.md` must be evidenced;
- `main` branch protection and `enforce_admins = true` must remain unchanged and be independently read back.

**End of register.** The Dependency Review exception is bounded to non-authoritative R&D. The separate CodeQL alert-enforcement gap is open and blocks experimental merges.

