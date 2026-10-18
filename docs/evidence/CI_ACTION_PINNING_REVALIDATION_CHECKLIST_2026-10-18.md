# CI Action Pinning — Revalidation Checklist

**Date:** 2026-10-18  
**Repository:** `vaidt/Kt-ry-Program`  
**Incident run:** [39130015871](https://github.com/vaidt/Kt-ry-Program/actions/runs/39130015871)  
**Affected source commit:** `d2ed5821412ba69e4a7294fb832bd2da5fa92002`  
**Remediation branch:** `infra/pin-actions-sha-failure-39130015871`  
**Status:** PATCH PREPARED · EXECUTION EVIDENCE PENDING · NOT MERGED

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

The Rust action is pinned to a commit on the author's `master` history and has the explicit input `toolchain: stable`. This preserves the intended Rust stable toolchain while satisfying SHA pinning.

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

## 4. Revalidation checklist

Mark each item only after evidence is available.

- [x] Create a remediation branch from `main`; do not modify `main` directly.
- [x] Pin all action references involved in the four failed required check jobs.
- [x] Pin action references in the separately failing Pages build/deploy workflow.
- [x] Preserve Python 3.11–3.13 matrix and Node.js 22 setup.
- [x] Preserve least-privilege permissions and existing `persist-credentials: false`.
- [x] Confirm action refs came from official upstream GitHub API refs/commit records.
- [ ] Verify the branch diff contains only the intended workflow changes plus this checklist.
- [ ] Run a YAML/workflow static validator (preferably `actionlint`) against both workflow files.
- [ ] Confirm `uses:` refs in these two files all match a full 40-character SHA.
- [ ] Observe a new branch-triggered CI run and confirm all four required jobs get past action setup.
- [ ] Verify Python 3.11, 3.12 and 3.13 jobs actually execute unit tests and package builds.
- [ ] Verify runtime adapter tests actually execute and record their result.
- [ ] Dispatch or otherwise validate the Pages workflow against this branch without deploying to production; if the available workflow mechanism cannot test it safely, record that limitation.
- [ ] Confirm new required check results are attached to the exact remediation head SHA.
- [ ] Obtain the required independent review and follow normal merge controls; do not bypass rules.
- [ ] After merge, verify the exact resulting `main` SHA and required-check results.

## 5. Scope limitation

The patch is targeted at the failing workflows observed for this incident. The current repository also has mutable action tags in other workflows, including the read-only pilot, reference-source inventory, and release workflows. They were not changed in this minimal incident patch and must not be described as repo-wide SHA-pinning compliant. If the policy is enforced uniformly for all workflows, track those files as a separate follow-up before their next execution.

## 6. Current disposition

- Workflow patch: **PREPARED ON A SEPARATE BRANCH**
- Application tests on patched workflow: **NOT YET PROVEN BY THIS CHECKLIST**
- Merge to `main`: **NOT PERFORMED**
- Branch protection / ruleset mutations: **NONE**
- Incident closure: **OPEN pending execution evidence**

A successful action-initialization phase alone is insufficient. Close this remediation only after the jobs execute the actual test commands and the results are tied to the exact reviewed commit.
