# AURA-STAGE3-AUTH-001
## Stage 3 Runtime Architecture Design Authorization

**Act ID:** `AURA-STAGE3-AUTH-001`  
**Authorization level:** `S3-DESIGN ONLY`  
**Status:** `PROPOSED · PENDING RATIFICATION BY PROTOCOL CUSTODIAN`  
**Normative effect:** `NONE UNTIL VALID RATIFICATION AND REGISTRATION`  
**Implementation authorization:** `NOT GRANTED`  
**Conformance / release authorization:** `NOT GRANTED`  
**Document class:** Proposed governance act; non-constitutive until effective  
**Preparation baseline (ASIG integration):** `bd9d59b93a661a987b8c848e5767103cf7ff3fad`

---

## 1. Purpose and state boundary

This document proposes a strictly bounded authorization to perform Stage 3 runtime architecture design for AURA.

It does **not** authorize runtime implementation, modifications to executable adapters, normative protocol changes, implementation-conformance claims, release activity, or production credential use.

The effective state remains:

**`NOT AUTHORIZED`**

The state may transition to `S3-DESIGN AUTHORIZED` only after this act has been validly ratified by the competent authority and the constitutive evidence has been registered in accordance with the current AURA governance mechanism.

## 2. Authority and governing basis

**Competent authority for this act:** `NOT ESTABLISHED — G1 BLOCKED`.

The repository's record-of-reference index and M1 closure record claim a current authority binding and proven authority continuity. Those status declarations are material evidence to inspect, but they are not independently conclusive while the source-level findings below remain unreconciled.

