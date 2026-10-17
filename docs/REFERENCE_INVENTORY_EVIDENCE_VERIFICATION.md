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

---

## Post-merge verification addendum — run 39038179646

**Review date:** 2026-10-17  
**Disposition:** **PASS — source inventory integrity and provenance only.**  
**Runtime qualification:** **BLOCKED.** **Protocol conformance:** **NOT CLAIMED.** **Release gate:** **NOT AUTHORIZED.**

### Run and artifact binding

| Field | Verified value |
|---|---|
| Repository | `vaidt/Kt-ry-Program` (repository ID `1423292837`) |
| Workflow | `.github/workflows/read-only-reference-source-inventory.yml` |
| Workflow run | [39038179646](https://github.com/vaidt/Kt-ry-Program/actions/runs/39038179646) |
| Run conclusion | `success` |
| ASIG commit / workflow commit | `0c50927f85bbee62cee84d0f099d1a220351daf0` |
| Ref | `refs/heads/main` |
| Artifact | [asig-reference-source-inventory-39038179646](https://github.com/vaidt/Kt-ry-Program/actions/runs/39038179646/artifacts/12102634225) |
| Artifact ID | `12102634225` |
| Artifact size | `61,105 bytes` |
| Downloaded GitHub Actions artifact ZIP SHA-256 | `da72aba23558e5f6abbf0716ade226e926bfab9894fa1c845fb0bcbe3bf58391` |
| Signed archive SHA-256 | `db566b3f576826f01e230fe0a2a8a28ebbc618a1fbcac99050efb14ac840fde4` |
| Sigstore bundle SHA-256 | `d77633636c7bea3564867d24a3b8953d71eedac70e54a3521eed6bb9153967b4` |

The independently downloaded artifact ZIP digest matches the GitHub artifact metadata for artifact ID `12102634225`.

### CI result for the merged commit

All five post-merge checks associated with commit `0c50927f85bbee62cee84d0f099d1a220351daf0` completed with conclusion `success` in [workflow run 39038179621](https://github.com/vaidt/Kt-ry-Program/actions/runs/39038179621):

- `test-and-build (3.11)`
- `test-and-build (3.12)`
- `test-and-build (3.13)`
- `runtime-adapter-integration`
- `inventory-reference-sources`

These CI results establish successful completion of those workflows only; they do not expand the source-inventory evidence scope stated below.

### Independent checksum and self-digest verification

| Check | Result | Recorded digest / evidence |
|---|---|---|
| Artifact ZIP SHA-256 versus GitHub metadata | **PASS** | `da72aba23558e5f6abbf0716ade226e926bfab9894fa1c845fb0bcbe3bf58391` |
| Entries listed in `asig-reference-inventory-SHA256SUMS.txt` | **5/5 PASS** | All five listed file digests matched the extracted files |
| RI-PY manifest canonical JSON self-digest | **PASS** | `bb5ba2d2723d65021f82e18fbc3311ee67808930553f5acce510d1a28f81ffb8` |
| RI-RS manifest canonical JSON self-digest | **PASS** | `03fc5c6cb43a79dca338f7a3b67c75054c0cd5812a21e67d5fab03659bc84955` |
| RI-PY receipt canonical JSON self-digest | **PASS** | `fdd33a3353a0fd76f86f418b66eea2892ccfdc033d656b99eeceaf6574c9f65e` |
| RI-RS receipt canonical JSON self-digest | **PASS** | `40a807d07e74274866cd51194357d0d2850b7a9923326cfa13705e6e3cfeb1de` |

### Frozen source targets

| Field | RI-PY | RI-RS |
|---|---|---|
| Repository | `vaidt/aura-poc-a-core-v3.3` | `vaidt/aura-guard-v1.3` |
| Repository ID | `1414456591` | `1378273687` |
| Pinned commit | `1d15ecbed8470476684951e9ff301a3cfc26a46d` | `e0ed7a8b381b725fe65bd86716894bfdf17d3a94` |
| Pinned Git tree | `2ada7e80083defab47cea18a2bd81d228685a9e0` | `67e2fc417cf6e2ecf0110e8684db2522d8149071` |
| Inventory entry count | 194 | 136 |
| Source identity disposition | `EXACT_MATCH` | `EXACT_MATCH` |

The recomputed manifest and receipt self-digests matched their recorded digest fields. The independently checked inventory records bind these exact pinned repository commits and tree identifiers; they are not assertions about subsequent repository states.

### Sigstore identity verification and provenance

Independent Sigstore CLI identity verification of the signed archive against the bundle completed with **exit code 0** using this workflow certificate identity and OIDC issuer:

```text
certificate identity:
https://github.com/vaidt/Kt-ry-Program/.github/workflows/read-only-reference-source-inventory.yml@refs/heads/main

OIDC issuer:
https://token.actions.githubusercontent.com

signed archive:
asig-reference-source-inventory.tar.gz

signed archive SHA-256:
db566b3f576826f01e230fe0a2a8a28ebbc618a1fbcac99050efb14ac840fde4

verification result:
PASS (exit code 0)
```

The verified statement binds the archive digest to repository ID `1423292837`, workflow path `.github/workflows/read-only-reference-source-inventory.yml`, workflow ref `refs/heads/main`, workflow commit `0c50927f85bbee62cee84d0f099d1a220351daf0`, and run invocation `39038179646`. The verified transparency timestamp was `2026-10-17T13:50:11Z`.

The bundle records Rekor global log index `3295739294`, shard-local inclusion-proof index `3173835032`, and proof tree size `3173835185`. Global and shard-local index values are distinct index domains; their inequality alone is not a verification failure. The Sigstore verifier accepted the bundle and expected identity.

### Scope and explicit non-claims

This record is limited to **read-only source inventory, evidence-file integrity, and provenance for the two pinned source snapshots**. The captured context explicitly states:

- `audit_scope = READ_ONLY_SOURCE_INVENTORY_ONLY`
- `runtime_tests_executed = false`
- `runtime_identity_observed = false`
- `protocol_conformance_claimed = false`
- `release_gate_authorized = false`

Accordingly, this addendum does **not** establish that RI-PY or RI-RS runtime tests were executed, that runtime or machine-code identity was observed, that protocol conformance has been demonstrated, that a normative or governance decision has been closed, or that a release gate is authorized. It does not authorize changes to either target repository.

**Disposition:** PASS for the artifact integrity/provenance and read-only source-inventory scope of run `39038179646` and these exact pinned snapshots. Runtime qualification and release-gate adoption remain **BLOCKED** pending their separate authorization and reviewed test/toolchain bindings. Each later run or changed target pin requires its own evidence review.

---

## CAPA follow-up — deviation and reproducible verification evidence

On 2026-10-17, PR #10 was merged with no submitted GitHub review recorded. The deviation is registered as `NC-ASIG-2026-10-17-PR10` in [`docs/COMPLIANCE_DEVIATIONS.md`](COMPLIANCE_DEVIATIONS.md). This finding is not waived by CI success.

The complete five-entry artifact checksum list is preserved in [`docs/evidence/ASIG_RUN_39038179646_SHA256SUMS.txt`](evidence/ASIG_RUN_39038179646_SHA256SUMS.txt). Timestamped output excerpts returned by the original GitHub Actions job—including the original SHA256 verification output and `gh attestation verify` command/result—are preserved in [`docs/evidence/ASIG_RUN_39038179646_SIGSTORE_CHECKSUM_RAW.log`](evidence/ASIG_RUN_39038179646_SIGSTORE_CHECKSUM_RAW.log).

| Evidence object | SHA-256 |
|---|---|
| GitHub Actions artifact ZIP, ID `12102634225` | `da72aba23558e5f6abbf0716ade226e926bfab9894fa1c845fb0bcbe3bf58391` |
| Signed archive `asig-reference-source-inventory.tar.gz` | `db566b3f576826f01e230fe0a2a8a28ebbc618a1fbcac99050efb14ac840fde4` |
| Sigstore bundle `attestation.json` | `d77633636c7bea3564867d24a3b8953d71eedac70e54a3521eed6bb9153967b4` |
| Attestation verification JSON | `149a13e2ea61906b7572e5bc82243dc1460742b7ebcfedf9258497a9313027f9` |

The source workflow run and original evidence artifact remain linked from the raw-log record. The verification excerpt records the command used, signer workflow identity and the workflow's PASS summary. These are source-inventory integrity/provenance claims only; they do not establish runtime test execution, runtime identity, protocol conformance, or release authorization.

**CAPA status:** OPEN pending an independent approving review and successful required checks on the remediation PR. This addendum is documentary evidence, not a retroactive approval of PR #10.

