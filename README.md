# Który Program — AURA Source Identity Gate

**ASIG MVP 0.1.0 · Engineering preview · Not a protocol certification tool**

Kt-ry-Program develops an independent source-identity and test-evidence gate for AURA engineering workflows.

The core question is simple: do the preserved test results refer to the exact source tree and delivery artifact that are being presented for review? ASIG compares a deterministic source inventory with the current Git checkout and checks supplied test evidence for complete test IDs, test-source hash consistency, explicit outcomes, and independent evaluation of the delivered artifact.

## Current capabilities

- Capture a sorted SHA-256 inventory of repository files and symbolic links.
- Bind the manifest to the Git commit SHA, tree SHA, and working-tree cleanliness.
- Verify manifest integrity and compare the current checkout to the captured inventory.
- Qualify evidence as PASS, FAIL, or BLOCKED without treating missing evidence as success.
- Emit JSON reports with a digest that permits tamper detection of the report content.
- Run unit tests on Python 3.11, 3.12, and 3.13 in GitHub Actions.
- Build Python wheel/source distributions and attach them to a GitHub Release when a version tag is pushed.

## Quick start

Requires Python 3.11+ and Git.

Install from a checkout using `python -m pip install .`.

Capture a clean checkout manifest; keep the output outside the repository being measured:

`aura-source-identity capture --root . --repository vaidt/Kt-ry-Program --output ../asig-manifest.json`

Verify it later against the same checkout:

`aura-source-identity verify --root . --manifest ../asig-manifest.json`

Qualify a test-evidence document against that manifest:

`aura-source-identity qualify --root . --manifest ../asig-manifest.json --evidence ../asig-evidence.json --output ../asig-qualification.json`

The capture command exits non-zero when the working tree is not clean. Verification returns EXACT_MATCH only when the manifest integrity, inventory, commit, Git tree, and clean-checkout requirements are satisfied.

## Qualification rules

- **PASS** requires an exact verified source identity, a complete test plan whose executed IDs equal the required IDs, passing results for each required test, unchanged test-source hashes, and an independent evaluation of the same delivery artifact hash.
- **FAIL** means a concrete mismatch or mandatory test/evaluation failure was observed.
- **BLOCKED** means the evidence is missing, incomplete, unsupported, or unknown.

FAIL dominates BLOCKED. Neither missing evidence nor an unknown observation can become PASS.

See [the evidence schema](schemas/source-identity-evidence.schema.json), [the manifest schema](schemas/source-identity-manifest.schema.json), [architecture](docs/ARCHITECTURE.md), and [the threat model](docs/THREAT_MODEL.md).

## AURA integration boundary

ASIG is a repository/build/test engineering control. It does not replace Aura-Guard's Conformance Core, does not modify normative Aura Protocol semantics, and does not certify an implementation as Aura-conformant.

MVP 0.1 checks the repository inventory and qualifies supplied test evidence. It does **not yet** instrument live imports or runtime module resolution in Python, Node.js, or Rust; nor does it authenticate an external CI attestation. These are explicit future milestones, not current guarantees.

The proposed integration path for Aura-Guard and RI-PY / RI-RS is documented in [AURA Adoption Map](docs/AURA_ADOPTION_MAP.md). Repository-specific authorization and architecture review are required before making ASIG a mandatory gate in other AURA repositories.

## Upstream relationship

This is a clean-room implementation informed by the engineering concepts documented in [down-shift/which-program](https://github.com/down-shift/which-program). No upstream source files were copied. The upstream licensing status and the licensing status of this repository are documented in [UPSTREAM_AND_LICENSE.md](docs/UPSTREAM_AND_LICENSE.md). Do not assume that this repository is open-source licensed or publish it to a public package index under an assumed license.

## Development

Run the test suite with `python -m unittest discover -s tests -v`. The CI pipeline also compiles the package and builds wheel/source distributions.

**Current status:** feature branch implementation; review and CI acceptance required before merge to `main`.
