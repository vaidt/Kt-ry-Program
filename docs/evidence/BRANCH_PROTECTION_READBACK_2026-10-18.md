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
- The original JPEG bytes are not embedded in this Markdown record. The available GitHub connector supports UTF-8 text file writes only; it could not upload the binary screenshot. Consequently, this file is a transcription/index with a source-byte fingerprint, **not a substitute for the original screenshot**. The raw JPEG must still be added to the repository at `docs/evidence/BRANCH_PROTECTION_READBACK_2026-10-18.jpeg` and its committed bytes re-hashed to complete repository-side preservation. Until then, the image is preserved only as the conversation attachment plus the fingerprint above.

## Evidentiary limitations

1. This is a point-in-time read-back. It establishes that `enforce_admins.enabled` was `true` when the displayed query was executed.
2. It does not establish when the setting was last changed, whether it was temporarily disabled for PR #11, or the UTC time at which it may have been restored.
3. The authorization text in PR #11 is not evidence that every step of the prescribed break-glass sequence actually occurred.
4. The result does not establish legal identity or whether distinct GitHub accounts are controlled by distinct humans.
5. It does not establish runtime qualification, protocol conformance, release readiness, or CAPA closure.

## Related pull request sequence

- PR #11: https://github.com/vaidt/Kt-ry-Program/pull/11
- Reviewed head: `aa77c86d5d27a1155fee192d5e2602a1fef30bcd`
- Merge commit: `8266ab94d797d97619fbd2fa2a9c74ec4ea485fd`
- Merge timestamp from GitHub: `2026-10-18T09:03:25Z`
- GitHub records two `APPROVED` review events on PR #11 before merge: `kamilkrasinski4-sys` at `2026-10-18T09:02:35Z` and `Kamil1230xd` at `2026-10-18T09:03:01Z`. The recorded accounts differ from PR author/merger `vaidt`; account-level distinction alone does not establish independent human control or substantive independence. Review links: https://github.com/vaidt/Kt-ry-Program/pull/11#pullrequestreview-5562221365 and https://github.com/vaidt/Kt-ry-Program/pull/11#pullrequestreview-5562222625.
- All nine check-runs read from PR #11's reviewed head show `conclusion=success`; the four required branch-protection contexts completed before the merge timestamp. Current post-merge checks also succeeded on the resulting merge commit. These facts demonstrate CI/review events and current protection state, but do not independently identify the merge path or supply the missing disable/restore event times.

**Disposition:** PA-02 is supported for the current observed state. PA-07 and the historical exception sequence remain partially evidenced. `NC-ASIG-2026-10-17-PR10` remains **OPEN**.
