# ASIG Runtime Adapters

Status: Implemented as engineering-preview adapters; qualification strength differs by language.

## Shared receipt principles

All adapters run an explicit argv command without invoking an implicit shell, capture process status and output digests, write receipts outside the repository being measured, and preserve missing evidence as UNKNOWN/BLOCKED. These hooks are cooperative instrumentation, not sandboxes.

## Python

Command: `aura-source-identity runtime-python`

The adapter injects an ASIG bootstrap into the child environment. For explicitly mapped module names, the finder delegates normal discovery to Python's `PathFinder`, captures stable filesystem source bytes, hashes them, and compiles the captured bytes directly to avoid relying on cached bytecode. It compares both resolved path and content digest with the expected target path.

When the command is a pytest invocation, an explicit plugin records call-phase node IDs and outcomes. Qualification can be PASS only when all configured expected modules are exact path/content matches, the command succeeds, and the observed test-node set exactly equals the required set with every outcome passing.

Limits: arbitrary Python processes can disable or bypass cooperative instrumentation; custom import loaders, native modules, exec/eval, subprocesses that do not inherit the environment, and unconfigured modules are not proven. Test IDs are only as authoritative as the caller-supplied required list.

## Node.js

Command: `aura-source-identity runtime-node`

The adapter sets `NODE_OPTIONS` to load an explicit CommonJS `Module._load` observer and an ESM loader hook. Module specifiers must be listed explicitly and mapped to expected source paths. It compares loaded source digest and path to the target source.

Current limitation: this adapter does not extract a complete test inventory from Jest/Vitest/node:test or another test framework. For this reason, an otherwise successful run is BLOCKED rather than PASS until runner-specific test-scope evidence is connected. Custom loaders, native addons, eval/Function, and imports that use unconfigured specifiers are outside the observed scope.

## Rust / Cargo

Command: `aura-source-identity runtime-rust`

The adapter records the Cargo command's exit status/output digests, Cargo and rustc versions, and SHA-256 digests of `Cargo.toml`, `Cargo.lock`, and selected toolchain files when present. It can compare observed test-output names against a caller-supplied expected set when Cargo output exposes compatible harness lines.

Current limitation: Cargo build-context evidence is not direct observation of loaded Rust source or executed machine-code identity. Even a zero exit code is reported as BLOCKED until a separate, independently validated execution-artifact binding exists. This is deliberate; do not promote this adapter to PASS by inferring runtime identity from a lockfile hash.

## Required validation before release-gate use

- Positive control: exact source path and bytes, complete required suite, all tests pass.
- Negative control: a different source copy is imported even though tests happen to pass.
- Missing-observation control: the expected module is never observed; result remains UNKNOWN/BLOCKED.
- Scope control: one required test is omitted or a duplicate ID appears; no completeness PASS.
- Mutation control: test source or tested artefact changes after the manifest is captured.
- Per-adapter checks: verify receipts have stable schema, accurate scope limitations, and tamper-evident metadata.

Only the Python adapter currently has an end-to-end unit test asserting a full suite identity qualification. Node tests assert only identity observation and intentionally expect BLOCKED. Rust is context-only and intentionally cannot assert runtime-source identity.
