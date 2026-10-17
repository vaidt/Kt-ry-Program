# ASIG Architecture

Status: MVP 0.1.0 — engineering preview, not a certification product.

## Objective

AURA Source Identity Gate (ASIG) captures the source inventory for a Git checkout, verifies that inventory against the current checkout, and qualifies supplied test/evaluation evidence without converting missing evidence into a positive result.

ASIG is an independent engineering-control tool. It does not define Aura Protocol behavior, evidence hashing, canonical serialization, or conformance status semantics.

## Data flow

1. Capture a sorted inventory of regular files and symbolic links under a declared repository root.
2. Record each path, entry kind, size, and SHA-256; do not follow symbolic links.
3. Bind the inventory to Git commit SHA, Git tree SHA, and working-tree cleanliness.
4. Hash the manifest body using ASIG's private deterministic JSON encoding.
5. Verify the manifest hash and compare the inventory and Git identity against a current checkout.
6. Qualify separate evidence for test-plan completeness, observed test-source identity, per-test outcomes, and independent evaluation of the delivered artifact.
7. Emit PASS, FAIL, or BLOCKED, together with the reasons.

## Trust boundaries

ASIG's manifest proves a content comparison within the stated scope. It does not, by itself, prove who created the manifest, that a CI runner was uncompromised, that a test process imported the intended module, or that a build is reproducible.

A supplied execution-evidence JSON document is not an attestation merely because it is well-formed. The evidence source and authentication of CI results remain external trust inputs in MVP 0.1.

## Manifest scope

Default excluded path components include Git metadata, Python caches and virtual environments, Node dependency directories, build/distribution directories, and run output directories. Extra exclusions are declared in the manifest. Do not exclude protocol-critical source files, tests, fixtures, schemas, policy files, lockfiles, or build configuration when making a release claim.

The manifest output should be placed outside the repository being measured. This avoids the manifest itself changing the tree cleanliness status.

Symlinks are recorded as links, including the link text; targets are not followed. Special files are not inventoried in MVP 0.1.

## Status semantics

- EXACT_MATCH: manifest integrity, inventory, commit, tree, and clean-checkout conditions all match.
- MISMATCH: an observable content or source-identity condition differs.
- UNKNOWN: verification cannot establish the necessary facts, such as when Git metadata is unavailable or the manifest is malformed.
- PASS: the complete qualification contract is satisfied.
- FAIL: a verified requirement has failed, such as a content mismatch or failing mandatory test.
- BLOCKED: required evidence is missing, incomplete, unsupported, or unknown.

UNKNOWN and BLOCKED are never promoted to PASS.

## Determinism boundary

The deterministic JSON encoding in canonical.py is private to ASIG metadata. It is not RFC 8785 JCS and is not the Aura Protocol canonical byte contract. Do not use it to generate Aura Protocol hashes, audit chain links, Evidence Pack hashes, or normative fixtures.

## Current implementation boundary

MVP 0.1 inventories source state and qualifies externally supplied test evidence. It does not yet instrument Python imports, Node.js module resolution, Rust process execution, compiled binaries, dependency loading, or operating-system state. Runtime-level adapters and authenticated CI attestations are later work.
