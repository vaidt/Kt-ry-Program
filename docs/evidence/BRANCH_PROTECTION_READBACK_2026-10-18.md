# Branch Protection Read-back — 2026-10-18

## Disposition

**Current-state control result:** PASS for the fields listed below.  
**Historical restore sequence:** NOT PROVEN.  
**CAPA:** Remains OPEN; this evidence does not close the deviation.

## Repository and endpoints

- Repository: `vaidt/Kt-ry-Program`
- Branch: `main`
- Full read-back endpoint: https://api.github.com/repos/vaidt/Kt-ry-Program/branches/main/protection
- Administrator-enforcement endpoint: https://api.github.com/repos/vaidt/Kt-ry-Program/branches/main/protection/enforce_admins
- Read-back command shown in the supplied Termux screenshot:
  `gh api repos/vaidt/Kt-ry-Program/branches/main/protection > main-branch-protection.json`
- Display command: `cat main-branch-protection.json`

## Observed configuration

The supplied screenshot shows the GitHub API response containing the following values:

| Field | Observed value |
|---|---|
| `enforce_admins.enabled` | `true` |
| `required_pull_request_reviews.required_approving_review_count` | `1` |
| `required_pull_request_reviews.dismiss_stale_reviews` | `true` |
| `required_pull_request_reviews.require_code_owner_reviews` | `false` |
| `required_pull_request_reviews.require_last_push_approval` | `false` |
| `required_status_checks.strict` | `true` |
| Required status checks | `test-and-build (3.11)`, `test-and-build (3.12)`, `test-and-build (3.13)`, `runtime-adapter-integration` |
| `required_conversation_resolution.enabled` | `true` |
| `allow_force_pushes.enabled` | `false` |
| `allow_deletions.enabled` | `false` |
| `required_signatures.enabled` | `false` |
| `lock_branch.enabled` | `false` |

The independently read repository ruleset is also active and requires the same four status-check contexts and one approving review; its bypass-actor list is empty and `current_user_can_bypass` was returned as `never`. Ruleset read-back: https://github.com/vaidt/Kt-ry-Program/rules/25323386.

## Source artifact and handling

- Source: JPEG screenshot supplied by the repository operator in this audit conversation, showing the Termux commands and the output of `cat main-branch-protection.json`.
- The device clock visible in the image reads **11:15**. The screenshot itself does not display a full date or timezone; the conversation date is 2026-10-18. The exact capture time in UTC is therefore **not independently attested**.
- SHA-256 of the supplied JPEG source bytes: `941d4eaf7b67a7780eedbbce60e65c9c5da05d36866f1bc43288bce3ede3a75d`.
- The raw JPEG is now committed in this branch at [`docs/evidence/BRANCH_PROTECTION_READBACK_2026-10-18.jpeg`](BRANCH_PROTECTION_READBACK_2026-10-18.jpeg). Local Termux output recorded the expected SHA-256 before commit. A subsequent GitHub Contents API read returned the committed file as Base64 with Git blob SHA `7d589fb0aad41faa689321b605858ff293fb54b1`; decoding the exact API-returned bytes produced 251,413 bytes and SHA-256 `941d4eaf7b67a7780eedbbce60e65c9c5da05d36866f1bc43288bce3ede3a75d`, matching the source hash. This verifies byte-for-byte hash agreement for the locally hashed source and the bytes returned by GitHub. The screenshot still does not attest its full capture date/time or timezone, and a hash alone does not independently attest the truth of the pictured API output.

## Evidentiary limitations

1. This is a point-in-time read-back. It establishes that `enforce_admins.enabled` was `true` when the displayed query was executed.
2. It does not establish when the setting was last changed, whether it was temporarily disabled for PR #11, or the UTC time at which it may have been restored.
3. The authorization text in PR #11 is not evidence that every step of the prescribed break-glass sequence actually occurred.
4. The result does not establish legal identity or whether distinct GitHub accounts are controlled by distinct humans.
5. It does not establish runtime qualification, protocol conformance, release readiness, or CAPA closure.



## Reviewer-account independence assessment — supplemental public evidence

### Account metadata observed

The public GitHub user endpoints were read during this review. The public fields below are platform metadata, not verified civil identity:

| Field | `kamilkrasinski4-sys` | `Kamil1230xd` |
|---|---|---|
| GitHub user ID | `243464820` | `170595912` |
| Account creation time | `2025-11-12T01:52:58Z` | `2024-05-23T04:08:32Z` |
| Public repositories | 4 | 23 |
| Public name / email / bio / company | Not populated | Not populated |
| Current repository collaborator check | `true` | `true` |

