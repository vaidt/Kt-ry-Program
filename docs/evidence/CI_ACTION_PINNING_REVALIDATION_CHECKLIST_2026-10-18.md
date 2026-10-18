# CI Action Pinning — Revalidation Checklist

**Date:** 2026-10-18  
**Repository:** `vaidt/Kt-ry-Program`  
**Incident run:** [39130015871](https://github.com/vaidt/Kt-ry-Program/actions/runs/39130015871)  
**Affected source commit:** `d2ed5821412ba69e4a7294fb832bd2da5fa92002`  
**Remediation branch:** `infra/pin-actions-sha-failure-39130015871`  
**Verified test head before this evidence update:** `9c1fa773e181e6162165be02fac60b7c9659cf29`  
**Status:** PATCH PREPARED · CI PASS ON TESTED HEAD · INDEPENDENT REVIEW PENDING · NOT MERGED

## 1. Incident evidence

The failed jobs stopped while GitHub Actions was preparing the job, before application tests ran. Their logs report that actions referenced by version tags are disallowed because this repository requires every action to be pinned to a full-length commit SHA.

Affected required check contexts on `d2ed582`:

- `test-and-build (3.11)` — failed during action setup
- `test-and-build (3.12)` — failed during action setup
- `test-and-build (3.13)` — failed during action setup
- `runtime-adapter-integration` — failed during action setup

The same commit also had a separate `build` job failure from `.github/workflows/jekyll-gh-pages.yml`, caused by mutable action tags. This patch updates that workflow too.

**Interpretation constraint:** those failures are not test failures in application code. Since setup stopped first, test results for those jobs are unavailable.

## 2. Changes prepared on the remediation branch

### `.github/workflows/ci.yml`

Replaced moving tags with 40-character commit SHAs:

| Action | Immutable ref selected |
|---|---|
| `actions/checkout` (v4 line) | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/setup-python` (v5 line) | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `actions/setup-node` (v4 line) | `49933ea5288caeca8642d1e84afbd3f7d6820020` |
| `actions/upload-artifact` (v4 line) | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| `dtolnay/rust-toolchain` | `683b588c487a69d01f6c6ddf40f036ff682cc2c8` |

The Rust action is pinned to a commit in the author's `master` history and uses the explicit input `toolchain: stable`. This preserves the intended Rust stable toolchain while satisfying SHA pinning.

Preserved workflow contract:
- Python matrix 3.11, 3.12, 3.13
- Node.js 22 adapter setup
- Python unit tests, schema validation, compile, wheel and source-distribution build
- runtime adapter contract test command
- top-level and job-level least-privilege `permissions`
- existing `persist-credentials: false` on the runtime adapter checkout
- existing artifact naming and retention

### `.github/workflows/jekyll-gh-pages.yml`

Pinned each referenced action, including the deployment action, so the Pages build does not leave a second mutable-tag failure path:

| Action | Immutable ref selected |
|---|---|
| `actions/checkout` | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/configure-pages` | `983d7736d9b0ae728b81ab479565c72886d7745b` |
| `actions/jekyll-build-pages` | `44a6e6beabd48582f863aeeb6cb2151cc1716697` |
| `actions/upload-pages-artifact` | `56afc609e74202658d3ffba0e8f6dda462b719fa` |
| `actions/deploy-pages` | `368f82528645a54fb793d4d04e342629a3f51346` |

No branch-protection setting, ruleset, application source file, release authorization, or default-branch reference was changed by this patch.

## 3. SHA source and provenance checks

The SHAs above were resolved using the official GitHub API references for the corresponding action repositories (the v4/v5/v1/v3 tag refs) and the official `dtolnay/rust-toolchain` commit endpoint. The commit IDs used in the workflow are full 40-character hexadecimal object IDs, not version tags or branch names.

This documents source resolution; it is not a cryptographic verification of the upstream maintainers' signing identity. Action execution on the branch remains required.

## 4. Revalidation results

The branch diff against `main` was inspected. It contains exactly these three intended paths:
- `.github/workflows/ci.yml`
- `.github/workflows/jekyll-gh-pages.yml`
- `docs/evidence/CI_ACTION_PINNING_REVALIDATION_CHECKLIST_2026-10-18.md`

The two workflow files were checked for action-reference syntax: all 13 `uses:` references in these two files end in full 40-character hexadecimal SHAs. The GitHub Actions runner successfully parsed and executed `ci.yml`; a separate `actionlint` execution was not performed in this environment.

### Successful execution evidence

| Run / job | Tested head | Result |
|---|---|---|
| [ASIG CI run #199](https://github.com/vaidt/Kt-ry-Program/actions/runs/39130751252) | `9c1fa773e181e6162165be02fac60b7c9659cf29` | **SUCCESS** |
| `test-and-build (3.11)` | same | **PASS**, unit tests ran (21 tests), package build and artifact upload passed |
| `test-and-build (3.12)` | same | **PASS**, unit tests ran (21 tests) and package build passed |
| `test-and-build (3.13)` | same | **PASS**, unit tests ran (21 tests) and package build passed |
| `runtime-adapter-integration` | same | **PASS**, runtime contract tests ran (7 tests) |
| [ASIG Security Controls run #79](https://github.com/vaidt/Kt-ry-Program/actions/runs/39130751381) | same | **SUCCESS** — secret scan, dependency/license audit, and CodeQL completed successfully |

The above results apply to the exact tested head listed in the table. This evidence document is being updated in a subsequent commit; GitHub must run CI again for the resulting updated branch head, and the final PR must have passing checks on its exact head SHA before merge.

### Remaining verification

- [x] Create a remediation branch from `main`; do not modify `main` directly.
- [x] Pin all action references involved in the four failed required check jobs.
- [x] Pin action references in the separately failing Pages build/deploy workflow.
- [x] Preserve Python 3.11–3.13 matrix and Node.js 22 setup.
- [x] Preserve least-privilege permissions and existing `persist-credentials: false`.
- [x] Confirm action refs came from official upstream GitHub API refs/commit records.
- [x] Inspect the three-path diff against `main`.
- [x] Confirm `uses:` refs in the two changed workflow files all match a full 40-character SHA.
- [x] Confirm all four required jobs got past action setup and ran tests on the tested head.
- [x] Confirm secret scan, dependency/license audit and CodeQL completed on the tested head.
- [ ] Confirm required checks pass on the final updated branch head and PR head SHA.
- [ ] Run a separate YAML/workflow static validator (preferably `actionlint`); GitHub's successful `ci.yml` execution is not represented as an `actionlint` result.
- [ ] Validate the Pages workflow safely on the proposed ref without a production deployment, or explicitly document an approved alternative. This workflow has not been executed in this remediation.
- [ ] Obtain an independent review from a reviewer other than the change preparer; this assistant's technical pre-review is not independent human approval.
- [ ] Merge only through normal repository review and required-check controls.
- [ ] After merge, verify the exact resulting `main` SHA and its required-check results.

## 5. Scope limitation

The patch is targeted at the failing workflows observed for this incident. The current repository also has mutable action tags in other workflows, including the read-only pilot, reference-source inventory, and release workflows. They were not changed in this incident patch and must not be described as repo-wide SHA-pinning compliant. If the policy is enforced uniformly for all workflows, track those files as a separate follow-up before their next execution.

A non-blocking Node.js 20 deprecation warning was observed in the successful run for some pinned actions, which GitHub said were being forced to run on Node.js 24. This did not fail the run but should be considered in a separate action-version compatibility review.

## 6. Current disposition

- Workflow patch: **PREPARED ON A SEPARATE BRANCH**
- ASIG CI on tested head: **PASS; evidence above**
- Current updated head / PR head: **MUST BE REVALIDATED**
- Pages workflow on remediation branch: **NOT EXECUTED**
- Independent review: **PENDING**
- Merge to `main`: **NOT PERFORMED**
- Branch protection / ruleset mutations: **NONE**
- Incident closure: **OPEN pending final-head CI, independent review, and required process**

A successful action-initialization phase alone is insufficient. The reviewed PR head must have passing required checks and an independent review; the remaining Pages and repository-wide pinning scope limitations must remain explicit.
