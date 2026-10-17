# AURA Adoption Map

Status: proposal only; no Aura Protocol or Aura-Guard mutation is authorized by this document.

## Intended integration role

ASIG is a build/test provenance gate that runs beside Aura-Guard, RI-PY, and RI-RS. It should provide the source/build/test identity evidence consumed by release engineering. It must not replace the Conformance Core or redefine protocol semantics.

## Mapping from engineering risks to ASIG controls

| Risk | ASIG control in MVP 0.1 | Remaining work |
|---|---|---|
| Test was run against a modified or different checkout | File inventory + Git commit/tree + clean-worktree verification | Runtime module identity per supported language |
| Delivered source changed after evidence capture | Re-inventory and exact manifest comparison | Immutable CI artifact store and authenticated attestations |
| Partial test suite is claimed as full coverage | Exact comparison of required and executed test IDs | CI adapter must collect IDs from the actual runner, not accept manually typed claims |
| Public test source changed | Expected versus observed test-source digest | Runner integration and automatic test-file collection |
| Independent evaluator tested different bytes | Equality of delivered and tested artifact SHA-256 | Build artifact capture and separate isolated evaluator job |
| Failure or missing observation is treated as success | FAIL-dominant and BLOCKED-preserving qualification | Wire the result into repository branch protection after successful pilot |

## Proposed repository integration order

1. Validate ASIG as a standalone tool in Kt-ry-Program.
2. Add a read-only pilot job to Aura-Guard CI that emits a manifest and test evidence artifact.
3. Compare ASIG results against existing CI outcomes; do not block merges yet.
4. Run mutation tests that intentionally change source, test IDs, test hashes, and delivered artifact hashes.
5. Add RI-PY and RI-RS adapters with explicit toolchain and artifact identity.
6. Only after a recorded Architecture Review and appropriate repository-specific authorization, introduce ASIG as a required release gate.

## Non-goals

- ASIG does not make an implementation Aura-conformant.
- ASIG cannot resolve governance or ratification gaps in the Aura specification.
- A source manifest is not a cryptographic attestation of identity or a signature.
- An ASIG PASS does not imply protocol-level PASS.
