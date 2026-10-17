# AURA Adoption Map

Status: staged rollout proposal. The ASIG feature branch has a read-only Aura-Guard source audit workflow and runtime adapter prototypes. The signed pilot receipt must be reviewed before proceeding to RI-PY/RI-RS. No target repository mutation is authorized or performed by this stage.

## Intended integration role

ASIG runs beside Aura-Guard, RI-PY, and RI-RS as an engineering control. It provides source/build/test identity evidence for release engineering. It must not replace the Conformance Core or redefine protocol semantics.

## Current controls

| Risk | ASIG control | Current strength / gap |
|---|---|---|
| Wrong or modified checkout | Git commit/tree, clean-tree check, tracked source inventory, SHA-256 manifest | Implemented and covered by unit tests |
| Receipt content altered | Manifest/receipt self-digest plus GitHub Artifact Attestation on the pilot receipt | Signature authenticity depends on verification of the signer repository/workflow; unsigned manifests alone do not authenticate origin |
| Tests imported a different Python file | Cooperative Python loader records actual loaded bytes and expected file digest | Unit-tested; limited to configured file-backed modules and cooperative execution |
| Node imported a different module | Explicit CommonJS and ESM specifier hooks | Identity hooks have unit tests; no test-suite completeness adapter yet |
| Rust source/build identity | Git/source manifest plus Cargo/toolchain context receipt | Does not yet prove runtime machine-code identity |
| Partial test suite presented as full suite | Exact required versus observed pytest node IDs | Python adapter only; Node/Rust test-runner integrations remain open |
| Delivered artefact differs from evaluated artefact | Existing supplied evidence qualifier compares delivered/tested hashes | Still requires an authenticated, immutable artifact handoff from independent evaluator |

## Staged rollout

1. **ASIG standalone CI** — run unit and mutation tests for the source identity and adapter receipts.
2. **Aura-Guard read-only source pilot** — inventory only, write output outside target checkout, sign the receipt in the ASIG repository workflow. Do not alter Aura-Guard.
3. **Review the signed pilot** — verify attestation signer identity, target commit/tree, source manifest digest, and explicit scope limitations. If the workflow or evidence fails, stop; do not treat absence as PASS.
4. **RI-PY read-only pilot** — only after step 3 is reviewed, capture the frozen core repository and add a controlled Python runtime/test run against an approved test list.
5. **RI-RS read-only pilot** — capture the Rust repository and toolchain context; do not claim live source identity until a verifiable binary/test-harness binding has been designed and tested.
6. **Mutation and independent review** — test wrong-source imports, incomplete IDs, altered manifests, changed artifacts, and invalid/missing attestations.
7. **Only then consider a required release gate** — requires Architecture Review, repository-specific authorization, protected branch settings, and verification instructions.

## Non-goals

- ASIG does not make an implementation Aura-conformant.
- ASIG cannot resolve governance or ratification gaps in Aura specification.
- A source manifest digest alone is not a signature or origin-authentication proof.
- A signed source-audit receipt is not proof that target tests passed.
- ASIG PASS does not imply protocol-level PASS.
