# GENUS EGG Status

## Current Version

- Package version: `0.0.6`
- Architecture scope: consolidated EGG-v0 phases `0.0-0.6`
- Persistence: SQLite is the only source of truth
- Ledger: append-only

## Implemented

- Reaction Core: active deterministic `remember` flow
- Habitat Core: read-only environment probe plus persisted `HabitatManifest`
- Maturation Seed: persisted outcomes, observations, and draft capability needs
- Development Boundary: draft proposals plus blocking `ApprovalGate`
- Growth Simulation: explainable draft proposal chain with no patch and no Git

## Draft-Safe Boundaries

Habitat Core is observing and boundary-focused only. It does not change the
environment, enable network access, or run GitHub actions.

Maturation Seed is draft-safe only. It may record observations and draft
capability needs, but it does not activate capabilities.

Development Boundary is draft-safe only. It may create `CapabilityProposal` and
`CodeChangeProposal` records, but `ApprovalGate` blocks file modification and
activation.

## Explicitly Not Present

- no file modification by GENUS runtime
- no GitHub actions
- no agents or workers
- no vector store
- no GraphDB
- no patch generation
- no autonomous activation
- no runtime self-modification

## Verification

Run the full test suite:

```powershell
.venv\Scripts\python.exe -m pytest
```
