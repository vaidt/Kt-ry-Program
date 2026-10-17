# ASIG SLSA Artifact-Attestation Validation Record

**Record ID:** ASIG-VAL-ATT-001  
**Date:** 2026-10-17  
**Status:** TECHNICAL VALIDATION PASS · VALIDATION ONLY  
**Repository:** `vaidt/Kt-ry-Program`  
**Evidence branch:** `validation/attestation-negative-control` (deleted after capture)  
**Governance branch:** `infra/ci-updates`  
**Authorization boundary:** This is a bounded test of artifact provenance and digest verification. It is not release approval and does not authorize Stage 3, promotion, or experimental merges.

## 1. Objective

Prove that a GitHub Actions workflow can build a synthetic R&D test artifact, issue signed SLSA build provenance via GitHub Artifact Attestations / Sigstore, upload the artifact and bundle, and independently verify the downloaded bytes using GitHub CLI with explicit repository, signer-workflow, source-ref, source-commit, and predicate constraints.

The flow also includes a tamper negative control: a modified copy of the subject must not verify against the original attestation.

## 2. Isolated test source

| Field | Observed value |
|---|---|
| Validation workflow | `.github/workflows/attestation-validation.yml` |
| Tested commit SHA | `b2e7f1b72a80b0140649c0236eabbc051e925ab5` |
| Source tree | Recorded in the signed build fixture manifest and provenance statement |
| Source ref at signing | `refs/heads/validation/attestation-negative-control` |
| GitHub repository ID | `1423292837` |
| GitHub owner ID | `321871992` |
| Attestation action | `actions/attest-build-provenance` v3.2.0 |
| Attestation action pin | `96278af6caaf10aea03fd8d33a09a777ca52d62f` |
| Checkout action pin | `actions/checkout` commit `11bd71901bbe5b1630ceea73d27597364c9af683` |
| Upload action pin | `actions/upload-artifact` commit `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| Download action pin | `actions/download-artifact` commit `d3f86a106a0bac45b974a628896c90dbdf5c8093` |

The synthetic archive contains metadata identifying the repository, source ref/commit/tree, workflow path and SHA, run identity, and test-only disposition. It is not a product build and is not for distribution.

## 3. Workflow run and artifact retention

- [ASIG SLSA Attestation Validation — run 39051752235](https://github.com/vaidt/Kt-ry-Program/actions/runs/39051752235): overall **SUCCESS**.
- Job `build-and-attest`: **SUCCESS** — exact source identity checked, synthetic archive built, SLSA provenance attested, and evidence uploaded.
- Job `verify-out-of-band`: **SUCCESS** — artifact downloaded to a separate GitHub-hosted runner, checksummed, cryptographically verified with GitHub CLI, and checked for certificate/source/digest identity.
- [Build artifact and Sigstore bundle — artifact ID 12107712455](https://github.com/vaidt/Kt-ry-Program/actions/runs/39051752235/artifacts/12107712455), size 8,282 bytes, expiry `2026-10-24T16:59:09Z`.
- [Raw verification evidence — artifact ID 12108195314](https://github.com/vaidt/Kt-ry-Program/actions/runs/39051752235/artifacts/12108195314), size 18,536 bytes, expiry `2026-10-24T16:59:25Z`. Contains the raw `gh attestation verify --format json` output, CLI version, command record, checksum manifest, Sigstore bundle, tamper-control output, and related files.

The workflow artifacts intentionally have a seven-day retention for this validation environment. The Actions run and its job logs are separately linked above. Do not rely on the short-lived artifacts as the sole long-term record; this Markdown record preserves the primary outputs and digests.

## 4. Exact GitHub CLI verification

The verification job used GitHub-hosted runner separate from the build-and-attest job. The downloaded subject was verified with:

```sh
gh version
# gh version 2.102.0 (2026-09-30)

gh attestation verify asig-slsa-validation.tar.gz \
  --repo vaidt/Kt-ry-Program \
  --signer-workflow vaidt/Kt-ry-Program/.github/workflows/attestation-validation.yml \
  --source-digest b2e7f1b72a80b0140649c0236eabbc051e925ab5 \
  --source-ref refs/heads/validation/attestation-negative-control \
  --predicate-type https://slsa.dev/provenance/v1 \
  --format json