The first account's public repositories are Aura-related repositories, including `aura-specification`, `aura-poc-a-core-v3.3`, and `aura-guard-v1.3`, plus `aura-p0-0-toolchain`. The second account's public repositories include Aura-related projects such as `aura-idtoken`, `aura-sign-mvp`, `aura-cloudrun`, and `Aura`. The account creation dates and repository portfolios differ, but these differences do not prove distinct human controllers.

### Correlated review-event pattern

Public event feeds show the two accounts reviewing the same pull-request heads in repeated, close succession on 2026-10-18. Examples include:

| PR | First observed account event | Second observed account event | Difference |
|---|---|---|---:|
| #11 | `kamilkrasinski4-sys` — 09:02:35Z | `Kamil1230xd` — 09:03:01Z | 26 seconds |
| #22 | `Kamil1230xd` — 08:54:28Z | `kamilkrasinski4-sys` — 08:55:02Z | 34 seconds |
| #27 | `Kamil1230xd` — 08:45:02Z | `kamilkrasinski4-sys` — 08:46:13Z | 71 seconds |
| #23 | `kamilkrasinski4-sys` — 07:26:32Z | `Kamil1230xd` — 07:27:19Z | 47 seconds |
| #25 | `Kamil1230xd` — 06:20:37Z | `kamilkrasinski4-sys` — 06:21:35Z | 58 seconds |

The public events also show closely spaced, mirrored review/dismissal activity on PR #27: dismissal events at 07:49:47Z and 07:50:17Z, further dismissals at 07:57:30Z and 07:58:30Z, and approvals at 08:45:02Z and 08:46:13Z. Times are from public event objects, which may be recorded a few seconds after the underlying review submission. The specific PR #11 review API remains the authoritative source for its approval submissions and reviewed head.

These temporal correlations do **not** prove the accounts share an operator. They are, however, a material audit signal: the pattern is consistent with coordinated dual-account activity and cannot be treated as affirmative evidence of independent human review. Both accounts' publicly exposed name, email, bio and company fields are unpopulated, so the reviewed public metadata supplies no corroborating person-level distinction.

### Finding and required disposition

- GitHub platform events: **PASS** — two distinct user IDs submitted approvals to PR #11 before merge.
- Separate-account status: **PASS** — the platform records different account IDs.
- Separate human controllers / independent judgment: **NOT PROVEN**.
- Risk disposition: **ELEVATED / OPEN** until the project obtains evidence outside these GitHub account events that satisfies its segregation-of-duties criterion. Suitable evidence may include a documented, auditable attestation by the responsible individuals and an independently verified organizational identity/role link; the exact acceptable evidence standard is for the CAPA owner to define. Do not infer identity from profile names, repository history, timing, or the accounts' availability as connected integrations.

This section does not accuse either account of misconduct and does not conclude that the same person controls both. It records that the available evidence is insufficient to accept the independence claim.


## Related pull request sequence

- PR #11: https://github.com/vaidt/Kt-ry-Program/pull/11
- Reviewed head: `aa77c86d5d27a1155fee192d5e2602a1fef30bcd`
- Merge commit: `8266ab94d797d97619fbd2fa2a9c74ec4ea485fd`
- Merge timestamp from GitHub: `2026-10-18T09:03:25Z`
- GitHub records two `APPROVED` review events on PR #11 before merge: `kamilkrasinski4-sys` at `2026-10-18T09:02:35Z` and `Kamil1230xd` at `2026-10-18T09:03:01Z`. The recorded accounts differ from PR author/merger `vaidt`; account-level distinction alone does not establish independent human control or substantive independence. Review links: https://github.com/vaidt/Kt-ry-Program/pull/11#pullrequestreview-5562221365 and https://github.com/vaidt/Kt-ry-Program/pull/11#pullrequestreview-5562222625.
- All nine check-runs read from PR #11's reviewed head show `conclusion=success`; the four required branch-protection contexts completed before the merge timestamp. Current post-merge checks also succeeded on the resulting merge commit. These facts demonstrate CI/review events and current protection state, but do not independently identify the merge path or supply the missing disable/restore event times.

**Disposition:** PA-02 is supported for the current observed state. PA-07 and the historical exception sequence remain partially evidenced. `NC-ASIG-2026-10-17-PR10` remains **OPEN**.
