# GENUS EGG Versioning

GENUS EGG uses package versions for shipped repository states and EGG phase
labels for architecture milestones from the concept document.

## Current State

- Package version: `2.0.0`
- Architecture level: Complete first EGG plus first controlled capability
  activation
- Current boundary: draft needs, proposals, shadow plans, fitness scores,
  cockpit projections, readiness reports, patch draft records, and evidence
  records only; local Git status and preparation records are allowed, but no
  push, merge, rebase, non-draft GitHub action, autonomous activation, or
  runtime self-modification
- Next architecture target: post-2.0 physiology, resource economy,
  distributed Habitats, stronger inspection surfaces, and richer memory search

## History

- `0.0.2`: Initial EGG-v0 foundation through Reaction Core v0.2.
- `0.0.6`: Habitat Core, Maturation Seed, Development Boundary, and First
  Growth Simulation consolidated as draft-safe EGG-v0.
- `0.1.0`: Shadow Testing and Fitness Evaluation for existing draft
  `CodeChangeProposal` records.
- `0.2.0`: Read-only Inspection Cockpit for Memory, Ledger, Habitat,
  Observations, Needs, Proposals, Shadow Plans, and Fitness Scores.
- `0.3.0`: Habitat Contract v1 with ResourceSnapshot and readiness reporting.
- `0.4.0`: SandboxPatch Boundary with PatchApproval, SandboxPatch,
  PatchFileChange, and PatchRiskAssessment records.
- `0.5.0`: Controlled TestRunner, TestResult, EvidenceRecord, and EvidenceChain.
- `0.6.0`: Local GitConnector with read-only Git status and deterministic
  branch-preparation records.
- `0.7.0`: Draft-only GitHubConnector records gated by Habitat, approval, local
  Git preparation, and passing evidence.
- `0.8.0`: Activation Boundary with blocked requests, decisions, candidates,
  and runtime compatibility checks.
- `0.9.0`: Rollback plans, blocked capability activations, capability monitors,
  and fossil records.
- `1.0.0`: Complete first EGG consolidation for Desktop/Server Habitats.
- `2.0.0`: First controlled capability activation for SQLite-backed
  `index_memory`.

## Boundary

Version `2.0.0` may create memories through the deterministic Reaction Core,
may create draft needs, draft proposals, shadow test plans, and fitness
evaluations, may render read-only cockpit snapshots, and may store resource and
readiness records. It may create draft patch records after approval, read local
Git status, store deterministic local branch-preparation evidence, and store
draft-only GitHub PR records when explicitly allowed and evidenced. It may model
blocked activation requests and rejection decisions, rollback plans, blocked
capability activation records, monitoring records, and fossil records. It must
not create non-draft PRs, merge, auto-merge, mutate issues, change labels or
reviewers, touch secrets/permissions, activate runtime reactions, start
agents/workers, call an LLM, run arbitrary shell commands, introduce
vector/graph storage, or delete truth during fossilization. It may activate only
`index_memory` through explicit CLI approval after rollback data exists; memory
indexing is deterministic and SQLite-only.
