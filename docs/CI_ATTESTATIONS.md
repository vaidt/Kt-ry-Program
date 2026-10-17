# CI Attestations for ASIG Evidence

Status: Engineering preview. This document describes the configured Aura-Guard read-only source audit.

## Flow

1. GitHub Actions checks out `vaidt/Kt-ry-Program` and installs ASIG.
2. A separate checkout reads `vaidt/Aura-Guard@main` with `persist-credentials: false`; no target write token is persisted.
3. ASIG creates a source manifest and a read-only audit receipt in `RUNNER_TEMP`, outside the target repository.
4. The receipt explicitly states that no target tests ran, runtime identity was not observed, and protocol conformance is not claimed.
5. `actions/attest@v4` signs an attestation for the receipt with GitHub's artifact-attestation service. The attestation identifies the ASIG workflow provenance and binds the receipt's digest.
6. The workflow uploads the receipt, manifest, checksums, and attestation bundle for later review.

The workflow requires `contents: read`, `id-token: write`, `attestations: write`, and `artifact-metadata: write`. The OIDC token allows the attestation action to obtain a short-lived signing certificate; the attestation write permissions allow publication to GitHub. See the official [actions/attest documentation](https://github.com/actions/attest) and [GitHub artifact-attestation documentation](https://docs.github.com/en/actions/concepts/security/artifact-attestations).

## Verify

Download the artifact from the ASIG workflow run and run:

```sh
gh attestation verify asig-aura-guard-read-only-receipt.json \
  --repo vaidt/Kt-ry-Program \
  --signer-workflow vaidt/Kt-ry-Program/.github/workflows/read-only-aura-guard-pilot.yml \
  --predicate-type https://github.com/vaidt/Kt-ry-Program/attestations/asig-read-only-source-audit/v1
```

The repository and signer workflow must be constrained, not merely omitted, when the result is used as a trusted release input. Verify the receipt content as well: check target repository, requested ref, commit SHA, Git tree SHA, manifest digest, and the three explicit non-claims.

## Security interpretation

An artifact attestation authenticates the receipt's provenance and links it to the signing workflow; it does not prove that target code is correct. A compromised workflow may produce a false predicate. The workflow is therefore deliberately limited to a verifiable source inventory record, and its output is not treated as a protocol conformance verdict.

Do not sign every routine test log. The current signed receipt is generated for a scheduled or explicitly requested source audit and can be verified independently.
