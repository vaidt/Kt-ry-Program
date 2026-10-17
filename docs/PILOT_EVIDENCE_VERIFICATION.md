# ASIG Aura-Guard Pilot: Independent Evidence Verification

Status: Per-run verification procedure. Workflow code alone never establishes PASS. The current recorded decision is in `docs/AURA_ADOPTION_MAP.md`; each subsequent run/artifact requires its own independent review.

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


## Recorded independent review — run 39035764160 (2026-10-17)

**Decision: PASS — ASIG read-only source-identity gate only.** This is not an Aura Protocol conformance decision.

- Workflow run: https://github.com/vaidt/Kt-ry-Program/actions/runs/39035764160
- Artifact: https://github.com/vaidt/Kt-ry-Program/actions/runs/39035764160/artifacts/12102345928
- Artifact ZIP SHA-256: `d0c92f5f31e1efe6da4626df950bd6efc0754a0b44c956b23cb04b18a4695799`
- Signed evidence archive SHA-256: `22e40dfa1e0212796808245610b6a16deffcb6278db53368f7ea2b95bbe9aac3`
- ASIG repository ID / workflow commit: `1423292837` / `d99b0ea07eba660cc3ca90bb145befff0d5fed32`
- Target repository ID / commit / tree: `1367018150` / `7d2f5746ae61a66edcd11d75bff0787bed854363` / `3269eb54922ae928054a67b98498c2c304876210`
- Manifest digest / receipt digest: `ea5807106e1139e10c3acffc04bef5af3b5420b985ea7768047e05f9ec110a48` / `8a909f80cb49f9e0f7ce1ed354ea75140319455c8876f4fe7afb4bc9a65d7370`
- Verified timestamp: `2026-10-17T13:15:01Z`; signer workflow identity: `vaidt/Kt-ry-Program/.github/workflows/read-only-aura-guard-pilot.yml@refs/heads/main`; certificate source repository ID: `1423292837`.

Independent checks completed:
1. Downloaded artifact ZIP SHA-256 matches GitHub artifact metadata; all entries in `SHA256SUMS` validate; duplicate evidence files match their copies inside the signed tar archive.
2. Recomputed ASIG canonical JSON self-digests for the source manifest and receipt; recomputed values match. Context fields correctly bind target repo ID, commit/tree, manifest/receipt digests, ASIG run, and workflow commit.
3. Resolved the target commit through GitHub's Git API: commit tree equals the recorded tree SHA, and the tree lists 152 file blobs, matching the manifest's inventory count.
4. Independently verified the DSSE signature with the embedded leaf certificate's public key; verified the Fulcio leaf→intermediate→root certificate signatures; verified the Rekor checkpoint signature using the published Rekor key; recomputed the Merkle inclusion proof and confirmed it matches the checkpoint root.
5. The attestation statement subject SHA-256 matches the signed evidence archive. The signed statement identifies the expected ASIG repository, workflow path, source commit, run ID, and `https://slsa.dev/provenance/v1` predicate.
6. The recorded receipt/context explicitly set `runtime_tests_executed=false`, `runtime_identity_observed=false`, and `protocol_conformance_claimed=false`.

Trust material was sourced from the public Sigstore root-signing repository: https://github.com/sigstore/root-signing/blob/main/targets/trusted_root.json (Git blob SHA `effb0a19e6a0b3f69b3f0a2c72b5c2a02a0ddeea`). The workflow's `gh attestation verify` step also completed successfully against the expected repository, signer workflow, source digest, and ref.

**Scope boundary:** the result proves identity and integrity of the captured source inventory and evidence provenance only. It does not prove the target code is correct, test-complete, safe, live-runtime-identical, or Aura-conformant. No target files were changed and no target tests/runtime were executed.