**Current governance references (read-only; not independently conclusive for G1):**
- [Governance Status Index](https://github.com/vaidt/aura-specification/blob/main/GOVERNANCE_STATUS_INDEX.md)
- [AURA M1 Closure Record v1.0](https://github.com/vaidt/aura-specification/blob/main/AURA_M1_CLOSURE_RECORD_v1.0.md)
- [Authority Binding Record v1.1](https://github.com/vaidt/aura-specification/blob/main/AUTHORITY_BINDING_RECORD_v1.1.md)
- [Wave 1 Implementation Authorization v1.2](https://github.com/vaidt/aura-specification/blob/main/AURA_IMPLEMENTATION_AUTHORIZATION_WAVE1_v1.2.md)
- [Article XIII Authorship and Intent Source Review v0.1](https://github.com/vaidt/aura-specification/blob/main/governance/evidence/AURA_ARTICLE_XIII_AUTHORSHIP_AND_INTENT_RECORD_v0.1.md)
- [Founding Instrument and Authority Evidence Procedure v0.1-DRAFT](https://github.com/vaidt/aura-specification/blob/main/governance/AURA-AFI-AEP-001_FOUNDING_INSTRUMENT_AND_AUTHORITY_EVIDENCE_PROCEDURE_v0.1-DRAFT.md)

**G1 evidence disposition:** `NOT PROVEN / BLOCKED`.

The Article XIII source-review record states that procedural effect was not established from the reviewed sources. It reports that the inspected Article XIII insertion did not evidence the amendment steps required by Constitution Article XI; standards-compliant verification of the Genesis declaration's detached SSHSIG envelope was not established due to an anomalous inner algorithm identifier; and the authority-binding record did not independently establish real-world identity or a prior competent source granting constitutional authority. The AFI procedure is itself a non-constitutive, unratified draft, so it does not decide the matter; its existence and conclusions do, however, document an unresolved evidence gap that must be reconciled rather than silently overridden by the M1 closure status.

The Wave 1 authorization is expressly limited to `vaidt/aura-specification`, its named baseline, and its listed paths. It does not authorize changes in runtime implementation repositories and does not establish competence for this separate Stage 3 act.

Before G1 can pass, the evidence package must establish and independently verify:
1. a competent primary source for the authority asserted;
2. the procedurally effective amendment, appointment, or succession chain from source to current holder;
3. the current holder's identity, scope, effective date, and continuing validity for this exact act;
4. standards-compliant verification of any cryptographic signature relied upon, including resolution of the reported SSHSIG envelope anomaly;
5. reconciliation of the source-level findings with the M1 closure and authority-binding claims, with a reasoned disposition.

Only after G1 is established may a competent human issuer ratify this exact act through the applicable mechanism. The ratification record must identify:
1. the competent issuer and the capacity in which the issuer acts;
2. evidence that the issuer's authority is current and covers this act;
3. the applicable ratification mechanism;
4. the exact ratified artifact revision or content digest;
5. the required valid signature and registration evidence;
6. the effective date and any conditions or expiry.

A historical role designation, a local signature file, a GitHub status label, or this draft's presence in GitHub is not, by itself, evidence that this act has been ratified.

## 3. Frozen source baseline — G0 evidence

The following references were read directly from GitHub during preparation on 2026-10-17. These SHAs identify the observed refs; they do not imply that the runtime repositories are authorized for mutation.

| Source | Ref | Observed SHA | Use in S3-DESIGN |
|---|---|---|---|
| `vaidt/Kt-ry-Program` | `integration` | `bd9d59b93a661a987b8c848e5767103cf7ff3fad` | ASIG governance / preparation baseline |
| `vaidt/aura-specification` | `main` | `8f0cd6be94a68a3728e69a1d21d49237c9d8bd05` | Read-only specification and governance reference |
| `vaidt/aura-poc-a-core-v3.3` | `main` | `1d15ecbed8470476684951e9ff301a3cfc26a46d` | Read-only runtime source reference |
| `vaidt/aura-guard-v1.3` | `main` | `e0ed7a8b381b725fe65bd86716894bfdf17d3a94` | Read-only runtime source reference |

**Baseline verification evidence:**
- PR #20 merged as `bd9d59b93a661a987b8c848e5767103cf7ff3fad`.
- All seven required status contexts passed on PR #20's exact head SHA `6ff4dbf24ec2748706f67b87023151f1b68ada04`.
- All seven required status contexts subsequently passed on merge commit `bd9d59b93a661a987b8c848e5767103cf7ff3fad`, including post-merge `codeql`.
- Ruleset [25306960](https://github.com/vaidt/Kt-ry-Program/rules/25306960) was read back as active for `refs/heads/integration`, with strict required status checks and no bypass actors.
- The ASIG residual-risk register was reconciled on the merged baseline. Its open risks remain open; this authorization does not close them.

These observations close the G0 baseline verification requirement for preparing this proposed design act. They do not constitute ratification of this act or authorize implementation.

## 4. Permitted S3-DESIGN activities

After this act becomes effective, the permitted work is limited to design and analysis artifacts:

1. Specify runtime interfaces, component boundaries, and session lifecycle.
2. Produce a threat model using STRIDE and LINDDUN where applicable, with assumptions and mitigations documented.
3. Prepare Architecture Decision Records (ADRs) for the adapter execution model.
4. Define interface contracts, failure semantics, trust boundaries, and lifecycle invariants.
5. Propose canonical conformance vectors for applicable identifiers such as `INV-001…INV-015` and `CK-003`, only after verifying their identifiers and meanings against the current authoritative inventory.
6. Produce traceability from source requirement to design decision and proposed verification method.
7. Record unresolved issues, risk owners, and the evidence needed to close each issue.

All design artifacts MUST identify the source baseline and distinguish normative source requirements from proposals, assumptions, and unresolved decisions.

## 5. Strict operational boundaries

This proposed authorization MUST NOT be interpreted as permission to:

- modify executable code in `aura-poc-a-core-v3.3`, `aura-guard-v1.3`, or any other runtime repository;
- merge runtime implementation changes or execute runtime migration;
- claim implementation conformance, protocol conformance, or AURA standards compliance;
- modify normative APS specifications or ratified protocol semantics;
- bypass repository protections or evidence requirements;
- use production tokens or credentials, publish releases, or promote artifacts;
- treat design review acceptance as implementation authorization.

Any activity outside the explicit S3-DESIGN scope remains `NOT AUTHORIZED`.

## 6. S3-DESIGN exit criteria

The design package may be submitted for independent acceptance only when it includes:

- architecture decision records and a coherent component/interface model;
- threat model with documented mitigations and residual risks;
- session lifecycle and interface contracts;
- proposed conformance vectors with expected outcomes and deterministic test oracles;
- requirement-to-design-to-verification traceability;
- explicit list of open decisions and dependencies;
- independent review evidence identifying reviewer, reviewed revision, findings, and disposition;
- evidence that no prohibited runtime-code or normative-specification changes occurred.

Passing these criteria allows the package to be submitted for design acceptance. It does not automatically authorize implementation.

## 7. Separate implementation authorization

Any transition to `S3-IMPLEMENTATION` requires a distinct successor act:

**Proposed successor act:** `AURA-STAGE3-IMPL-001`

That act MUST specify its own competent issuer, baseline, target repositories and paths, permitted operations, acceptance criteria, rollback conditions, verification requirements, and constitutive authorization evidence.

This document MUST NOT be interpreted as creating or implying `AURA-STAGE3-IMPL-001`.

## 8. State machine

Permitted progression:

`NOT AUTHORIZED`  
→ `S3-DESIGN AUTHORIZED`  
→ `DESIGN ACCEPTED`

The first transition requires all of the following:
1. G0 baseline and SSOT reconciliation evidenced;
2. G1 authority and decision competence established for this act;
3. G2 ratification completed under the applicable mechanism;
4. the ratified artifact and required signature evidence registered and verified;
5. the effective state explicitly recorded by the competent authority.

Until every condition is satisfied, the effective state remains **`NOT AUTHORIZED`**.

## 9. Ratification and registration record — intentionally pending

- G1 authority / decision competence: `NOT PROVEN / BLOCKED`
- Competent issuer: `PENDING — NOT TO BE NAMED UNTIL G1 PASSES`
- Authority evidence reference for this act: `PENDING`
- Ratified artifact revision / digest: `PENDING`
- Ratification decision reference: `PENDING`
- Valid signature reference: `PENDING`
- Registration location and commit: `PENDING`
- Effective date: `PENDING`
- Independent verification result: `PENDING`

**Current determination:** `PROPOSED · G1 BLOCKED — AUTHORITY NOT PROVEN; RATIFICATION NOT YET ELIGIBLE`  
**Effective authorization:** `NONE`  
**Implementation authorization:** `NOT GRANTED`  
**Release / conformance authorization:** `NOT GRANTED`

---

**End of proposed act.**
