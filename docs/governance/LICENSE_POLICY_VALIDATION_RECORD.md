# ASIG License Policy Negative-Control Validation Record

**Record ID:** ASIG-VAL-LIC-001  
**Date:** 2026-10-17  
**Status:** NEGATIVE CONTROL PASSED · VALIDATION ONLY  
**Repository:** `vaidt/Kt-ry-Program`  
**Implementation branch:** `infra/ci-updates`  
**Target branch used for the isolated PR:** `integration`  
**Authority boundary:** This record is test evidence only. It is not a final legal/licensing decision, does not revise `docs/UPSTREAM_AND_LICENSE.md`, and does not authorize Stage 3 or experimental merges.

## 1. Objective

Demonstrate that an explicit, validation-only Python dependency-license policy detects a prohibited GPL-family license label and causes a required GitHub status check to fail closed on an isolated pull request. The test must not merge the fixture or test policy into `integration` or `main`.

## 2. Tested implementation

The following controls were added on `infra/ci-updates`:

- `.github/workflows/security-controls.yml`: installs the vulnerability auditor in its existing environment and a separate isolated license-scanner environment; pins `pip-licenses==5.5.5`; generates a JSON inventory; invokes the explicit policy evaluator within the existing required `python-dependency-audit` job.
- `.github/license-policy.json`: policy identifier `ASIG-LICENSE-VALIDATION-001`, status `VALIDATION_ONLY`; lists GPL-2.0, GPL-3.0, and AGPL-3.0 families as blocked; routes LGPL/MPL-family, missing, unknown, or unrecognized metadata to fail-closed/manual-review outcomes.
- `scripts/check_license_policy.py`: evaluates the machine-readable license inventory and exits non-zero on banned or review-required findings.
- The inventory excludes `aura-source-identity-gate` itself because the repository's own licensing position remains undecided. This validation policy does not set that legal position.

Implementation baseline head used for the clean scan: `a00702d2ef28aeefd621bf58ae858d20678d74a7`.

- [Clean baseline ASIG Security Controls run 39050669832](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050669832): SUCCESS, including `python-dependency-audit`. This confirms the test scanner/policy can run against the environment without the synthetic prohibited-license fixture.

## 3. Isolated negative-control PR

| Item | Evidence |
|---|---|
| PR | [#17 — Negative control: prohibited dependency license](https://github.com/vaidt/Kt-ry-Program/pull/17) |
| Source branch | `validation/license-negative-control` |
| Final tested head SHA | `11564648914309b95f7d30d5340ba90be496816f` |
| Base | `integration` at `487e63069d18d2ab3f289131e9a5427f0cc61116` |
| Fixture | `asig-license-negative-control-fixture==0.0.1`; synthetic free-text license metadata `GNU General Public License v3 (GPLv3)`; not for distribution |
| CI | [ASIG CI run 39050856515](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050856515): SUCCESS |
| Security workflow | [ASIG Security Controls run 39050856436](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050856436): expected FAILURE |
| Required job | `python-dependency-audit`: FAILURE at `Enforce validation-only license policy` |
| Other security jobs | `secret-scan`: SUCCESS; `codeql`: SUCCESS |
| Merge blocking | Immediately before closure, PR API returned `mergeable_state = blocked`, `merged = false`; the required dependency-audit context was failing |
| PR disposition | CLOSED WITHOUT MERGE; `merged_at = null` |

## 4. Primary negative-control output

The final workflow log records that the synthetic fixture was successfully built and installed, then the policy evaluator emitted:

```text
LICENSE_POLICY_BANNED: asig-license-negative-control-fixture 0.0.1: 'GNU General Public License v3 (GPLv3)' — license is listed in the validation-only blocked policy
LICENSE_POLICY_FAIL: 1 blocking finding(s); policy=ASIG-LICENSE-VALIDATION-001 status=VALIDATION_ONLY
Process completed with exit code 1.
```

Source: the `python-dependency-audit` job log in [run 39050856436](https://github.com/vaidt/Kt-ry-Program/actions/runs/39050856436).

This is the counted result. It shows that the scanner output, policy evaluator, required status context, and API-observed merge block worked together for the specific synthetic GPLv3 fixture.

## 5. Superseded attempt — not counted

The previous PR head `8b962c33d35fa2767b189a22db3e61906a902931` is not accepted as negative-control evidence: setuptools rejected the synthetic fixture build before the scan ran because the initial fixture combined a modern license expression with a legacy GPL classifier. The fixture metadata was changed to a buildable free-text GPLv3 label, after which the final run above successfully reached the evaluator and produced the explicit `LICENSE_POLICY_BANNED` result. The failed build is retained as historical iteration evidence but is not represented as a passing negative control.

## 6. Cleanup and ref verification

After preserving PR and workflow evidence:

1. PR #17 was closed with `merged = false` and `merged_at = null`.
2. The source ref `refs/heads/validation/license-negative-control` at head `11564648914309b95f7d30d5340ba90be496816f` was deleted through the authorized GitHub reference-deletion operation.
3. A subsequent reference lookup returned HTTP 404 `Not Found`.
4. A repository branch inventory (page 1, 100 branches) contained no `validation/license-negative-control` entry.

This establishes deletion of the branch reference, not erasure of historical Git objects. The synthetic fixture remains in the closed PR's historical commit graph for auditability; it was not merged into `integration` or `main`.

## 7. Disposition and limits

**Gate 3 technical negative control: PASS.** The control detected the prohibited synthetic GPLv3 label and blocked the PR through a required check.

The approved list remains a validation-only test policy, not a final licensing decision. The status of the repository's own license and `UPSTREAM_AND_LICENSE.md` is unchanged. The license-negative-control test does not validate cryptographic artifact-attestation verification, which remains open.

**Program status remains:** `VALIDATION ONLY · NOT ACTIVE FOR EXPERIMENTAL MERGES`.  
**Stage 3:** NOT AUTHORIZED.
