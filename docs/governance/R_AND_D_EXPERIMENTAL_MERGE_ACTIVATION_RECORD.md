# ASIG R&D-Only Experimental-Merge Activation Record

**Record ID:** ASIG-GOV-ACT-001  
**Version:** 0.1  
**Decision date:** 2026-10-17  
**Repository:** `vaidt/Kt-ry-Program`  
**Source branch:** `infra/ci-updates`  
**Target branch:** `integration`  
**Status:** OWNER-AUTHORIZED FOR R&D-ONLY ACTIVATION AFTER CLEAN BASELINE-PROMOTION PR MERGE  
**Authority boundary:** Repository engineering workflow only. No AURA Protocol normative effect, Stage 3 authorization, runtime qualification, CAPA closure, product/release approval, or promotion to `main`.

## 1. Decision and scope

The repository owner expressly directed a baseline-promotion step after completion of the four isolated R&D validation controls: Gitleaks, pip-audit, the validation-only license-policy negative control, and the synthetic-artifact SLSA provenance control.

This record authorizes the policy status `ACTIVE FOR EXPERIMENTAL MERGES (R&D ONLY)` to become operational on `integration` only after the clean pull request from `infra/ci-updates` to `integration` merges while every required status check is `success` on the exact PR head and the effective repository ruleset is still satisfied.

The authorization is limited to non-authoritative R&D work on `integration`: CI/security infrastructure, documentation, prototypes, adapters, local test harnesses, and controlled fixtures. It does not authorize Stage 3, runtime execution against AURA target repositories, AURA Protocol changes or conformance claims, production/release qualification, or changes to `main`.

CAPA `NC-ASIG-2026-10-17-PR10` remains separate and open. No prior deviation is closed by this decision.

## 2. Effective ruleset read-back

Direct GitHub API read-back on 2026-10-17 confirmed:

| Property | Observed value |
|---|---|
| Ruleset | [ASIG integration — R&D protection](https://github.com/vaidt/Kt-ry-Program/rules/25306960) |
| ID | `25306960` |
| Enforcement | `active` |
| Exact target | `refs/heads/integration` |
| Bypass actors | Empty list |
| `current_user_can_bypass` | `never` |
| Required checks strict/up-to-date | `strict_required_status_checks_policy = true` |
| Required approvals | `required_approving_review_count = 0` for the solo-developer workflow |
| Other PR rules | Pull request required; conversation resolution required |
| Force push / delete | Blocked by `non_fast_forward` and `deletion` rules |
| CodeQL alert threshold | `security_alerts_threshold = high_or_higher`; `alerts_threshold = none` |

The seven required contexts, all from GitHub Actions App ID `15368`, are:

1. `test-and-build (3.11)`
2. `test-and-build (3.12)`
3. `test-and-build (3.13)`
4. `runtime-adapter-integration`
5. `codeql`
6. `secret-scan`
7. `python-dependency-audit`

This means the planned merge must follow the normal ruleset path; it must not use administrator bypass. The absence of classic branch-protection data for `integration` does not nullify the separately confirmed active repository ruleset.

## 3. CodeQL enforcement evidence

- The effective ruleset includes a CodeQL `code_scanning` rule with `security_alerts_threshold = high_or_higher`.
- The required status context `codeql` is bound to GitHub Actions App ID `15368`.
- Validation PR [#15](https://github.com/vaidt/Kt-ry-Program/pull/15) produced a critical `py/code-injection` alert. The GitHub Advanced Security CodeQL check failed and the PR API reported `mergeable_state = blocked`. PR #15 was closed without merging.
- The earlier statement that effective ruleset enforcement was still unverified is superseded by this direct ruleset read-back and the API-observed negative-control result. A successful CodeQL analysis job alone is not interpreted as zero alerts; the configured alert threshold and the associated merge-blocking check are separate controls.

## 4. Pre-promotion baseline evidence

Immediately before the policy-status revision, `infra/ci-updates` was at `6a772da08729e5b0a32f5a09c14d1da085ad93bb`. The seven ruleset-required contexts reported `success` on that exact head. Relevant check records are in [ASIG CI / security workflow runs 39052474783 and 39052474740](https://github.com/vaidt/Kt-ry-Program/actions).

This is a preflight baseline result only. It does not substitute for the required seven green contexts on the final baseline-promotion PR head. After opening the promotion PR, the merge is permitted only if all seven checks complete successfully on that exact head, no mandatory check is pending/skipped/cancelled/missing, all review conversations are resolved, the head remains mergeable, and the ruleset read-back remains unchanged.

## 5. Residual risks explicitly retained

| Residual item | Required boundary |
|---|---|
| Final repository licensing/legal disposition | `UPSTREAM_AND_LICENSE.md` remains undecided. The current `pip-licenses==5.5.5` blocklist is a fail-closed R&D control, not a legal decision. Do not distribute or promote R&D results as a product release until the appropriate licensing decision is recorded. |
| Dedicated Dependency Review | Still absent. The documented compensating control is the required Python `pip-audit` check plus the license-policy checker. Do not add non-Python package ecosystems without corresponding scanning. Review/expiry remains no later than 2026-11-17. |
| Release artifacts / production provenance | Only a synthetic tarball was attested and independently verified. No claim is made that the actual ASIG sdist, wheel, release package, or deployed artifact currently carries valid provenance. Actual release artifact attestation and verification remain a separate gate. |
| CAPA | `NC-ASIG-2026-10-17-PR10` remains OPEN and separate. |
| Stage 3 / Protocol / runtime | Not authorized by this record. |

The residual risks above are accepted only to enable the bounded non-authoritative R&D track. They must not be treated as closed or satisfied for release, production, main-branch promotion, AURA protocol conformance, or regulatory claims.

## 6. Promotion and post-merge verification

The baseline-promotion PR is the first normal, non-negative-control PR from `infra/ci-updates` to `integration`. It must:

- preserve `main` at its current SHA and leave its protection unchanged;
- preserve the current `integration` ruleset and all seven status contexts;
- pass all seven checks on the exact PR head;
- be merged only through the ruleset with no bypass;
- be re-read after merge to verify that `integration` advanced to the recorded merge commit, `main` did not move, the ruleset remains active, and the source `infra/ci-updates` branch still exists until any separately approved cleanup decision.

The source branch should not be deleted as part of the promotion itself unless a separate decision explicitly authorizes deletion after successful merge and evidence capture.

## 7. Final status boundary

After successful baseline-promotion merge, the repository policy status is:

`ACTIVE FOR EXPERIMENTAL MERGES (R&D ONLY)`

This means only non-authoritative R&D experimentation on `integration` can proceed under the seven-check ruleset. It does not mean Stage 3 is authorized. It does not mean the final license decision, CAPA, release provenance, production readiness, runtime identity, or AURA protocol conformance is resolved.

`main` remains authoritative and protected. `integration` remains non-authoritative.
