# AURA Adoption Map

Status: staged rollout proposal. ASIG main contains the read-only Aura-Guard pilot workflow and runtime adapter prototypes. **Read-only source-identity gate: PASS** for [latest workflow run 39036521844](https://github.com/vaidt/Kt-ry-Program/actions/runs/39036521844), ASIG commit `595ad8896febf1b9064959a16fb86f58eff64dbb`. The [evidence artifact](https://github.com/vaidt/Kt-ry-Program/actions/runs/39036521844/artifacts/12101808651) has SHA-256 `cf67d4ce84f07e7f39e34e2f8d754e5bc45632a92c6ed6e2b0893a9ecfb50f79`; its signed evidence archive has SHA-256 `af4dc7eb880065397206d452519e0f1a7fd8241e1ccc87d2c9e6fadc1e9a4de3`. Independent review confirmed target repository ID `1367018150`, pinned target commit `7d2f5746ae61a66edcd11d75bff0787bed854363`, tree `3269eb54922ae928054a67b98498c2c304876210`, 152 file entries, manifest digest `ea5807106e1139e10c3acffc04bef5af3b5420b985ea7768047e05f9ec110a48`, receipt self-digest `24f5407d241e8555ee90ad54423be7e329d3df07058839537a007ecd1acd9c38`, SHA-256 sums, DSSE signature, signer certificate chain, and Rekor checkpoint/inclusion proof. Verified transparency timestamp: `2026-10-17T13:26:07Z`. This is source-identity evidence only; it claims no target runtime/test execution, runtime identity, protocol conformance, or governance closure. RI-PY, RI-RS, release gates, and branch-protection changes remain separately blocked. No target repository mutation is authorized or performed by this stage.

**Reference source inventory: PASS** for [workflow run 39037323404](https://github.com/vaidt/Kt-ry-Program/actions/runs/39037323404), ASIG commit `130385746c77538eeeb7601877b1b0b966afa421`. The [inventory artifact](https://github.com/vaidt/Kt-ry-Program/actions/runs/39037323404/artifacts/12103100176) and signed archive SHA-256 `031b9a2736f6eed4dc7498c710387021d100a3e8f6fc92284779870b5068e9c5` were independently checked: archive and checksum integrity, four canonical metadata self-digests, target commit/tree pins, context bindings, and external Sigstore identity verification. Details: [Reference Inventory Evidence Verification](REFERENCE_INVENTORY_EVIDENCE_VERIFICATION.md). This PASS covers only the two pinned source inventories (RI-PY: 194 files; RI-RS: 136 files). It does **not** authorize target runtime execution, conformance claims, repository changes, or release-gate adoption.

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
4. **RI-PY / RI-RS source inventory** — **PASS for run `39037323404` only**, limited to the frozen source snapshots recorded in [REFERENCE_IMPLEMENTATIONS_INVENTORY.md](REFERENCE_IMPLEMENTATIONS_INVENTORY.md). Any changed pin or later run requires a new evidence review.
5. **RI-PY runtime pilot — BLOCKED** — requires separate human/governance authorization, frozen source selection, and an approved test list. The source-inventory PASS does not authorize this stage.
6. **RI-RS runtime pilot — BLOCKED** — requires separate human/governance authorization and a defined toolchain/binary/test-harness binding; the source-inventory PASS does not authorize this stage.
7. **Mutation and independent review** — test wrong-source imports, incomplete IDs, altered manifests, changed artifacts, and invalid/missing attestations.
8. **Only then consider a required release gate** — requires Architecture Review, repository-specific authorization, protected branch settings, and verification instructions.

## Non-goals

- ASIG does not make an implementation Aura-conformant.
- ASIG cannot resolve governance or ratification gaps in Aura specification.
- A source manifest digest alone is not a signature or origin-authentication proof.
- A signed source-audit receipt is not proof that target tests passed.
- ASIG PASS does not imply protocol-level PASS.