```


### Raw verification result

The workflow log recorded the following lines after the CLI returned exit code 0:

```text
gh version 2.102.0 (2026-09-30)
GH_ATTESTATION_VERIFY_EXIT=0
ATTESTATION_CRYPTOGRAPHIC_VERIFICATION=PASS
SIGNER_REPOSITORY_ID=1423292837
VERIFIED_TIMESTAMP_COUNT=1
PREDICATE_TYPE=https://slsa.dev/provenance/v1
SUBJECT_NAME=asig-slsa-validation.tar.gz
LOCAL_ARTIFACT_SHA256=1483325b7a4fd3829bd347222101002b54a07a70a62d66ae6316682df0cec9d9
ATTESTED_SUBJECT_SHA256=1483325b7a4fd3829bd347222101002b54a07a70a62d66ae6316682df0cec9d9
SIGNER_WORKFLOW_CONSTRAINT=PASS (enforced by gh attestation verify --signer-workflow)
SOURCE_COMMIT_CONSTRAINT=PASS (enforced by --source-digest)
SOURCE_REF_CONSTRAINT=PASS (enforced by --source-ref)
```

The computed SHA-256 of the downloaded file and the attested subject digest are identical:

`1483325b7a4fd3829bd347222101002b54a07a70a62d66ae6316682df0cec9d9`

### Verified certificate and provenance fields

The raw JSON emitted by `gh attestation verify` contained these verified certificate/provenance fields:

| Field | Verified value |
|---|---|
| Predicate type | `https://slsa.dev/provenance/v1` |
| Source repository | `https://github.com/vaidt/Kt-ry-Program` |
| Source repository ID | `1423292837` |
| Source owner ID | `321871992` |
| OIDC issuer | `https://token.actions.githubusercontent.com` |
| Sigstore certificate issuer | `CN=sigstore-intermediate,O=sigstore.dev` |
| Certificate subject alternative name | `https://github.com/vaidt/Kt-ry-Program/.github/workflows/attestation-validation.yml@refs/heads/validation/attestation-negative-control` |
| Workflow identity | `ASIG SLSA Attestation Validation` |
| Workflow path | `.github/workflows/attestation-validation.yml` |
| Workflow ref | `refs/heads/validation/attestation-negative-control` |
| Workflow/source SHA | `b2e7f1b72a80b0140649c0236eabbc051e925ab5` |
| Trigger | `push` |
| Runner | `github-hosted` |
| Verified transparency timestamp | Rekor at `2026-10-17T16:59:08Z` |
| Run invocation | [run 39051752235, attempt 1](https://github.com/vaidt/Kt-ry-Program/actions/runs/39051752235/attempts/1) |

The command constrained `--repo`, `--signer-workflow`, `--source-digest`, `--source-ref`, and `--predicate-type`; successful CLI exit plus the parsed certificate and digest assertions are captured in the verifier job log.

## 5. Tamper negative control

The verifier copied the original archive, appended bytes (`tamper-probe`), then ran the same constrained `gh attestation verify` command against the modified file.

Observed output:

```text
TAMPER_NEGATIVE_CONTROL=PASS: modified bytes rejected by gh attestation verify (exit=1)
Error: HTTP 404: Not Found
```

The lookup was for the altered subject digest `sha256:6fa2922e84210a7c6690d08b58e18f8f6c34ce7e212f9346117cf467bcbf183d`. The rejection occurred because no attestation matched those altered bytes. This is the expected integrity-binding negative result, not a test of whether a malicious attestation could be issued by a compromised workflow.

## 6. PR disposition and test-ref cleanup

- [PR #18 — SLSA provenance validation](https://github.com/vaidt/Kt-ry-Program/pull/18): **CLOSED WITHOUT MERGE**; `merged = false`, `merged_at = null`.
- Before closure, the PR API reported `mergeable_state = clean`. This validation was not intended to demonstrate merge blocking, and no claim of such a block is made.
- The PR base `integration` remained at `487e63069d18d2ab3f289131e9a5427f0cc61116`.
- The source ref `refs/heads/validation/attestation-negative-control` at tested SHA `b2e7f1b72a80b0140649c0236eabbc051e925ab5` was deleted after preserving the run/artifact/PR evidence.
- Subsequent GitHub REST ref lookup returned HTTP 404 `Not Found`; a branch inventory of up to 100 refs contained no matching `validation/attestation-negative-control` entry.
- `main` remained at `8b62cca211cd8969040aa90ac501db5fa6649bca`; `integration` remained at `487e63069d18d2ab3f289131e9a5427f0cc61116`.

## 7. Scope limits and disposition

**Gate 4 technical validation: PASS for the synthetic artifact flow.**

This evidence proves that the test workflow generated a SLSA v1 provenance attestation, that the uploaded subject verified in a separate runner with constrained signer/source inputs, that the local and attested digests match, that a verified timestamp exists, and that altered bytes do not match the attested subject.

It does **not** prove that the repository's real sdist/wheel/release output is currently attested, that all production build inputs are trustworthy, that the build is hermetic or SLSA Build Level 3 compliant, that source code is correct, or that AURA protocol conformance is established. The validation workflow is isolated on the deleted test branch and was not merged to `integration` or `main`.

**Program status remains:** `VALIDATION ONLY · NOT ACTIVE FOR EXPERIMENTAL MERGES`.  
**Stage 3:** NOT AUTHORIZED.  
The evidence closes only the synthetic-artifact attestation validation item; it does not itself authorize synchronization to `integration` or a change to the program's governing status.
