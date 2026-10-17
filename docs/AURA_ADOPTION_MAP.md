# AURA Adoption Map

Status: staged rollout proposal. ASIG main contains the read-only Aura-Guard pilot workflow and runtime adapter prototypes. **Read-only source-identity gate: PASS** for [workflow run 39035764160](https://github.com/vaidt/Kt-ry-Program/actions/runs/39035764160), ASIG commit `d99b0ea07eba660cc3ca90bb145befff0d5fed32`. The [evidence artifact](https://github.com/vaidt/Kt-ry-Program/actions/runs/39035764160/artifacts/12102345928) has SHA-256 `d0c92f5f31e1efe6da4626df950bd6efc0754a0b44c956b23cb04b18a4695799`; its signed evidence archive has SHA-256 `22e40dfa1e0212796808245610b6a16deffcb6278db53368f7ea2b95bbe9aac3`. Independent review confirmed target repository ID `1367018150`, pinned target commit `7d2f5746ae61a66edcd11d75bff0787bed854363`, tree `3269eb54922ae928054a67b98498c2c304876210`, 152 file entries, manifest/receipt bindings, checksums, DSSE signature, certificate chain, and Rekor checkpoint/inclusion proof. This is source-identity evidence only; it claims no target runtime/test execution, runtime identity, protocol conformance, or governance closure. RI-PY, RI-RS, release gates, and branch-protection changes remain separately blocked. No target repository mutation is authorized or performed by this stage.

## Intended integration role

ASIG runs beside Aura-Guard, RI-PY, and RI-RS as an engineering control. It provides source/build/test identity evidence for release engineering. It must not replace the Conformance Core or redefine protocol semantics.

## Current controls

| Risk | ASIG control | Current strength / gap |
|---|---|---|
| Wrong or modified checkout | Git commit/tree, clean-tree check, tracked source inventory, SHA-256 manifest | Implemented and covered by unit tests |
| Receipt content altered | Manifest/receipt self-digest plus GitHub Artifact Attestation on the pilot receipt | GitHub Artifact Attestation covers the complete evidence archive; signer identity, workflow, certificate chain, and transparency-log proof must be independently verified |
| Tests imported a different Python file | Cooperative Python loader records actual loaded bytes and expected file digest | Unit-tested; limited to configured file-backed modules and cooperative execution |
| Node imported a different module | Explicit CommonJS and ESM specifier hooks | Identity hooks have unit tests; no test-suite completeness adapter yet |
| Rust source/build identity | Git/source manifest plus Cargo/toolchain context receipt | Does not yet prove runtime machine-code identity |
| Partial test suite presented as full suite | Exact required versus observed pytest node IDs | Python adapter only; Node/Rust test-runner integrations remain open |
| Delivered artefact differs from evaluated artefact | Existing supplied evidence qualifier compares delivered/tested hashes | Still requires an authenticated, immutable artifact handoff from independent evaluator |

## Staged rollout

1. **ASIG standalone CI** — run unit and mutation tests for the source identity and adapter receipts.
2. **Aura-Guard read-only source pilot** — inventory only, write output outside target checkout, sign the receipt in the ASIG repository workflow. Do not alter Aura-Guard.
3. **Review the signed pilot** — **PASS for run `39035764160` only**; the evidence package is recorded and independently reviewed below. Every later run or target snapshot requires its own verification. If the workflow or evidence fails, stop; absence is not PASS.
4. **RI-PY read-only pilot — BLOCKED** — requires separate human/governance authorization, frozen source selection, and an approved test list. The source-identity PASS does not authorize this stage.
5. **RI-RS read-only pilot — BLOCKED** — requires separate human/governance authorization and a defined toolchain/binary/test-harness binding; the source-identity PASS does not authorize this stage.
6. **Mutation and independent review** — test wrong-source imports, incomplete IDs, altered manifests, changed artifacts, and invalid/missing attestations.
7. **Only then consider a required release gate** — requires Architecture Review, repository-specific authorization, protected branch settings, and verification instructions.

## Non-goals

- ASIG does not make an implementation Aura-conformant.
- ASIG cannot resolve governance or ratification gaps in Aura specification.
- A source manifest digest alone is not a signature or origin-authentication proof.
- A signed source-audit receipt is not proof that target tests passed.
- ASIG PASS does not imply protocol-level PASS.
