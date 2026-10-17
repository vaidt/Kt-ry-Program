# AURA Adoption Map

Status: staged rollout proposal. ASIG main contains the read-only Aura-Guard pilot workflow and runtime adapter prototypes. **Read-only source-identity gate: PASS** for [latest workflow run 39036521844](https://github.com/vaidt/Kt-ry-Program/actions/runs/39036521844), ASIG commit `595ad8896febf1b9064959a16fb86f58eff64dbb`. The [evidence artifact](https://github.com/vaidt/Kt-ry-Program/actions/runs/39036521844/artifacts/12101808651) has SHA-256 `cf67d4ce84f07e7f39e34e2f8d754e5bc45632a92c6ed6e2b0893a9ecfb50f79`; its signed evidence archive has SHA-256 `af4dc7eb880065397206d452519e0f1a7fd8241e1ccc87d2c9e6fadc1e9a4de3`. Independent review confirmed target repository ID `1367018150`, pinned target commit `7d2f5746ae61a66edcd11d75bff0787bed854363`, tree `3269eb54922ae928054a67b98498c2c304876210`, 152 file entries, manifest digest `ea5807106e1139e10c3acffc04bef5af3b5420b985ea7768047e05f9ec110a48`, receipt self-digest `24f5407d241e8555ee90ad54423be7e329d3df07058839537a007ecd1acd9c38`, SHA-256 sums, DSSE signature, signer certificate chain, and Rekor checkpoint/inclusion proof. Verified transparency timestamp: `2026-10-17T13:26:07Z`. This is source-identity evidence only; it claims no target runtime/test execution, runtime identity, protocol conformance, or governance closure. RI-PY, RI-RS, release gates, and branch-protection changes remain separately blocked. No target repository mutation is authorized or performed by this stage.

## Intended integration role

ASIG runs beside Aura-Guard, RI-PY, and RI-RS as an engineering control. It provides source/build/test identity evidence for release engineering. It must not replace the Conformance Core or redefine protocol semantics.

## Current controls

| Risk | ASIG control | Current strength / gap |
|---|---|---|
| Wrong or modified checkout | Git commit/tree, clean-tree check, tracked source inventory, SHA-256 manifest | Implemented and covered by unit tests |
| Receipt content altered | Manifest/receipt self-digest plus GitHub Artifact Attestation on the complete evidence archive | GitHub Artifact Attestation covers the complete evidence archive; signer identity, workflow, certificate chain, and transparency-log proof must be independently verified |
| Tests imported a different Python file | Cooperative Python loader records actual loaded bytes and expected file digest | Unit-tested; limited to configured file-backed modules and cooperative execution |
| Node imported a different module | Explicit CommonJS and ESM specifier hooks | Identity hooks have unit tests; no test-suite completeness adapter yet |
| Rust source/build identity | Git/source manifest plus Cargo/toolchain context receipt | Does not yet prove runtime machine-code identity |
| Partial test suite presented as full suite | Exact required versus observed pytest node IDs | Python adapter only; Node/Rust test-runner integrations remain open |
| Delivered artefact differs from evaluated artefact | Existing supplied evidence qualifier compares delivered/tested hashes | Still requires an authenticated, immutable artifact handoff from independent evaluator |

## Staged rollout

1. **ASIG standalone CI** — run unit and mutation tests for the source identity and adapter receipts.
2. **Aura-Guard read-only source pilot** — inventory only, write output outside target checkout, sign the receipt in the ASIG repository workflow. Do not alter Aura-Guard.
3. **Review the signed pilot** — **PASS for run `39036521844` only**; the evidence package is recorded and independently reviewed above. Earlier run `39035764160` was separately verified, but the latest run supersedes it as the current recorded result. Every later run or target snapshot requires its own verification. If the workflow or evidence fails, stop; absence is not PASS.
4. **RI-PY source inventory — PASS; runtime qualification — BLOCKED** — the pinned snapshot and signed source inventory are reviewed below. Runtime work still requires separate human/governance authorization, an approved required-test list, and explicit source/evidence bindings.
5. **RI-RS source inventory — PASS; runtime qualification — BLOCKED** — the pinned snapshot and signed source inventory are reviewed below. Runtime work still requires separate human/governance authorization and a validated toolchain/binary/test-harness binding.
6. **Mutation and independent review** — test wrong-source imports, incomplete IDs, altered manifests, changed artifacts, and invalid/missing attestations.
7. **Only then consider a required release gate** — requires Architecture Review, repository-specific authorization, protected branch settings, and verification instructions.

## Non-goals

- ASIG does not make an implementation Aura-conformant.
- ASIG cannot resolve governance or ratification gaps in Aura specification.
- A source manifest digest alone is not a signature or origin-authentication proof.
- A signed source-audit receipt is not proof that target tests passed.
- ASIG PASS does not imply protocol-level PASS.


## RI-PY / RI-RS source inventory — reviewed result

**Decision: PASS — pinned read-only source identity and evidence provenance only.** Workflow run [39037323404](https://github.com/vaidt/Kt-ry-Program/actions/runs/39037323404) ran from ASIG commit `130385746c77538eeeb7601877b1b0b966afa421`. The [artifact](https://github.com/vaidt/Kt-ry-Program/actions/runs/39037323404/artifacts/12103100176) ZIP SHA-256 is `14759aa1b36c5a18654b6b5f9b29a8b3c921a55bf3ad1df115636c6e61a045c7`; the signed evidence archive SHA-256 is `031b9a2736f6eed4dc7498c710387021d100a3e8f6fc92284779870b5068e9c5`.

| Target | Repository ID | Pinned commit | Git tree | Inventory entries | Manifest SHA-256 | Receipt self-digest |
|---|---:|---|---|---:|---|---|
| RI-PY — `vaidt/aura-poc-a-core-v3.3` | 1414456591 | `1d15ecbed8470476684951e9ff301a3cfc26a46d` | `2ada7e80083defab47cea18a2bd81d228685a9e0` | 194 | `bb5ba2d2723d65021f82e18fbc3311ee67808930553f5acce510d1a28f81ffb8` | `570c7b7af35d0f3f7877e5027d246d4dc9be33104ca434b258ca1ebdad4dcc66` |
| RI-RS — `vaidt/aura-guard-v1.3` | 1378273687 | `e0ed7a8b381b725fe65bd86716894bfdf17d3a94` | `67e2fc417cf6e2ecf0110e8684db2522d8149071` | 136 | `03fc5c6cb43a79dca338f7a3b67c75054c0cd5812a21e67d5fab03659bc84955` | `085f07af732876b8a61e836fa03003bf1a0810da1c6b64ae64996b972258ea9d` |

Independent evidence checks completed for this run:
1. The downloaded artifact's SHA-256 matches GitHub's artifact metadata. Every entry in `SHA256SUMS` matches, and all six data files inside the signed TAR archive are byte-identical to their outer artifact copies.
2. The deterministic ASIG manifest and receipt self-digests recompute exactly. Each receipt binds the expected repository identifier, requested pinned commit, Git tree, file count, manifest digest, and clean working tree.
3. The target commits resolve through GitHub to the stated tree SHAs. Each tree's blob count matches the source inventory count: 194 RI-PY and 136 RI-RS.
4. The DSSE signature verifies using the embedded Fulcio leaf certificate. The leaf-to-intermediate and intermediate-to-root certificate signatures verify against the published Sigstore trusted root; the leaf identity is `vaidt/Kt-ry-Program/.github/workflows/read-only-reference-source-inventory.yml@refs/heads/main`, source repository ID `1423292837`.
5. The signed Rekor checkpoint verifies using the active published Rekor key. The inclusion proof for the canonicalized transparency-log entry recomputes to the checkpoint root. Sigstore's bundle schema distinguishes the global `logIndex` from the shard-local `inclusionProof.logIndex`; those values are therefore not expected to be identical. The verified transparency timestamp is `2026-10-17T13:37:37Z`.
6. The attestation subject digest equals the SHA-256 of the signed evidence archive. Its provenance statement binds the ASIG run `39037323404` and source commit `130385746c77538eeeb7601877b1b0b966afa421`.

The published trust-root file used for this independent verification is [Sigstore trusted_root.json](https://github.com/sigstore/root-signing/blob/main/targets/trusted_root.json), Git blob SHA `effb0a19e6a0b3f69b3f0a2c72b5c2a02a0ddeea`.

**Strict scope boundary:** both results prove source inventory identity and evidence provenance only. Neither target test suite, build, nor runtime was executed. Context explicitly records `runtime_tests_executed=false`, `runtime_identity_observed=false`, `runtime_qualification_status=BLOCKED`, `protocol_conformance_claimed=false`, and `release_gate_authorized=false`. DQ-006 / DQ6-R4 is not ratified or resolved by this work. No files were changed in either target repository.
