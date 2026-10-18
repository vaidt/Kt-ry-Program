# ASIG Workspace Environment

**Status:** Engineering workspace profile; not a release or protocol-qualification environment.

## Supported workspace

The Dev Container definition in `.devcontainer/devcontainer.json` provides:

- Python 3.12 and an isolated `.venv`;
- Node.js 22 for runtime adapter tests;
- Rust stable, rustfmt, and Clippy for Cargo adapter tests;
- VS Code extensions for Python, YAML, and Rust;
- an automated post-create bootstrap that installs the ASIG package in editable mode and build tooling.

The container installs project dependencies from `pyproject.toml`. Do not place secrets in workspace environment variables or commit local environment files. Git credentials are not required for local test execution. Do not mount production credentials, target-repository secrets, or signing keys into this workspace.

## Local commands

Run `make help` to display commands.

| Command | Function |
|---|---|
| `make bootstrap` | Create .venv and install the package/build tooling |
| `make doctor` | Report Python, Node, Rust, Cargo, Git, and pip versions |
| `make validate-delegations` | Validate delegation records and write a local report under .artifacts |
| `make compile` | Compile source, scripts, and tests |
| `make test` | Run the complete unittest suite |
| `make test-runtime` | Run the Python/Node/Rust adapter contract tests |
| `make build` | Build wheel/sdist and create SHA-256 checksums |
| `make ci-local` | Run delegation validation, compile, tests, adapter tests, and build in sequence |

The local environment is a convenience and consistency layer. CI on the pull-request revision remains authoritative for required GitHub status checks. A local PASS does not establish independent review or governance authority.

## Integration workflow

The workflow `.github/workflows/delegation-integration-gate.yml` uses isolated GitHub-hosted runners and read-only repository permissions. It runs:

1. schema/template parsing and delegation invariant validation;
2. unit/contract tests and distributions builds under Python 3.11, 3.12, and 3.13;
3. runtime adapter tests under Python 3.12, Node 22, and Rust stable.

Validation/build artifacts are retained for 14 days. The exact workflow run, checked commit, artifact digest, and test outcomes must be recorded when evidence is needed.

## Upstream workspace policy

No Git remote, source sync, or source import from `down-shift/which-program` is configured by this profile. The upstream licensing question is unresolved in `docs/UPSTREAM_AND_LICENSE.md`; a public repository or upstream URL does not grant reuse permission.

To add upstream integration later, first establish the applicable license or explicit permission, record the exact repository/ref/commit, review the diff and provenance, then run the normal PR and security gate. Do not fetch-and-merge upstream source automatically.

## Safety and reproducibility limits

- The workspace is designed for repeatable engineering checks, not bit-for-bit container image reproducibility.
- The Dev Container image/features use version references; pinning immutable image/feature digests should be a separate controlled change if strict toolchain image reproducibility becomes a release requirement.
- Rust stable can advance over time. Capture `rustc --version` and `cargo --version` in any evidence intended to support a release decision.
- No command in this workspace deploys, publishes a package, updates another repository, merges a PR, or changes protocol semantics.
