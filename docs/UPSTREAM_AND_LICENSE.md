# Upstream relationship and licensing note

The design of this independent implementation is informed by the publicly visible project:

- Repository: https://github.com/down-shift/which-program
- Project focus: runtime source identity, independent repair evaluation, and evidence-supported verification claims.
- Reference material reviewed: README.md, docs/protocol.md, docs/limitations.md, docs/claim_rubric.md, src/program_identity/provenance.py, src/program_identity/execution.py, src/program_identity/evaluator.py, src/program_identity/tasks.py, and src/program_identity/pytest_plugin.py.

No source files from the upstream repository were copied into this repository. ASIG MVP 0.1 is a clean-room implementation of a narrower source-inventory and evidence-qualification contract.

At the time of initial integration review (2026-10-17), a top-level LICENSE file was not found through the repository file endpoint. Absence of a license file is not a grant of reuse rights. Reconsider direct code import or porting only after the upstream owner has clarified the applicable license or supplied explicit permission.

This note is provenance context, not legal advice. The licensing terms for this repository itself remain to be decided by its owner. Until then, do not represent the repository as open-source licensed or publish the package to a public package index under an assumed license.
