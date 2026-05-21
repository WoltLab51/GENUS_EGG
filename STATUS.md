# GENUS EGG Status

## Current Version

- Package version: `0.2.0`
- Architecture scope: EGG-v0 base plus Shadow/Fitness evaluation and read-only
  Inspection Cockpit
- Persistence: SQLite is the only source of truth
- Ledger: append-only

## Implemented

- Reaction Core: active deterministic `remember` flow
- Habitat Core: read-only environment probe plus persisted `HabitatManifest`
- Maturation Seed: persisted outcomes, observations, and draft capability needs
- Development Boundary: draft proposals plus blocking `ApprovalGate`
- Growth Simulation: explainable draft proposal chain with no patch and no Git
- Shadow Testing: persisted `ShadowTestPlan` objects for code proposals
- Fitness Evaluation: persisted scores and rationales with activation blocked
- Inspection Cockpit: read-only local projection over SQLite truth

## Draft-Safe Boundaries

Habitat Core is observing and boundary-focused only. It does not change the
environment, enable network access, or run GitHub actions.

Maturation Seed is draft-safe only. It may record observations and draft
capability needs, but it does not activate capabilities.

Development Boundary is draft-safe only. It may create `CapabilityProposal` and
`CodeChangeProposal` records, but `ApprovalGate` blocks file modification and
activation.

Shadow Testing is draft-safe only. It creates static review plans and does not
execute code, write files, create patches, or run Git/GitHub.

Fitness Evaluation is draft-safe only. Scores and rationales are informational;
they do not activate proposals.

Inspection Cockpit is read-only only. It renders local visibility from SQLite
and does not write records, trigger routes, run workers, or call Git/GitHub.

## Explicitly Not Present

- no file modification by GENUS runtime
- no GitHub actions
- no agents or workers
- no vector store
- no GraphDB
- no patch generation
- no autonomous activation
- no runtime self-modification
- no write-capable dashboard
- no LLM call

## Verification

Run the full test suite:

```powershell
.venv\Scripts\python.exe -m pytest
```
