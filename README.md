# Który Program — AURA Source Identity Gate

**ASIG 0.2.0 · Engineering preview · Not a protocol certification tool**

Kt-ry-Program develops an independent source-identity and test-evidence gate for AURA engineering workflows.

ASIG separates three different claims: **which source was observed**, **which tests actually reported results**, and **whether the resulting evidence is sufficient to qualify a delivery**. Missing observations do not become PASS.

## Current capabilities

- Capture a sorted SHA-256 inventory of Git-tracked files and symbolic links.
- Bind a manifest to the Git commit SHA, tree SHA, and clean-worktree status.
- Verify manifest integrity and compare the current checkout against the captured inventory.
- Qualify supplied test evidence with `PASS`, `FAIL`, or `BLOCKED`.
- **Python adapter:** instrument explicitly mapped filesystem-backed `.py` imports, capture pytest call results, and compare observed test node IDs to the required set.
- **Node adapter:** instrument explicitly mapped CommonJS `require()` and ESM imports and compare loaded source bytes to the expected file.
- **Rust/Cargo adapter:** capture command outcome, selected toolchain versions, and critical Cargo/toolchain file digests. It explicitly reports `BUILD_CONTEXT_ONLY` because it does not observe loaded machine-code instructions.
- Generate a read-only source inventory receipt for another repository.
- GitHub Actions workflow to sign the Aura-Guard read-only receipt using GitHub Artifact Attestations.
- CI matrix for Python 3.11/3.12/3.13; Node 22 adapter tests; schema parsing; package compilation and distribution builds.

## Quick start

Requires Python 3.11+ and Git.

Install from a checkout:

`python -m pip install .`

Capture a clean source manifest; write the manifest outside the measured repository:

`aura-source-identity capture --root . --repository vaidt/Kt-ry-Program --output ../asig-manifest.json`

Verify it:

`aura-source-identity verify --root . --manifest ../asig-manifest.json`

Qualify supplied test evidence:

`aura-source-identity qualify --root . --manifest ../asig-manifest.json --evidence ../asig-evidence.json --output ../asig-qualification.json`

## Runtime adapters

Python example; required pytest node IDs must come from the approved test plan:

`aura-source-identity runtime-python --root . --manifest ../asig-manifest.json --module package.rules=package/rules.py --required-test-id public_tests/test_public.py::test_example --output ../asig-python-receipt.json -- python -m pytest -q public_tests`

Node example; mappings are exact module specifier strings and expected paths:

`aura-source-identity runtime-node --root . --manifest ../asig-manifest.json --specifier ./verification.js=frontend/src/lib/verification.js --output ../asig-node-receipt.json -- node run-a-test-command.js`

Rust example:

`aura-source-identity runtime-rust --root . --manifest ../asig-manifest.json --required-test-id module::test_name --output ../asig-rust-receipt.json -- cargo test --locked`

**Status semantics:** Python can return `PASS` only when every configured module is observed as an exact path/content match and the observed pytest node IDs exactly match the required set with all tests passing. Node records source identity but currently leaves overall qualification `BLOCKED` because there is no runner-specific test-completeness adapter yet. Rust records build context only and deliberately leaves qualification `BLOCKED` on a passing command. A non-zero command or confirmed source mismatch is `FAIL`.

## Read-only Aura-Guard pilot

The workflow [read-only-aura-guard-pilot.yml](.github/workflows/read-only-aura-guard-pilot.yml) checks out `vaidt/Aura-Guard` with `persist-credentials: false`, creates the manifest and receipt outside the target checkout, and generates a signed GitHub Artifact Attestation for the receipt. It runs on schedule, manual dispatch from `main`, and changes to ASIG’s relevant source/workflow paths.

The current pilot is **source inventory only**. It does not run Aura-Guard tests and does not claim protocol conformance or runtime identity.

After the Aura-Guard pilot has a successful, reviewable receipt, the planned next phase adds separate read-only inventories and controlled adapter executions for RI-PY (`vaidt/aura-poc-a-core-v3.3`) and RI-RS (`vaidt/aura-guard-v1.3`). Those targets remain outside this stage’s changes.

## Verify an attestation

After downloading the receipt artifact from GitHub Actions, verify it with GitHub CLI:

```sh
gh attestation verify asig-aura-guard-read-only-receipt.json --repo vaidt/Kt-ry-Program --signer-workflow vaidt/Kt-ry-Program/.github/workflows/read-only-aura-guard-pilot.yml --predicate-type https://github.com/vaidt/Kt-ry-Program/attestations/asig-read-only-source-audit/v1
```

This verifies the artifact attestation’s signature and configured signer identity. The signed receipt proves which read-only source snapshot the ASIG workflow recorded; it is not an attestation that the target repository’s code is correct or Aura-conformant.

See [CI Attestations](docs/CI_ATTESTATIONS.md), [Runtime Adapters](docs/RUNTIME_ADAPTERS.md), [the read-only receipt schema](schemas/read-only-source-audit-receipt.schema.json), [architecture](docs/ARCHITECTURE.md), [the threat model](docs/THREAT_MODEL.md), [the AURA adoption map](docs/AURA_ADOPTION_MAP.md), and [the RI-PY/RI-RS inventory evidence review](docs/REFERENCE_INVENTORY_EVIDENCE_VERIFICATION.md).

## Integration boundary

ASIG is an engineering control. It does not replace Aura-Guard’s Conformance Core, does not modify normative Aura Protocol semantics, and does not certify an implementation as Aura-conformant.

Runtime observation is cooperative and scoped to the explicitly configured modules/specifiers. It is not a hostile-process security boundary and does not prove every loaded library, custom loader, native extension, dynamic evaluation, or operating-system instruction. No target runtime integration should become a required release gate until the relevant adapter is validated with mutation tests and approved governance.

## Upstream relationship and licensing

This is an independent implementation informed by public design material from [down-shift/which-program](https://github.com/down-shift/which-program). No upstream source files were copied. The upstream licensing status and the licensing status of this repository are documented in [UPSTREAM_AND_LICENSE.md](docs/UPSTREAM_AND_LICENSE.md). Do not assume this repository is open-source licensed or publish it to a public package index under an assumed license.

## Development

Run tests with `python -m unittest discover -s tests -v`. CI compiles the package, validates JSON files, runs the tests on supported Python versions, tests Node adapters under Node 22, and builds wheel/source distributions.

**Current status:** ASIG 0.2.0 on `main`; the Aura-Guard source-identity pilot and pinned RI-PY/RI-RS source-inventory evidence have independently verified PASS results. RI-PY/RI-RS runtime qualification, protocol conformance, and release-gate adoption remain **BLOCKED** pending separate approved authorization.
