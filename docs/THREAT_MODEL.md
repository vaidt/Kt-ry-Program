# ASIG Threat Model

## Assets

- Identity of source files, Git commit, and Git tree.
- Integrity of the source manifest.
- Completeness and correctness of supplied test/evaluation evidence.
- Separation of source identity, test outcome, and final qualification.

## Threats addressed in MVP 0.1

- Accidental source drift after manifest capture.
- Manifest body tampering without recomputing the manifest digest.
- A test plan that omits required test IDs or includes duplicates.
- Missing or failing mandatory test outcomes.
- A test source digest that differs from the expected digest.
- Independent evaluation of a different artifact hash.
- Missing identity or test evidence incorrectly treated as success.

## Threats not solved by MVP 0.1

- A malicious actor who can rewrite the manifest and recompute its unkeyed SHA-256.
- Compromised GitHub credentials, branch controls, CI runners, or dependencies.
- Runtime import redirection, dynamic loading, monkeypatching, native code, injected processes, or compromised operating systems.
- Supply-chain attacks in build tools or dependencies.
- Forged test evidence supplied by a trusted-looking but unauthenticated caller.
- Untrusted clocks or timestamps.

## Controls required for a higher assurance level

- Signed CI attestations tied to workflow identity and commit SHA.
- Pinned build tools and dependency lockfiles.
- Reproducible builds where technically feasible.
- Isolated independent evaluation of immutable build artifacts.
- Language-specific runtime source identity instrumentation.
- Protected main branch, required CI, code-owner review, and release provenance.
- Explicit artifact retention and verification procedures.

## Security interpretation

A SHA-256 digest provides integrity comparison, not origin authentication. PASS only means the current qualification contract passed against the supplied evidence and checks; it does not establish resistance to a compromised CI environment.
