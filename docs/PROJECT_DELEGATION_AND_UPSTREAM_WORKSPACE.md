# Project Delegation and Upstream Workspace Contract

**Document ID:** ASIG-GOV-DEL-001  
**Version:** 1.0  
**Status:** PROPOSED — workflow and schema are engineering controls, not an authorization instrument  
**Repository:** `vaidt/Kt-ry-Program`  
**Scope:** ASIG engineering/R&D workflow only

## 1. Purpose

Provide one auditable contract for delegated engineering tasks, their execution boundary, integration checks, evidence, verification, and rollback. A work item is not authorized merely because an issue exists, a branch was created, CI passes, or an agent reports completion.

The contract follows these rules:

- **Exists ≠ reachable ≠ current ≠ authoritative ≠ normative ≠ effective.**
- **PASS on tooling is not authorization.** CI establishes only the controls that actually ran against the recorded revision.
- **Missing or ambiguous evidence is BLOCKED/NOT PROVEN, never PASS by default.**
- Delegates may propose or implement only the explicitly authorized scope. They may not self-approve their authority.
- No workflow in this change executes arbitrary commands from a delegation record, mutates a target repository, merges a PR, deploys, or changes AURA Protocol semantics.

## 2. Upstream and workspace boundary

### 2.1 Code lineage versus Git remote

The current lineage note identifies `down-shift/which-program` as public reference material. It states that ASIG was independently implemented and that upstream licensing was not established in the recorded review. That status remains a hard constraint: do not add an upstream Git remote as permission to pull, copy, port, publish, or redistribute code. Do not synchronize upstream source until applicable licensing or explicit written permission is established and reviewed.

A documentation reference to an upstream project is not a license grant and is not proof that code was copied or synchronized.

### 2.2 Repository roles

| Resource | Intended role | Boundary |
|---|---|---|
| `vaidt/Kt-ry-Program` | ASIG implementation, schemas, controls, and evidence | Engineering gate; not AURA protocol certification |
| `main` | Protected integration/review target | No direct push; PR and required checks/review apply |
| Feature branch | Isolated delegated work | Non-authoritative until reviewed and merged |
| External upstream reference | Provenance/context only | No automatic source synchronization |
| Other AURA repositories | Separate targets | This workflow does not check them out, test them, or mutate them |

The historical R&D-only `integration` branch is not assumed to exist. A missing branch must be confirmed and authorized before anyone recreates it or changes the repository's branch topology.

## 3. Delegation lifecycle

1. **PROPOSED** — an issue or JSON record describes the objective, scope, paths, target ref, acceptance criteria, risk, evidence, and rollback. No implementation is authorized.
2. **BLOCKED** — required constitutive evidence, authority continuity, approved scope, or a required prerequisite is missing.
3. **AUTHORIZED_FOR_R&D** — only after a competent issuer, current holder, authority scope, effective period, and constitutive evidence references are recorded and verified. Authorization is bounded to non-normative R&D/documents/CI-security work.
4. **IN_PROGRESS** — work occurs on a non-protected source branch. The delegate may not broaden scope, alter normative AURA semantics, access target-repository secrets, or claim conformance.
5. **VERIFICATION_PENDING** — implementation is complete; evidence, acceptance criteria, tests, and review are assembled.
6. **VERIFIED** — required tests have recorded PASS results, evidence is available, and the prescribed verification/independence condition is satisfied.
7. **CLOSED** or **REJECTED** — the decision and evidence are recorded. Closure does not silently close an independent CAPA, licensing issue, governance gap, protocol question, or release gate.

The automation validates this lifecycle contract. It does not establish identity, appointment, holder continuity, ratification competence, legal authority, or independent human control.

## 4. Minimum delegation record

Create a record by copying `docs/templates/project-delegation.template.json` to:

`governance/delegations/records/ASIG-DEL-NNNN.json`

Replace every placeholder and keep the identifier consistent with the filename. A record must declare:

- objective, requester, and timestamp;
- exact repository and source reference;
- in-scope and out-of-scope work, path allowlist and denylist;
- source branch, intended target branch, change class, and network-side-effect classification;
- whether implementation is authorized, and the evidence for that decision;
- issuer, current holder, scope, effective date, expiry, decision reference, and constitutive evidence;
- required tests, observed results, reviewer role, independence disposition, and evidence references;
- rollback plan and objective rollback triggers.

Do not store credentials, tokens, private keys, personal secrets, or raw secret-bearing logs in records or artifacts. Use stable links/identifiers and sanitized evidence.

## 5. Fail-closed policy

The executable validator must reject a record when, among other things:

- an authorized status is asserted while `implementation_authorized` is false, or vice versa;
- implementation is authorized without proven authority status, scoped constitutive evidence, or a valid effective period;
- a delegated action is classified as protocol-normative, target-runtime execution, release, or production work;
- direct push is permitted or PR-based change control is disabled;
- VERIFIED is claimed without all required tests passing, evidence references, and the required independence disposition;
- required fields are empty, placeholders remain, duplicate records exist, or status/evidence combinations conflict.

The JSON Schema is the portable contract definition. The repository validator enforces the project-specific critical invariants using the Python standard library; it is not represented as a general-purpose implementation of every JSON Schema keyword.

## 6. Automated integration jobs

`.github/workflows/delegation-integration-gate.yml` adds three independent checks:

1. **Delegation contract** — parses the schema/template and validates every record under `governance/delegations/records/`. With no records, it emits `NO_RECORDS`; this is a structural result, not a delegation approval.
2. **Python test/build matrix** — runs package compilation, unit tests, and wheel/source-distribution build across Python 3.11, 3.12, and 3.13.
3. **Runtime adapter integration** — runs the existing Python/Node/Rust adapter tests under pinned toolchain setup actions.

The jobs are read-only with respect to GitHub content and do not deploy or merge. Test/build evidence is uploaded as short-retention workflow artifacts. Existing CI and security workflows remain in place; this addition does not replace their required status contexts.

## 7. Upstream workspace integration sequence

1. Select the canonical repository and fetch the exact source ref/SHA.
2. Create a uniquely named non-protected branch from that baseline.
3. Add the delegation record before assigning implementation work; keep it PROPOSED/BLOCKED until authority evidence is sufficient.
4. Make changes only within the path allowlist.
5. Run the contract validator, test matrix, runtime integration tests, and existing security workflows.
6. Publish evidence references and hashes; distinguish source inventory, test outcomes, artifact integrity, and attestation claims.
7. Open a PR against an existing authorized target branch. Require normal repository protection and review; do not bypass controls.
8. Verify the exact reviewed head and required check contexts before merge. Do not treat account-level review events alone as proof of independent human control.
9. Record the merge SHA, post-merge status, and residual risks. Keep unrelated CAPA/governance/license items OPEN until independently resolved.

## 8. Acceptance criteria

- The issue form gathers a complete delegation proposal without implying approval.
- The schema parses as JSON and records are rejected on authority/status contradictions.
- Unit tests cover unauthorized execution, valid R&D authorization, and verification-independence failures.
- The integration workflow uses full-length action commit SHAs and runs without deployment or target-repository mutation.
- The repository's existing required checks and branch protection are not modified.
- The pull request remains unmerged pending the repository's standard review and governance controls.

## 9. Explicit non-claims

This implementation does not establish that an upstream license is clear, that independent human review is proven, that any AURA governance/ratification gate is closed, that target runtimes are qualified, that an artifact has a signed attestation, or that ASIG/AURA is production-ready. A successful workflow run is evidence only for its recorded commit and the jobs that actually completed.
