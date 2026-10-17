# ASIG Aura-Guard Pilot: Independent Evidence Verification

Status: PENDING execution and independent review.

Target repository: `vaidt/Aura-Guard`
Target commit: `7d2f5746ae61a66edcd11d75bff0787bed854363`
ASIG repository ID: `1423292837`
Attesting workflow: `.github/workflows/read-only-aura-guard-pilot.yml`
Expected predicate: `https://slsa.dev/provenance/v1`

## Required review

1. Download and preserve the workflow artifact ZIP from the completed ASIG Actions run.
2. Require the source manifest, receipt, pilot context, checksum list, evidence archive, attestation bundle, and verifier output. Missing files mean BLOCKED.
3. Extract the evidence archive and run `sha256sum -c asig-aura-guard-SHA256SUMS.txt`. All entries must match.
4. Verify the archive using GitHub CLI's `gh attestation verify` command, the supplied bundle, expected repository `vaidt/Kt-ry-Program`, signer workflow `vaidt/Kt-ry-Program/.github/workflows/read-only-aura-guard-pilot.yml`, and predicate `https://slsa.dev/provenance/v1`. Require verifier success, expected signer identity, certificate repository ID `1423292837`, and a verified timestamp. Offline verification additionally requires a separately obtained trust root.
5. Check receipt `audit_status == PASS` and `source_identity_verification.status == EXACT_MATCH`.
6. Confirm both receipt and manifest identify target commit `7d2f5746ae61a66edcd11d75bff0787bed854363`; receipt tree equals manifest `git.tree_sha`; manifest `working_tree_clean == true`; receipt self-digest validates; and the receipt manifest digest equals manifest `manifest_sha256`.
7. Confirm context binds target commit/tree, manifest and receipt digests, ASIG repository ID, workflow run, and ASIG source commit.
8. Confirm scope fields remain false: `protocol_conformance_claimed`, `runtime_tests_executed`, and `runtime_identity_observed`.

## Classification

- PASS: signature, timestamp, signer, exact target identity, checksums, receipt, and scope all validate.
- FAIL: hash mismatch, unexpected commit/tree, invalid signature, wrong signer, or target content change.
- BLOCKED: missing evidence, absent certificate/timestamp, unavailable trust material, interrupted workflow, or unresolved checks.

Until a reviewer records PASS, RI-PY and RI-RS pilots, required release-gate adoption, and branch-protection changes remain blocked. An attestation authenticates the evidence package and workflow provenance; it does not prove code quality or AURA protocol conformance.
