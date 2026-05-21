# GENUS EGG Versioning

GENUS EGG uses package versions for shipped repository states and EGG phase
labels for architecture milestones from the concept document.

## Current State

- Package version: `0.6.0`
- Architecture level: EGG-v0 base plus Shadow/Fitness evaluation, read-only
  Inspection Cockpit, Habitat Contract v1, SandboxPatch Boundary, and
  EvidenceChain, and Local GitConnector
- Current boundary: draft needs, proposals, shadow plans, fitness scores,
  cockpit projections, readiness reports, patch draft records, and evidence
  records only; local Git status and preparation records are allowed, but no
  push, merge, rebase, GitHub, autonomous activation, or runtime
  self-modification
- Next architecture target: Draft-only GitHubConnector

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

## Boundary

Version `0.6.0` may create memories through the deterministic Reaction Core,
may create draft needs, draft proposals, shadow test plans, and fitness
evaluations, may render read-only cockpit snapshots, and may store resource and
readiness records. It may create draft patch records after approval, read local
Git status, and store deterministic local branch-preparation evidence. It must
not push, merge, rebase, force-push, call GitHub, activate runtime reactions,
modify files through GENUS itself, start agents/workers, call an LLM, run
arbitrary shell commands, or introduce vector/graph storage.
