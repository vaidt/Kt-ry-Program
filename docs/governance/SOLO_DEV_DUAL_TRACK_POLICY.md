# Solo-Developer Dual-Track Governance Policy

**Document ID:** ASIG-GOV-DT-001  
**Version:** 0.1  
**Status:** RATIFIED FOR PREPARATION ONLY · NOT ACTIVE FOR INTEGRATION  
**Repository scope:** `vaidt/Kt-ry-Program` (ASIG engineering controls only)  
**Policy record:** [PR #12 operational decision](https://github.com/vaidt/Kt-ry-Program/pull/12#issuecomment-6235297660)  
**Decision date:** 2026-10-17  
**Normative effect:** NONE ON AURA PROTOCOL; repository-level operational effect is limited to CI/security-infrastructure preparation  
**Implementation authorization:** LIMITED — isolated CI/security-infrastructure preparation only; `integration` activation NOT AUTHORIZED

> The repository owner recorded limited operational ratification for implementation preparation in PR #12. This does not activate `integration`, change GitHub protection settings, close CAPA NC-ASIG-2026-10-17-PR10, authorize runtime work, or modify AURA Protocol semantics. Experimental merges on `integration` remain prohibited until the activation checklist below is satisfied and its controls have been verified.

## 1. Purpose and decision requested

Define a controlled dual-track workflow for a repository operated by a solo developer, while preserving `main` as the authoritative integration and release boundary.

The recorded decision adopts this policy only as authorization to prepare CI/security infrastructure. The `integration` branch is not yet authorized for experimental merges. Activation requires the verified controls and completed checklist in Section 9; `integration` must never become an alternate authoritative branch.

The decision requested from the competent repository/governance authority is whether to adopt this policy, reject it, or return it for changes. Adoption must be recorded separately from this proposal.

## 2. Principles and precedence

The following principles apply:

1. **Track separation:** experimental work and authoritative delivery have different permitted claims and gates.
2. **Main remains protected:** no procedure in this policy authorizes disabling `enforce_admins`, reducing required checks, bypassing protection, force-pushing, or directly pushing to `main`.
3. **Evidence before status:** a control is ACTIVE only when its configuration and execution are evidenced. A requirement written here is not evidence that a scanner or check is already running.
4. **Fail closed:** failed, skipped, cancelled, missing, stale, or unobservable mandatory controls are not PASS. They block the affected merge or promotion.
5. **Automation is not independence:** automated scanning and attestation provide evidence and compensating controls; they are not a human independent review and do not satisfy a required human approval.
6. **Claims are scoped:** source inventory, build context, test results, runtime identity, protocol conformance, and release qualification remain distinct claims.
7. **No retroactive cure:** adoption of this policy cannot retroactively make a previously unreviewed merge compliant or close a deviation without its own verified corrective-action disposition.
8. **No normative protocol effect:** this repository policy does not ratify, amend, or interpret AURA Protocol requirements and does not resolve separate AURA authority-continuity or normative-governance blockers.

## 3. Scope

### 3.1 In scope

- The workflow and CI/CD controls for `vaidt/Kt-ry-Program`.
- Future, isolated experimental work on a proposed `integration` branch.
- Local prototyping, documentation, CI configuration experiments, adapter-harness development, and tests of ASIG itself.
- Evidence recording for checks, artifacts, source snapshots, and promotion decisions.

### 3.2 Out of scope without separate authorization

- Modifications to `vaidt/aura-poc-a-core-v3.3`, `vaidt/aura-guard-v1.3`, `vaidt/Aura-Guard`, or `vaidt/aura-specification`.
- RI-PY or RI-RS target runtime execution, changes to target repositories, or claims of target runtime identity.
- AURA protocol conformance, normative status, release qualification, production readiness, or regulatory approval.
- Closing or reclassifying CAPA NC-ASIG-2026-10-17-PR10.
- Changing `main` branch protection or the existing required human-review rule.

Any such work requires its own documented scope, evidence, and applicable authorization.

## 4. Track definitions

### 4.1 Authoritative track — `main`

`main` remains the only authoritative integration baseline for the repository and any releases made from it.

Required invariants:

- Branch protection remains enabled.
- Administrator enforcement remains enabled (`enforce_admins = true`).
- Existing required review and status-check requirements remain in force unless changed through a separately authorized governance decision.
- No direct push, force-push, deletion, or undocumented break-glass operation is permitted.
- Release tags and release artifacts must be produced from an explicitly selected authoritative commit, not from `integration`.
- A merge to `main` does not by itself establish AURA protocol conformance or authorize runtime release gates.

### 4.2 Experimental track — proposed `integration`

The branch may be created only after this policy is ratified and the activation checklist in Section 9 passes.

Permitted activity, subject to the repository's accepted licensing and security requirements:

- prototyping CI/CD configuration and non-authoritative test harnesses;
- testing ASIG changes against ASIG's own fixtures and controlled local samples;
- developing documentation and proposed controls;
- testing candidate scanner integrations and evidence-capture processes.

The branch is explicitly **non-authoritative**. Its contents, test outputs, artifacts, reports, and successful status checks must not be represented as release-qualified or AURA-conformant.

The branch is not a protection bypass for `main`. Its ability to accept experimental work never grants a right to promote that work.

## 5. Compensating controls proposed for the experimental track

All controls in this section are **PROPOSED requirements until configured, executed, and verified**. Before the branch becomes operational, the responsible person must publish a control inventory containing the exact workflow/check name, source revision, configuration, evidence location, and verification result.

### 5.1 Baseline CI

For every pull request targeting `integration`, require:

- the existing unit-test/build matrix: Python 3.11, 3.12, and 3.13;
- the existing `runtime-adapter-integration` job;
- schema parsing, package compilation, and build checks already defined by the repository CI;
- additional tests relevant to the change, with test selection and expected outcomes stated in the pull request.

As known on 2026-10-17, `.github/workflows/ci.yml` defines the three-version Python matrix and `runtime-adapter-integration`, and triggers CI for pull requests. Its push trigger names `main` and `feat/**`; therefore direct pushes to a future `integration` branch are not currently shown as covered by that push trigger. Before activation, either extend triggers through a reviewed change or expressly configure and verify an equivalent workflow. Do not infer coverage from the existence of the workflow file alone.

Every mandatory check must report success for the exact pull-request head SHA. A missing or inconclusive check blocks merging to the experimental branch.

### 5.2 Static analysis and dependency controls

Before activation, configure and verify:

- SAST/static security analysis appropriate to the Python, JavaScript/Node, and Rust content actually present;
- dependency vulnerability scanning for supported lockfiles and package manifests;
- secret scanning, including prevention or blocking of newly introduced high-confidence secrets;
- license/dependency-policy checks where applicable;
- pinned or explicitly reviewed versions of CI actions and scanning tools, with a documented update process.

The policy does not prescribe an unconfigured scanner as already active. Scanner choice, version, thresholds, suppressions, and false-positive review must be documented. High-severity findings, exposed credentials, or unapproved suppressions block merge pending a recorded disposition.

The dedicated GitHub Dependency Review workflow is not present at this time. A bounded residual-risk decision for the non-authoritative R&D track is recorded in [SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md](SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md). The compensating Python dependency audit remains mandatory. This temporary R&D-only treatment is not a substitute for the missing PR dependency-diff control on `main` or for release promotion, and it does not permit adding another package ecosystem without corresponding verified scanning.

DAST is conditional: it is required only when a deployed test service or application is in scope and a safe, authorized test target exists. It is not a substitute for SAST or dependency scanning.

### 5.3 Artifact provenance and Sigstore verification

When a build artifact or evidence package is used to support a decision:

- bind the attestation to the exact artifact digest and source commit;
- constrain verification to the expected repository, workflow identity, ref, and predicate type;
- retain the attestation bundle, verification output, relevant workflow run URL, and SHA-256 digests;
- independently verify the attestation before relying on it as promotion evidence;
- treat missing, invalid, or scope-mismatched attestations as BLOCKED.

The existing read-only source-inventory attestation flow is limited to the evidence it describes. It is not a general attestation for all builds or tests. A valid signature/provenance statement authenticates stated origin and digest binding; it does not prove code correctness, complete test execution, runtime identity, or protocol conformance.

### 5.4 Evidence preservation and audit log

Each experimental pull request must include or link to:

- purpose, scope, known limitations, and affected components;
- source branch and exact head SHA;
- CI run URLs and mandatory-check outcomes;
- scan results, finding dispositions, and any approved suppressions;
- artifact digests and attestation verification where artifacts are relied upon;
- explicit statements of what was not tested or observed;
- promotion intent: `NOT REQUESTED`, `REQUESTED`, `BLOCKED`, or `APPROVED` by the competent authority.

Do not replace raw results with a summary alone. Store sufficient source evidence to reproduce the decision. Redact secrets safely; do not publish secret values to preserve a log.

### 5.5 Access and branch configuration

After ratification, configure an isolated branch-specific ruleset or equivalent settings for `integration`:

- forbid force pushes and branch deletion;
- require all mandatory CI/security status checks for the exact head SHA before merge;
- require review of workflow, security-policy, branch-rule, and release-control changes by an authorized human other than their author where such a reviewer is available;
- prohibit any configuration that grants `integration` a path to bypass `main` protection;
- document whether owner/admin bypasses exist on `integration`, their exact scope, and their audit evidence.

This proposal does **not** authorize any change to the present `main` protection. The actual settings must be read back from GitHub after any future configuration change.

## 6. Merge rules within the experimental track

Subject to policy adoption and successful activation:

1. Work is proposed through a pull request; direct pushes to `integration` are not the default workflow.
2. All mandatory checks in Section 5 must pass on the exact PR head SHA.
3. Any failed, skipped, stale, cancelled, unavailable, or inconclusive mandatory check blocks merge.
4. Security findings cannot be silently suppressed. Each accepted exception must identify the finding, rationale, compensating control, approver, and expiry/review date.
5. The merge result remains experimental and does not qualify for release or protocol-conformance claims.
6. Changes to security workflows, status-check definitions, scanner configuration, branch rules, or this policy must be separately identified and reviewed; they may not weaken the promotion contract within the same unreviewed change.

If GitHub cannot enforce these rules as configured, the branch remains non-operational until the discrepancy is corrected or a formally approved, narrowly scoped alternative is documented.

## 7. Promotion from `integration` to `main`

Promotion is a distinct decision. The following conditions are cumulative; passing CI alone is insufficient.

### 7.1 General promotion gates

- This policy is ratified and effective, and the applicable promotion procedure is active.
- The candidate change is proposed in a pull request to `main`, identifying the exact source/head SHA and proposed merge commit strategy.
- All currently required `main` checks pass on the candidate head, and the branch is up to date with its base as required.
- The required independent human review is recorded by an authorized account whose independence and permissions are evidenced. A second login, automated agent, author self-approval, AI analysis, or the policy author’s own assertion is not independent review.
- SAST, dependency, secret, and applicable license checks have no unresolved blocking findings.
- Required artifacts and attestations are valid for the exact source digest and expected workflow identity when they form part of the change's evidence.
- Evidence and limitations are recorded; no failed or absent observation is reclassified as PASS.
- Branch-protection settings are read back and shown to remain in force. No disabling of `enforce_admins` or bypass of required rules is permitted by this policy.

### 7.2 Additional gates for runtime or AURA-related claims

Before any promotion that could be used to authorize runtime qualification, target-repository execution, AURA conformance, or release readiness:

- the relevant test plan, target bindings, expected test set, toolchains, and scope must be explicitly approved;
- any prerequisite CAPA and governance blockers must be independently resolved according to their own closure criteria;
- required runtime evidence must be captured by the approved implementation and independently checked;
- protocol-normative decisions must have the required competent authorization and cannot be inferred from this repository policy;
- a separate release/conformance decision must explicitly authorize the precise claim and artifact.

A merge may be technically accepted without satisfying these additional gates, but no claim depending on the unmet gate may be made.

## 8. CAPA and deviation handling

CAPA NC-ASIG-2026-10-17-PR10 remains a separate record. This policy proposal does not close, downgrade, or supersede it.

CAPA closure requires its own evidence showing that the corrective actions were implemented, verified, and appropriately disposed. If the corrective action requires an independent reviewer, this policy cannot waive that requirement retroactively.

The PR #11 exception record, if merged in accordance with its explicitly authorized exception procedure, must remain transparently identified as an exception—not as a substitute for independent human review. Any decision to change the underlying policy must state whether it applies prospectively only and how unresolved past deviations will be handled.

## 9. Activation checklist — do not activate until every item is evidenced

- [x] Repository-owner decision and limited policy-ratification record identified: PR #12 comment https://github.com/vaidt/Kt-ry-Program/pull/12#issuecomment-6235297660.
- [x] Policy ratified for infrastructure preparation only on 2026-10-17. This does not authorize integration merges; all remaining activation controls are still required.
- [x] CAPA status and relationship are documented as a separate, unresolved record; no automatic closure is inferred.
- [ ] `integration` branch created from an identified base SHA. No branch is created by the present preparation step.
- [ ] CI triggers verified for pull requests and for any permitted push-based development workflow on the target ref.
- [x] Required status-check names and provider captured and read back in ruleset ID `25306960`; check contexts are bound to GitHub Actions app ID `15368`.
- [ ] SAST, dependency, secret, and applicable license scanners tested with positive and negative controls.
- [ ] CodeQL severity-threshold enforcement configured as a `code_scanning` rule and read back for the `integration` ref. A successful `codeql` job alone does not prove that findings are below threshold.
- [ ] Attestation verification identity, workflow, predicate, artifact digest, and retention rules documented and tested for the applicable R&D artifact flow.
- [x] Future-ref ruleset read back: ruleset [25306960](https://github.com/vaidt/Kt-ry-Program/rules/25306960) targets only `refs/heads/integration`, has no bypass actors, blocks deletion and force pushes, requires pull requests and resolved conversations, and requires all seven CI/security status checks.
- [x] `main` protection read back on 2026-10-17; `protected = true`, `enforce_admins = true`, one required approval, and its original four required checks remain unchanged.
- [x] Control evidence locations, responsible owner, risk expiry/review date, and review cadence recorded in [SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md](SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md).
- [x] Scope boundary and prohibited claims published in this policy.

An unchecked item means activation status is `BLOCKED`.

## 10. Change control, review, and effectiveness

The repository owner recorded a limited operational decision in PR #12 on 2026-10-17 authorizing preparation of CI/security infrastructure. That decision has repo-level effect for preparation only; it does not activate the `integration` track. The policy becomes operational for experimental merges only after the remaining activation checklist is evidenced, the branch-specific controls are configured and read back, and the authority's scope is recorded. A merge of this document alone is not proof that activation has occurred.

Changes to this policy require a pull request, a change rationale, a risk assessment, evidence of the previous effective version, and the appropriate review. Changes that affect `main` protection, release qualification, AURA Protocol semantics, or normative authority require the separate applicable authorization; this document cannot supply it.

Review the policy after a security incident, material change to repository workflows, change in GitHub protection configuration, adoption of a new runtime adapter, or at least every six months after it becomes effective.

## 11. Status summary

| Item | Status at decision time |
|---|---|
| This policy | RATIFIED FOR INFRASTRUCTURE PREPARATION ONLY / INTEGRATION MERGES NOT AUTHORIZED |
| `main` protection | Read back 2026-10-17 and unchanged: protected, admin enforcement true, one required approval, original four required CI contexts |
| `integration` branch | NOT CREATED |
| CI and security evidence checkpoint | `ASIG CI` run [39043353975](https://github.com/vaidt/Kt-ry-Program/actions/runs/39043353975) and `ASIG Security Controls` run [39043353992](https://github.com/vaidt/Kt-ry-Program/actions/runs/39043353992) succeeded on commit `5dae7b275277c92dc6f0173e6e74948256b4f370` |
| CodeQL | Analysis successful; scanned 22/22 Python files, 5/5 workflow files and 2/2 JavaScript files; SARIF upload completed. Alert-threshold enforcement remains a separate open activation item |
| Gitleaks | Push-diff scan found no leaks; additional redacted full-history scan inspected 132 commits / ~435.86 KB and found no leaks on the cited evidence checkpoint |
| Python dependency audit | `pip-audit . --strict` returned `No known vulnerabilities found` on the cited evidence checkpoint |
| Integration ruleset | Active, ID `25306960`, targeted only to `refs/heads/integration`; verified by read-back. No bypass actors. The branch itself remains absent |
| Dedicated Dependency Review | Absent; temporary R&D-only residual risk in [SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md](SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md) |
| Sigstore | Read-only source-inventory attestation exists; this is not a general build attestation |
| CAPA NC-ASIG-2026-10-17-PR10 | Separate and open; not closed by this policy |
| Runtime qualification / AURA conformance | Not authorized by this policy |

---

**End of policy.** This document records limited authorization for infrastructure preparation. It is not evidence that any scanner or GitHub setting has been configured, and it does not authorize experimental merges on `integration`.
