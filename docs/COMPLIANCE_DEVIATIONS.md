# Compliance Deviation Register

## NC-ASIG-2026-10-17-PR10 — Merge without recorded independent approval

**Status:** OPEN — CAPA implementation in progress  
**Classification:** Process nonconformity / Segregation of Duties control failure  
**Detection date:** 2026-10-17  
**Affected repository:** `vaidt/Kt-ry-Program`  
**Related PR:** [#10 — Record post-merge source inventory evidence for run 39038179646](https://github.com/vaidt/Kt-ry-Program/pull/10)

### 1. Deviation statement

PR #10 was merged without a recorded independent approving review. The GitHub pull-request API records the PR as merged at **2026-10-17 14:05:08 UTC**, with `merged_by.login = vaidt`, and the submitted review list returned an empty array (`reviews: []`). The merge commit is `8b62cca211cd8969040aa90ac501db5fa6649bca`; the PR head commit was `27f276a812a5f0afb9de97276f605c45f5bb880c`, based on `0c50927f85bbee62cee84d0f099d1a220351daf0`.

The change merged by PR #10 was limited to the documentation file `docs/REFERENCE_INVENTORY_EVIDENCE_VERIFICATION.md` (103 additions, 0 deletions); no runtime source code was changed by that PR.

### 2. Objective evidence

- [PR #10 metadata](https://api.github.com/repos/vaidt/Kt-ry-Program/pulls/10) records `merged=true`, `merged_at=2026-10-17T14:05:08Z`, `merged_by.login=vaidt`, and `changed_files=1`.
- [PR #10 review API](https://api.github.com/repos/vaidt/Kt-ry-Program/pulls/10/reviews) returned an empty review collection. No independent `APPROVED` review is recorded.
- [CI run 39039018292](https://github.com/vaidt/Kt-ry-Program/actions/runs/39039018292) completed with `success` before the recorded merge time. CI success does not substitute for human approval.
- During the pre-remediation control inspection, GitHub's branch-protection endpoint returned 404 with “No branch protection data available”. The exact branch-protection activation timestamp is not included in the captured endpoint response; therefore, this report records the confirmed control failure (merge with no recorded approval) without asserting an unsupported activation timestamp.

### 3. Root cause and contributing conditions

**Confirmed failure mode:** the merge process did not prevent PR #10 from being merged without an independent approval.

**Root-cause assessment:** preventative branch controls were absent or not effectively enforced during the merge window. The earlier branch-protection read returned no protection data, and the PR was merged with zero submitted reviews. The available snapshots do not establish the exact instant at which the later protection configuration became effective. This timing uncertainty does not change the deviation finding: an approval is not recorded for the merge.

**Contributing condition:** the repository's prior merge path did not provide a verified, enforced separation between change author/merger and an independent reviewer.

### 4. Correction and preventive actions

| ID | Action | Evidence / acceptance criterion | Status |
|---|---|---|---|
| CA-01 | Record this deviation in version-controlled documentation. | This register is included in the remediation PR. | Implemented in PR #11 |
| PA-01 | Require a pull request and at least one approving review on `main`. | GitHub branch-protection readback reports `required_approving_review_count = 1`. | Implemented; verified by API |
| PA-02 | Enforce the branch rules for administrators. | Readback reports `enforce_admins.enabled = true`. | Implemented; verified by API |
| PA-03 | Require all CI contexts that protect merge readiness. | Required contexts: `test-and-build (3.11)`, `test-and-build (3.12)`, `test-and-build (3.13)`, `runtime-adapter-integration`; strict up-to-date requirement enabled. | Implemented; verified by API |
| PA-04 | Reject force pushes and deletion of `main`. | Readback reports `allow_force_pushes.enabled = false` and `allow_deletions.enabled = false`. | Implemented; verified by API |
| PA-05 | Dismiss stale approvals when new commits are pushed; require conversation resolution. | Readback reports `dismiss_stale_reviews = true` and `required_conversation_resolution.enabled = true`. | Implemented; verified by API |
| PA-06 | Attach reproducible checksum and Sigstore evidence from the original run. | Complete five-entry `SHA256SUMS`, raw timestamped workflow log excerpts, artifact/attestation digests, and source run link are recorded in the remediation PR. | Implemented in PR #11 |
| PA-07 | Require genuine independent peer review of this remediation PR. | A reviewer other than the PR author/merger submits an `APPROVED` review; required CI contexts pass before merge. | Pending external reviewer |
| EV-01 | Test the amended preventative controls with this PR. | PR #11 remains unmerged until the branch protection gate and independent review are satisfied; no administrative/bypass merge. | Pending CI and independent approval |

### 5. CAPA closure criteria

This deviation remains **OPEN** until all of the following are evidenced:

1. The remediation PR's required CI contexts finish successfully.
2. A genuinely independent reviewer submits an approving review on the remediation PR.
3. GitHub shows that the required review and status checks are satisfied before merge, and the PR is merged through the protected PR path.
4. Post-merge verification confirms that `main` remains protected with the expected review and status-check rules.
5. The resulting evidence is preserved in the repository and the deviation disposition is updated to reflect the actual observed results.

No runtime work is authorized by this deviation record. Etap 3 remains on hold until CAPA closure is documented separately.

### 6. Boundaries

This record does not retroactively create a review for PR #10, does not characterize CI success as peer approval, and does not establish runtime qualification or protocol conformance. PR #10's historical review deficiency must remain visible in the audit trail.

---

## 7. Documented break-glass exception — PR #11

**Exception ID:** `BG-ASIG-2026-10-17-PR11`  
**Status before execution:** AUTHORIZED BY REPOSITORY OWNER — EXECUTION AND POST-CHECK PENDING  
**Scope:** PR #11 only; documentation and audit evidence only.

The repository owner has authorized a narrowly scoped administrator override for merging PR #11 after successful required CI, because no secondary human reviewer is available in this working environment. The purpose is to merge the CAPA record and source evidence, not to authorize runtime work or release activity.

### 7.1 Review classification and transparency

An AI-assisted review was performed out-of-band in this conversation. It is **not** a GitHub `APPROVED` review, is not a review by a separate human actor, and does not satisfy the normal independent-review control. No GitHub identity or review event is attributed to the AI auditor. The decision to proceed is recorded as a documented administrative exception, rather than misrepresented as an independent human approval.

### 7.2 Authorized break-glass sequence

1. Confirm that all required status checks on PR #11 have completed with `success`.
2. Record the then-current `main` commit and read back the complete existing branch-protection configuration.
3. Temporarily set only `enforce_admins.enabled = false` to permit the specifically authorized administrator merge. Do not remove the required-review count, status-check contexts, strict up-to-date requirement, stale-review dismissal, conversation resolution, force-push restriction, or branch-deletion restriction.
4. Merge PR #11 using the expected reviewed head SHA. Do not merge any other pull request during the exception window.
5. Immediately restore `enforce_admins.enabled = true`.
6. Read back the branch and protection endpoints, verify `main` is still protected and all expected review/status-check settings remain active, and record the merge SHA plus the UTC times for the disable/merge/restore/read-back sequence in the PR #11 discussion.

### 7.3 Closure criteria and limitation

This is a **single-use, time-bounded exception** only for PR #11. It does not waive the general segregation-of-duties requirement for future changes, and it does not permit direct pushes to `main`, force pushes, branch deletion, runtime tests against RI-PY/RI-RS, changes to the target repositories, protocol-conformance claims, or release-gate authorization.

The exception is not considered successfully executed until post-merge read-back verifies that administrator enforcement has been restored. Until the sequence and post-check are complete, `NC-ASIG-2026-10-17-PR10` remains **OPEN** and Etap 3 remains **BLOCKED**. Record actual execution times and merge identity in the PR #11 timeline; do not infer them in advance.

