# RI-PY / RI-RS Source Inventory: Independent Evidence Review

**Decision: PASS — source identity and evidence provenance only.**  
**Runtime qualification: BLOCKED. Protocol conformance: NOT CLAIMED. Release gate: NOT AUTHORIZED.**

Review date: 2026-10-17  
Repository: `vaidt/Kt-ry-Program`  
Workflow: `.github/workflows/read-only-reference-source-inventory.yml`  
Workflow run: [39037323404](https://github.com/vaidt/Kt-ry-Program/actions/runs/39037323404)  
ASIG commit: `130385746c77538eeeb7601877b1b0b966afa421`  
Artifact: [asig-reference-source-inventory-39037323404](https://github.com/vaidt/Kt-ry-Program/actions/runs/39037323404/artifacts/12103100176) (ID `12103100176`, 60,837 bytes)

## Artifact identities

| Object | SHA-256 |
|---|---|
| Downloaded GitHub Actions artifact ZIP | `14759aa1b36c5a18654b6b5f9b29a8b3c921a55bf3ad1df115636c6e61a045c7` |
| Signed evidence archive (`asig-reference-source-inventory.tar.gz`) | `031b9a2736f6eed4dc7498c710387021d100a3e8f6fc92284779870b5068e9c5` |
| Sigstore bundle (`5DtTje/attestation.json`) | `387e3b065533f1f64c142eb6a266cddc66a85b504df4889a6df40af5f2e5c6e0` |

The downloaded ZIP digest matches the digest reported by GitHub for artifact ID `12103100176`. The GitHub Attestations API also returned an attestation whose in-toto subject is the signed evidence archive digest above and whose predicate type is `https://slsa.dev/provenance/v1`.

## Frozen target identities and results

| Field | RI-PY | RI-RS |
|---|---|---|
| Repository | `vaidt/aura-poc-a-core-v3.3` | `vaidt/aura-guard-v1.3` |
| Repository ID | `1414456591` | `1378273687` |
| Pinned commit | `1d15ecbed8470476684951e9ff301a3cfc26a46d` | `e0ed7a8b381b725fe65bd86716894bfdf17d3a94` |
| Pinned Git tree | `2ada7e80083defab47cea18a2bd81d228685a9e0` | `67e2fc417cf6e2ecf0110e8684db2522d8149071` |
| Inventory entries | 194 | 136 |
| Manifest SHA-256 | `bb5ba2d2723d65021f82e18fbc3311ee67808930553f5acce510d1a28f81ffb8` | `03fc5c6cb43a79dca338f7a3b67c75054c0cd5812a21e67d5fab03659bc84955` |
| Receipt SHA-256 | `570c7b7af35d0f3f7877e5027d246d4dc9be33104ca434b258ca1ebdad4dcc66` | `085f07af732876b8a61e836fa03003bf1a0810da1c6b64ae64996b972258ea9d` |
| Source identity | `EXACT_MATCH` | `EXACT_MATCH` |

The target tree identifiers were independently resolved through the GitHub Git Trees API. Each returned tree SHA matches the frozen value above. Each manifest's commit/tree fields match its receipt's target commit/tree fields.

## Independent checks performed

1. Downloaded artifact ZIP SHA-256 matches GitHub artifact metadata.
2. All five entries in `asig-reference-inventory-SHA256SUMS.txt` match their extracted files. The evidence tar archive contains the expected two manifests, two receipts, context document, and checksum file.
3. Recomputed ASIG canonical JSON self-digests for both manifests and both receipts. All four computed values match their recorded digest fields.
4. Confirmed the context binds the ASIG repository ID (`1423292837`), workflow run (`39037323404`), ASIG commit/ref, target repository IDs, target commits/trees, and corresponding manifest/receipt digests.
5. Independently ran Sigstore CLI identity verification against the downloaded signed archive and bundle. The command exited with code `0` using the expected workflow identity and OIDC issuer:

   ```sh
   sigstore verify identity \
     --bundle 5DtTje/attestation.json \
     --cert-identity 'https://github.com/vaidt/Kt-ry-Program/.github/workflows/read-only-reference-source-inventory.yml@refs/heads/main' \
     --cert-oidc-issuer 'https://token.actions.githubusercontent.com' \
     asig-reference-source-inventory.tar.gz
   ```

6. Confirmed the attestation statement identifies the expected archive SHA-256, predicate type, ASIG repository, workflow path, workflow commit `130385746c77538eeeb7601877b1b0b966afa421`, `refs/heads/main`, and run invocation `39037323404`.
7. The verifier output records a verified transparency timestamp of `2026-10-17T13:37:37Z`.

### Rekor index interpretation

The bundle contains global `tlogEntries[].logIndex = 3295634579` and shard-local `inclusionProof.logIndex = 3173730317`, with proof tree size `3173730332`. **Inequality between those two index fields is not, by itself, a proof failure.** Sigstore's Rekor sharding documentation distinguishes global log indices from indices within a specific shard/tree. The independent Sigstore verifier accepted the bundle and verified the expected identity. Reviewers must validate the proof using the format's defined index semantics rather than assert that the global and shard-local indices are equal.

References:
- https://docs.sigstore.dev/logging/sharding/
- https://github.com/sigstore/architecture-docs/blob/main/rekor-spec.md

## Scope boundary

The result establishes integrity and provenance for the captured source-inventory evidence for these two frozen commits. It does **not** establish:

- execution of RI-PY or RI-RS tests;
- runtime identity or machine-code identity;
- test-suite completeness;
- Aura Protocol conformance or closure of any normative/governance decision;
- authorization to modify either target repository;
- authorization to enable a required release gate or change branch protection.

The receipts and context explicitly record `runtime_tests_executed = false`, `runtime_identity_observed = false`, `protocol_conformance_claimed = false`, `runtime_qualification_status = BLOCKED`, and `release_gate_authorized = false`.

**Disposition:** source-inventory evidence is PASS for this run and these exact pinned snapshots. RI-PY/RI-RS runtime qualification and release-gate adoption remain BLOCKED pending their separate authorization and reviewed test/toolchain bindings. A later run or changed target pin requires a new evidence review.
