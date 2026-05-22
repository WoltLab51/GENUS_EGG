# GENUS EGG Status

## Current Version

- Package version: `2.1.0`
- Architecture scope: Complete first EGG plus controlled `index_memory`
  capability activation and guided terminal interaction
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
- Habitat Contract v1: persisted `ResourceSnapshot` and
  `HabitatReadinessReport`
- SandboxPatch Boundary: explicit approval plus draft patch records only
- EvidenceChain: controlled test evidence for sandbox patch drafts
- Local GitConnector: read-only Git status plus blocked branch-preparation
  records for approved sandbox patches
- GitHubConnector: draft-PR-only records gated by Habitat, approval, local Git
  preparation, and passing evidence
- Activation Boundary: blocked activation requests, reaction spec candidates,
  compatibility checks, and explicit rejection decisions
- Monitoring/Fossilization/Rollback: rollback plans, blocked capability
  activation records, capability monitors, and fossil records
- Memory Indexing: first controlled active capability, explicit approval only
- Guided Interaction Layer: terminal guide for the safe memory-indexing chain

## Capability Matrix

| Capability | 2.1 status | Boundary |
| --- | --- | --- |
| Memory reaction | active | deterministic `remember`, seven ledger entries |
| Ledger | active | append-only |
| Habitat probe | active | read-only |
| Habitat readiness | active | informational only |
| Maturation observations | active | draft-safe |
| Capability needs | draft | no activation |
| Development proposals | draft | no file modification |
| Growth simulation | draft | no patch or Git |
| Shadow testing | draft | no execution |
| Fitness evaluation | draft | scores activate nothing |
| Inspection Cockpit | read-only | no writes |
| SandboxPatch | draft | approval required, no active application |
| Test evidence | bounded | internal checks only |
| Local GitConnector | bounded | local preparation records, no push/merge/rebase |
| GitHubConnector | draft-only | no non-draft PR, merge, labels, reviewers, secrets |
| Activation Boundary | modeled | blocked without explicit decision and rollback |
| RollbackPlan | record | no automatic rollback execution |
| Monitoring | record | observes only |
| Fossilization | record | deletes no truth |
| Memory indexing | active after approval | only `index_memory`, SQLite-only |
| Guided memory-indexing flow | interactive | prints IDs, asks before approval |

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

Habitat Contract v1 is observational. It records local physiology and readiness
status, but it does not open network, GitHub, patch, or activation authority.

SandboxPatch Boundary is draft-safe only. It creates patch records after
approval, but it does not write files, run Git, run GitHub, or activate code.

EvidenceChain is bounded to controlled internal checks. It is not a general
shell executor, and evidence never activates code by itself.

Local GitConnector is preparation-only. It may read status and record a
deterministic local branch preparation for an existing `SandboxPatch`, but it
does not push, merge, rebase, force-push, call GitHub, or activate code.

GitHubConnector is draft-only. It is blocked by default through
`github_allowed=false`; even when allowed, it creates only draft PR records and
never merges, auto-merges, mutates issues, changes labels/reviewers, touches
secrets/permissions, or activates code.

Activation Boundary is modeling-only. Activation requests require proposal,
approval, evidence, and fitness records, but remain blocked without rollback
data. Activation decisions can reject a request; no decision path activates code
in this version.

Rollback plans are required before an activation request can move from
`blocked` to `review_required`. CapabilityActivation records remain blocked
except the explicitly approved `index_memory` capability. Monitoring records
outcomes and boundary violations. Fossilization marks history without deleting
SQLite truth.

Memory indexing is the only active 2.x capability. It requires
`activation approve`, a `review_required` request, a `RollbackPlan`, and the
`index_memory` candidate. Backfill is synchronous and stored in SQLite.

The Guided Interaction Layer is a user-facing orchestration layer. It may create
the same draft/evidence/rollback records as the existing CLI chain, but it
activates only after an explicit `y` or `yes` answer and only through
`ActivationBoundary.approve(...)`. If approval is skipped, the prepared
`ActivationRequest` remains blocked.

## Explicitly Not Present

- no file modification by GENUS runtime
- no GitHub actions
- no agents or workers
- no vector store
- no GraphDB
- no active patch application
- no non-draft pull request
- no issue/label/reviewer automation
- no autonomous activation
- no activation without rollback data and explicit CLI approval
- no deletion of truth during fossilization
- no runtime self-modification
- no write-capable dashboard
- no LLM call
- no vector store

## Verification

Run the full test suite:

```powershell
.venv\Scripts\python.exe -m pytest
```
