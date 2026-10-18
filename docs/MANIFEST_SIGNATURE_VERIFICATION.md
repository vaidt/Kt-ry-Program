# ASIG Manifest Signature and Canonicalization Contract

**Status:** Engineering control; subject to normal pull-request review.  
**Protocol effect:** None.

## Backward compatibility

Manifests created before this change omit the optional `canonicalization` field and continue to use the current ASIG encoding:
`json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)`.

The default `capture` mode stays `asig-v1`, preserving historical manifest bytes and hashes. To opt in to RFC 8785/JCS, install `python -m pip install ".[canonical]"` and run `capture --canonicalization rfc8785`. Such manifests record `canonicalization: RFC8785_JCS`, and both manifest and source-tree hashes use JCS.

JCS mode does not silently fall back if the optional encoder is missing. An automatic encoder switch based on package availability would make hashes environment-dependent. The historical encoder is the explicit default/fallback mode. Neither encoding is Aura Protocol canonical serialization.

## Detached signature contract

Cosign and GitHub artifact attestations authenticate the exact file bytes of the manifest. Signature material is stored separately:

- Cosign: a Sigstore bundle containing signature, certificate, and transparency-log proof.
- GitHub attestation: DSSE/SLSA attestation verified by GitHub CLI against the manifest digest.

Do not embed signature metadata into the hashed manifest body: it changes the hash input and conflates source metadata with the signature envelope.

## Signature states

| `signature_status` | Meaning | Result policy |
|---|---|---|
| `valid` | Cryptographic and configured signer-identity checks passed | Preserves source result; source mismatch remains `MISMATCH` |
| `missing` | No bundle supplied or no matching attestation found | Optional: preserve old result. Required: `UNKNOWN`, unless source independently mismatches |
| `invalid` | Signature or signer identity failed verification | `MISMATCH` |
| `unverifiable` | Verifier, configuration, runtime, or trust service unavailable | `UNKNOWN`, unless source independently mismatches |

Existing source status values remain `EXACT_MATCH`, `MISMATCH`, and `UNKNOWN`. The result also contains `source_status`, `signature_policy`, `signature_status`, `signature_valid`, and `signature_backend`. Missing/unverifiable does not mean a cryptographically invalid signature.

When passed to `qualify`, `UNKNOWN` blocks qualification and `MISMATCH` becomes a failure. A valid signature does not establish independent human review, protocol conformance, legal authorization, or production readiness.

## CLI examples

Cosign keyless bundle:

```sh
aura-source-identity verify \
  --root . --manifest ../asig-manifest.json --require-signature \
  --signature-bundle ../asig-manifest.sigstore.json \
  --certificate-identity 'https://github.com/OWNER/REPO/.github/workflows/manifest-sign-verify.yml@refs/heads/main' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

GitHub DSSE/SLSA artifact attestation:

```sh
aura-source-identity verify \
  --root . --manifest ../asig-manifest.json --require-signature \
  --signature-backend github-attestation \
  --attestation-repository OWNER/REPO \
  --attestation-signer-workflow OWNER/REPO/.github/workflows/manifest-sign-verify.yml
```

The GitHub backend requires `gh` plus permission to read attestations; set `GH_TOKEN` in GitHub Actions. Cosign verification requires an expected signer identity and OIDC issuer. A bundle alone does not establish who is trusted.

## Workflow

`.github/workflows/manifest-sign-verify.yml` captures a JCS manifest outside the measured checkout, signs it with keyless Cosign, verifies the bundle against an exact workflow identity, generates a GitHub artifact attestation, verifies the DSSE/SLSA attestation, and uploads the manifest and reports for 14 days. It runs only from `main` so an untrusted pull request cannot receive OIDC signing authority.

## Evidence limits

A valid signature proves that exact bytes were signed under a cryptographic identity meeting the verifier policy. It does not prove the source code is correct, every code path was exercised, the runner was uncompromised, the signer is a legally identified person, independent human review occurred, or an AURA governance gate was ratified.
