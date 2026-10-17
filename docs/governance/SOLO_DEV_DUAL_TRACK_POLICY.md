# Solo-Developer Dual-Track Governance Policy

**Document ID:** ASIG-GOV-DT-001  
**Version:** 0.1  
**Status:** RATIFIED FOR PREPARATION AND VALIDATION ONLY · NOT ACTIVE FOR EXPERIMENTAL MERGES  
**Repository scope:** `vaidt/Kt-ry-Program` (ASIG engineering controls only)  
**Policy record:** [PR #12 operational decision](https://github.com/vaidt/Kt-ry-Program/pull/12#issuecomment-6235297660)  
**Decision date:** 2026-10-17  
**Normative effect:** NONE ON AURA PROTOCOL; repository-level operational effect is limited to CI/security-infrastructure preparation  
**Implementation authorization:** LIMITED — isolated CI/security-infrastructure preparation and validation-only branch creation/test PRs from the recorded baseline; experimental merges NOT AUTHORIZED

> The repository owner recorded limited operational ratification for implementation preparation in PR #12; this document now records a further limited validation authorization. The `integration` ref may be created at exactly `487e63069d18d2ab3f289131e9a5427f0cc61116` solely to run isolated positive/negative CI and security-control PRs. This does not activate experimental merges, change `main` protection, close CAPA NC-ASIG-2026-10-17-PR10, authorize runtime work, or modify AURA Protocol semantics. No experimental code, including Stage 3 architecture, may be merged until every activation gate is evidenced and the validation PRs are closed without merging.

## 1. Purpose and decision requested

Define a controlled dual-track workflow for a repository operated by a solo developer, while preserving `main` as the authoritative integration and release boundary.

The recorded decision adopts this policy for infrastructure preparation and a strictly bounded validation phase. The `integration` branch may be created only at the exact SHA stated in Section 9, for validation-control PRs only; it is not authorized for experimental merges. Activation requires the verified controls and completed checklist in Section 9; `integration` must never become an alternate authoritative branch. Dependency-vulnerability, license-policy, and synthetic-artifact SLSA provenance validation evidence are now captured; temporary validation refs were deleted after evidence capture. The SLSA result is limited to the synthetic test artifact and does not establish production/release provenance.

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

The branch may be created for validation-only purposes under Section 9 after this authorization is committed. This is a narrow exception for testing controls, not activation for experimental merges; the full activation checklist remains outstanding.

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

As read from `infra/ci-updates` on 2026-10-17, `.github/workflows/ci.yml` includes `integration` in its push trigger and `.github/workflows/security-controls.yml` includes `integration` in its push trigger and pull-request target filters. This is configuration evidence only. After creating `integration`, verify actual runs against the exact ref and each negative/positive control PR; do not infer execution or enforcement from workflow YAML alone.

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

## 9. Activation checklist — do not activate experimental merges until every item is evidenced

### 9.0 Transitional authorization — validation only

**Validation authorization status: AUTHORIZED FOR VALIDATION ONLY.** This authorization permits only the following bounded actions:

1. Create `integration` at exactly `487e63069d18d2ab3f289131e9a5427f0cc61116`.
2. Create an isolated positive-control PR with a harmless change and separate negative-control PRs for CodeQL and Gitleaks. The negative controls must remain isolated to their own temporary branches and must not be merged.
3. Capture the exact head SHAs, workflow run URLs, required status-check conclusions, CodeQL alert details, ruleset evaluation evidence, and observed mergeability/merge-block state.
4. Close every validation PR without merging and attempt to delete its temporary source branch. If deletion cannot be completed through the authorized interface, record the ref as ABANDONED, not eligible for reuse or merge, and keep `integration` free of test vectors.

No experimental code, including Stage 3 architecture, may be merged to `integration` until all activation checklist items are satisfied and separately verified. This validation authorization does not permit changes to `main`, does not waive required `main` review, and does not activate runtime or protocol-conformance work.

- [x] Repository-owner decision and limited policy-ratification record identified: PR #12 comment https://github.com/vaidt/Kt-ry-Program/pull/12#issuecomment-6235297660.
- [x] Policy ratified for infrastructure preparation only on 2026-10-17. This does not authorize integration merges; all remaining activation controls are still required.
- [x] CAPA status and relationship are documented as a separate, unresolved record; no automatic closure is inferred.
- [x] `integration` branch created at the authorized exact base SHA `487e63069d18d2ab3f289131e9a5427f0cc61116`; the ref remains at that baseline and creation is validation-only.
- [x] CI push and pull-request triggers verified for the validation ref: baseline runs and validation PRs invoked the expected workflows; exact run evidence is recorded in §9.1.
- [x] Required status-check names and provider captured and read back in ruleset ID `25306960`; check contexts are bound to GitHub Actions app ID `15368`.
- [x] CodeQL/GitHub Advanced Security and Gitleaks positive/negative control behavior tested; evidence and scope are recorded in §9.1.
- [x] Dependency-vulnerability negative control completed through isolated PR #16; see §9.2. The required `python-dependency-audit` check detected known vulnerabilities in the pinned test dependency and failed as expected; the PR was blocked and closed without merging.
- [x] License-policy negative control completed through isolated PR #17; see [LICENSE_POLICY_VALIDATION_RECORD.md](LICENSE_POLICY_VALIDATION_RECORD.md). The required `python-dependency-audit` context failed on an explicit synthetic GPLv3 label, the PR was API-observed as blocked, closed without merge, and its source ref was deleted and verified absent.
- [x] Removed the three earlier retained ABANDONED validation refs through normal authorized repository administration, then reran the full-history Gitleaks scan successfully. [ASIG Security Controls run 39047435796](https://github.com/vaidt/Kt-ry-Program/actions/runs/39047435796) completed `success` on `infra/ci-updates` at SHA `5ac7ab4af75258e51d39a4b3b5ee358e5cc72192`; both `secret-scan` and `Scan full Git history (redacted)` passed. The earlier failure is retained as historical evidence below, not current status.
- [x] Deleted the test branch ref `validation/pip-audit-negative-control` at SHA `32bfb0e0d7a1d4d00f43bdabf07681101b080f7e` after preserving PR #16 and workflow evidence. After the authorized GitHub CLI DELETE request, a subsequent GitHub REST GET returned `404 Not Found`; a follow-up branch search returned no result for the validation ref. No vulnerable dependency change was merged.
- [x] CodeQL severity-threshold rule configured and read back in ruleset `25306960`: `security_alerts_threshold = high_or_higher`, `alerts_threshold = none`, tool `CodeQL`.
- [x] CodeQL merge-protection behavior observed on validation PR #15: CodeQL reported one `critical` `py/code-injection` alert, the GitHub Advanced Security `CodeQL` check failed, and the PR API state was `mergeable_state = blocked`; the PR was closed without merging. This is API-observed blocking evidence; no separate screenshot of the GUI Merge button was captured.
- [x] Synthetic-artifact SLSA provenance flow documented and independently verified on a separate GitHub-hosted runner: [run 39051752235](https://github.com/vaidt/Kt-ry-Program/actions/runs/39051752235). The signer workflow, source ref and commit, SLSA v1 predicate, certificate repository identity, Rekor timestamp, and SHA-256 subject digest were checked; a modified subject was rejected. See [ATTESTATION_VALIDATION_RECORD.md](ATTESTATION_VALIDATION_RECORD.md). This applies only to the synthetic R&D artifact; production/release artifacts remain unvalidated.
- [x] Future-ref ruleset read back: ruleset [25306960](https://github.com/vaidt/Kt-ry-Program/rules/25306960) targets only `refs/heads/integration`, has no bypass actors, blocks deletion and force pushes, requires pull requests and resolved conversations, and requires all seven CI/security status checks.
- [x] `main` protection read back on 2026-10-17; `protected = true`, `enforce_admins = true`, one required approval, and its original four required checks remain unchanged.
- [x] Control evidence locations, responsible owner, risk expiry/review date, and review cadence recorded in [SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md](SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md).
- [x] Scope boundary and prohibited claims published in this policy.

### 9.1 Validation execution record — 2026-10-17

Validation controls were executed against PRs targeting `integration`. All three PRs were closed without merging. The exact results follow.

| Control | Source head SHA | Evidence | Outcome |
|---|---|---|---|
| Positive control, harmless Markdown-only change | `a7694f4eef26dc9bc819bfd3ab7662a2f6f6dfdf` | [PR #13](https://github.com/vaidt/Kt-ry-Program/pull/13); [ASIG CI run 39045542805](https://github.com/vaidt/Kt-ry-Program/actions/runs/39045542805); [Security run 39045542806](https://github.com/vaidt/Kt-ry-Program/actions/runs/39045542806) | Both workflows passed; PR API reported `mergeable_state = clean` before closure. CLOSED WITHOUT MERGE. |
| Negative control, CodeQL code injection | `8e218086eca8bcb38066ea260cbcd4e1a4c9abb7` | [PR #15](https://github.com/vaidt/Kt-ry-Program/pull/15); [CodeQL alert/check](https://github.com/vaidt/Kt-ry-Program/runs/117433561414); [Security workflow 39045543039](https://github.com/vaidt/Kt-ry-Program/actions/runs/39045543039) | Alert `py/code-injection`, severity `critical`; GitHub Advanced Security `CodeQL` check failed; PR API state was `blocked`. The Actions job named `codeql` also completed successfully because the analysis/upload job itself ran to completion. CLOSED WITHOUT MERGE. |
| Negative control, Gitleaks synthetic AWS-shaped value | `7afaafe0243577b4870a9ac217d33f305eb136b1` | [PR #14](https://github.com/vaidt/Kt-ry-Program/pull/14); [Security workflow 39045696827](https://github.com/vaidt/Kt-ry-Program/actions/runs/39045696827); [secret-scan job](https://github.com/vaidt/Kt-ry-Program/actions/runs/39045696827/job/117433852344) | Rule `aws-access-token` found one test-only match; `secret-scan` failed; the Security workflow failed as expected; PR API state was `blocked`. The earlier invalid fixture on SHA `99bc0c5af98fc92e7575be45a42abe0c61c6b70d` was not counted as a successful negative control. CLOSED WITHOUT MERGE. |

Historical finding — the initial 2026-10-17 inventory showed `validation/positive-control` (`a7694f4eef26dc9bc819bfd3ab7662a2f6f6dfdf`), `validation/codeql-negative-control` (`8e218086eca8bcb38066ea260cbcd4e1a4c9abb7`), and `validation/gitleaks-negative-control` (`7afaafe0243577b4870a9ac217d33f305eb136b1`) still present after their PRs closed. These refs were subsequently deleted through authorized repository administration after evidence capture; the full-history Gitleaks rerun [39047435796](https://github.com/vaidt/Kt-ry-Program/actions/runs/39047435796) passed. The later pip-audit, license, and SLSA attestation validation refs were also deleted after evidence capture and verified absent by REST 404 and branch inventory. This records source-ref cleanup, not erasure of historical Git objects. No test fixture was merged to `integration` or `main`.

**Historical finding — full-history Gitleaks was blocked by a retained test ref.** On documentation-evidence commit `7fc39a93490ee1e6edd67ba1bb632699d081b3b3`, `ASIG CI` run [39046279758](https://github.com/vaidt/Kt-ry-Program/actions/runs/39046279758) succeeded. `ASIG Security Controls` run [39046279773](https://github.com/vaidt/Kt-ry-Program/actions/runs/39046279773) failed because the full-history step found the synthetic `aws-access-token` fixture on `validation/gitleaks-negative-control`. This is preserved as historical evidence; the former blocker was subsequently resolved by deleting the three old validation refs and obtaining a clean post-cleanup scan as recorded below. No allowlist or suppression was introduced.

The controls recorded in §§9.1–9.4 support only the specific findings stated. Dependency-vulnerability and license-policy negative controls are evidenced; the synthetic-artifact SLSA provenance flow is verified in §9.4. Production/release artifact provenance and other activation controls remain outside this test's scope.

### 9.2 Dependency negative control — 2026-10-17

An isolated negative-control PR targeted `integration` from `validation/pip-audit-negative-control`. No test dependency was merged.

| Item | Evidence |
|---|---|
| PR | [PR #16](https://github.com/vaidt/Kt-ry-Program/pull/16), closed without merge; base `integration` SHA `487e63069d18d2ab3f289131e9a5427f0cc61116` |
| Tested head | `32bfb0e0d7a1d4d00f43bdabf07681101b080f7e`; one final file change in `pyproject.toml` pins `urllib3==1.26.15` |
| Advisory basis | `urllib3==1.26.15` is affected by [CVE-2023-45803 / GHSA-g4mx-q9vg-27p4](https://github.com/advisories/GHSA-g4mx-q9vg-27p4), fixed in 1.26.18, and [CVE-2023-43804 / GHSA-v845-jxx5-vc9f](https://github.com/advisories/GHSA-v845-jxx5-vc9f), fixed in 1.26.17. |
| Security workflow | [ASIG Security Controls run 39047903405](https://github.com/vaidt/Kt-ry-Program/actions/runs/39047903405) — **FAILURE** at `python-dependency-audit`. Installation succeeded; the audit reported **18 known vulnerabilities in urllib3 1.26.15**, including `PYSEC-2023-212` (fix 1.26.18) and `PYSEC-2023-192` (fix 1.26.17). |
| Other checks | [ASIG CI run 39047903383](https://github.com/vaidt/Kt-ry-Program/actions/runs/39047903383) — **SUCCESS**; `secret-scan` — **SUCCESS**; CodeQL job — **SUCCESS**. |
| Merge blocking | Before closure, the PR API reported `mergeable_state = blocked` while the required dependency audit check was `failure`. The PR was closed with `merged = false`. |

**Superseded initial probe:** the first commit used `urllib3==1.26.4`, which caused a `ModuleNotFoundError` inside the audit tool before advisory matching. That run is not counted as a successful negative control. The final tested head changed the pin to 1.26.15, remained compatible with the current audit tool, and produced vulnerability findings. Both attempts are preserved in the PR history; the final evidence is the run listed above.

The source ref `validation/pip-audit-negative-control` at tested head `32bfb0e0d7a1d4d00f43bdabf07681101b080f7e` was deleted after evidence capture. The subsequent GitHub REST GET returned `404 Not Found`, and a follow-up branch search returned no matching validation ref. The ref cleanup is recorded COMPLETE based on this API read-back; this does not imply purging historical Git objects or close any other activation gate. No vulnerable package change was merged to `integration` or `main`.


### 9.3 License policy negative control — 2026-10-17

See the detailed, preserved evidence in [LICENSE_POLICY_VALIDATION_RECORD.md](LICENSE_POLICY_VALIDATION_RECORD.md). The final isolated test used head `11564648914309b95f7d30d5340ba90be496816f` against base `integration` at `487e63069d18d2ab3f289131e9a5427f0cc61116`.

| Control | Evidence | Outcome |
|---|---|---|
| Clean implementation baseline | [ASIG Security Controls run 39050669832](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050669832) on infrastructure baseline `a00702d2ef28aeefd621bf58ae858d20678d74a7` | SUCCESS; policy and scanner execute without the synthetic prohibited-license fixture. |
| Negative control, synthetic GPLv3 dependency metadata | [PR #17](https://github.com/vaidt/Kt-ry-Program/pull/17); [ASIG CI run 39050856515](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050856515); [ASIG Security Controls run 39050856436](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050856436) | CI SUCCESS; required `python-dependency-audit` FAILURE at `Enforce validation-only license policy`, emitting `LICENSE_POLICY_BANNED` for `GNU General Public License v3 (GPLv3)`; CodeQL and secret-scan SUCCESS. Before closure, PR API reported `mergeable_state = blocked`. CLOSED WITHOUT MERGE. |
| Test-ref cleanup | PR #17 closed with `merged = false`, `merged_at = null`; REST ref lookup returned HTTP 404 and the branch inventory contained no matching `validation/license-negative-control` ref. | Cleanup complete; no fixture merged to `integration` or `main`. |

The earlier PR head `8b962c33d35fa2767b189a22db3e61906a902931` is excluded from negative-control evidence because fixture packaging failed before the scanner ran. Only the final run that produced an explicit `LICENSE_POLICY_BANNED` result is counted.

The policy remains **VALIDATION ONLY**. The synthetic-artifact SLSA provenance test is technically complete, but it does not attest the repository's actual sdist, wheel, or release artifacts. It does not determine the repository's final license, revise `UPSTREAM_AND_LICENSE.md`, or establish a legal license-compliance conclusion.


### 9.4 SLSA artifact-attestation validation — 2026-10-17

See [ATTESTATION_VALIDATION_RECORD.md](ATTESTATION_VALIDATION_RECORD.md) for the full evidence, command, certificate fields, raw output markers and retention information. The isolated test used PR [#18](https://github.com/vaidt/Kt-ry-Program/pull/18), tested head `b2e7f1b72a80b0140649c0236eabbc051e925ab5`, and base `integration` at `487e63069d18d2ab3f289131e9a5427f0cc61116`. PR #18 was closed without merging; before closure, its API state was `mergeable_state = clean`. This test was not intended to demonstrate merge-blocking behavior.

| Control | Evidence | Outcome |
|---|---|---|
| Build and attest | [ASIG SLSA Attestation Validation run 39051752235](https://github.com/vaidt/Kt-ry-Program/actions/runs/39051752235) | SUCCESS. Synthetic `asig-slsa-validation.tar.gz` built and signed using `actions/attest-build-provenance` v3.2.0 pinned to commit `96278af6caaf10aea03fd8d33a09a777ca52d62f`; SLSA v1 predicate produced. |
| Separate-runner CLI verification | Same run, job `verify-out-of-band`; [raw verification evidence artifact 12108195314](https://github.com/vaidt/Kt-ry-Program/actions/runs/39051752235/artifacts/12108195314) | SUCCESS. `gh version 2.102.0`; CLI exit `0`; signer workflow, source ref/commit and predicate constrained. Certificate source repository ID `1423292837`; OIDC issuer `https://token.actions.githubusercontent.com`; Sigstore certificate issuer `CN=sigstore-intermediate,O=sigstore.dev`; one verified Rekor timestamp at `2026-10-17T16:59:08Z`. |
| Artifact digest binding | [Build artifact 12107712455](https://github.com/vaidt/Kt-ry-Program/actions/runs/39051752235/artifacts/12107712455); raw output in artifact 12108195314 | Local SHA-256 and attested subject SHA-256 match: `1483325b7a4fd3829bd347222101002b54a07a70a62d66ae6316682df0cec9d9`. |
| Tamper negative control | Same run, step `Tamper negative control — modified artifact must fail verification` | PASS: appended bytes were rejected by `gh attestation verify` with exit code 1; no attestation matched the altered digest. |
| PR disposition / test-ref cleanup | [PR #18](https://github.com/vaidt/Kt-ry-Program/pull/18) | CLOSED WITHOUT MERGE (`merged = false`, `merged_at = null`). Source ref deleted; REST lookup returned 404 and branch inventory showed no matching ref. |

The test artifacts and raw verifier output were uploaded with seven-day retention. The record preserves key digests and certificate fields beyond that temporary window. The attested subject was synthetic; this run does not demonstrate that ASIG's normal sdist, wheel or release outputs currently carry verified provenance.

This closes the **synthetic-artifact R&D attestation validation item** only. It does not authorize synchronizing rules to `integration`, establish a production SLSA level, certify source-code correctness or protocol conformance, or activate Stage 3.

An unchecked item means activation status is `BLOCKED`.

## 10. Change control, review, and effectiveness

The repository owner recorded limited operational authorization for infrastructure preparation in PR #12; the subsequent validation authorization permitted only the controls recorded in §9.1. These validation results do not activate the `integration` track for experimental merges. The policy becomes operational for experimental merges only after every activation checklist item, including applicable artifact-attestation verification, is evidenced and the authorization scope is separately recorded. A successful CI run or a documentation commit alone is not proof that activation has occurred.

Changes to this policy require a pull request, a change rationale, a risk assessment, evidence of the previous effective version, and the appropriate review. Changes that affect `main` protection, release qualification, AURA Protocol semantics, or normative authority require the separate applicable authorization; this document cannot supply it.

Review the policy after a security incident, material change to repository workflows, change in GitHub protection configuration, adoption of a new runtime adapter, or at least every six months after it becomes effective.

## 11. Status summary

| Item | Status at decision time |
|---|---|
| This policy | RATIFIED FOR PREPARATION AND VALIDATION ONLY / EXPERIMENTAL MERGES BLOCKED — DEPENDENCY, LICENSE AND SYNTHETIC-ARTIFACT ATTESTATION TESTS EVIDENCED; PRODUCTION/RELEASE PROVENANCE AND OTHER ACTIVATION CONTROLS REMAIN OPEN |
| `main` protection | Read back 2026-10-17 and unchanged: protected, admin enforcement true, one required approval, original four required CI contexts |
| `integration` branch | Created and still at `487e63069d18d2ab3f289131e9a5427f0cc61116`; protected by ruleset 25306960; validation-only, experimental merges blocked |
| CI and security evidence checkpoint | [ASIG CI run 39046385384](https://github.com/vaidt/Kt-ry-Program/actions/runs/39046385384) and post-cleanup [ASIG Security Controls run 39047435796](https://github.com/vaidt/Kt-ry-Program/actions/runs/39047435796) passed on `infra/ci-updates` SHA `5ac7ab4af75258e51d39a4b3b5ee358e5cc72192`; §9.1 records the earlier failed scan and its subsequent resolution. |
| CodeQL | Ruleset 25306960 has `security_alerts_threshold = high_or_higher`; PR #15 returned one critical `py/code-injection` finding, a failing GitHub Advanced Security `CodeQL` check, and API-observed `blocked` mergeability. See §9.1; no test PR merged. |
| Gitleaks | Post-cleanup full-history scan [run 39047435796](https://github.com/vaidt/Kt-ry-Program/actions/runs/39047435796) passed, including the `Scan full Git history (redacted)` step. The three prior validation refs were absent at read-back. The later pip-audit negative-control ref was also deleted after its evidence was preserved; the subsequent REST GET returned `404 Not Found`. License-test ref `validation/license-negative-control` was likewise deleted after PR #17 evidence capture and verified absent by REST 404 and branch inventory. |
| Python dependency audit | Baseline audit in [run 39047435796](https://github.com/vaidt/Kt-ry-Program/actions/runs/39047435796) passed. Negative-control PR #16 caused the required audit to fail with 18 known findings for `urllib3==1.26.15`; PR was blocked and closed without merging. See §9.2. |
| License policy | Validation-only negative-control PR #17 emitted `LICENSE_POLICY_BANNED` for the synthetic GPLv3 fixture; required `python-dependency-audit` failed and PR was API-observed as blocked, then closed without merge. The isolated source ref was deleted and verified absent. See §9.3 and [LICENSE_POLICY_VALIDATION_RECORD.md](LICENSE_POLICY_VALIDATION_RECORD.md). The final legal/repository-license disposition remains OPEN. |
| Integration ruleset | Active, ID `25306960`, targeted only to `refs/heads/integration`; verified by read-back. No bypass actors. The branch exists at the authorized validation baseline and remains restricted to validation; experimental merges are not authorized. |
| Dedicated Dependency Review | Absent; temporary R&D-only residual risk in [SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md](SECURITY_CONTROL_RESIDUAL_RISK_REGISTER.md) |
| Sigstore / SLSA | Read-only source-inventory attestation is distinct from the synthetic-artifact build-provenance validation in §9.4; no product release artifact has been attested by this test |
| CAPA NC-ASIG-2026-10-17-PR10 | Separate and open; not closed by this policy |
| Runtime qualification / AURA conformance | Not authorized by this policy |

---

**End of policy.** The positive control and the CodeQL, Gitleaks, dependency-vulnerability, license-policy, and synthetic-artifact SLSA controls have produced the results recorded in §§9.1–9.4; all validation PRs were closed without merging. The earlier validation refs were deleted after evidence capture and the post-cleanup full-history Gitleaks scan passed in run 39047435796. The pip-audit, license, and SLSA attestation test refs were deleted and verified absent by REST 404 and branch inventory. The synthetic artifact's signature, signer workflow, source ref/commit, SLSA v1 predicate, Rekor timestamp, and SHA-256 subject digest passed CLI verification; this does not prove provenance for actual release artifacts. The current status remains **NOT ACTIVE FOR EXPERIMENTAL MERGES** because remaining activation requirements, including the separate CodeQL alert-enforcement gap, final license-policy/legal disposition, and production/release assurance, remain unresolved. `main` and `integration` were not changed by the validation PRs; Stage 3 remains unauthorized by this policy.
