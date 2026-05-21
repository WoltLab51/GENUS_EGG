# GENUS EGG Versioning

GENUS EGG uses package versions for shipped repository states and EGG phase
labels for architecture milestones from the concept document.

## Current State

- Package version: `0.4.0`
- Architecture level: EGG-v0 base plus Shadow/Fitness evaluation, read-only
  Inspection Cockpit, Habitat Contract v1, and SandboxPatch Boundary
- Current boundary: draft needs, proposals, shadow plans, fitness scores,
  cockpit projections, readiness reports, and patch draft records only; no
  patch application, Git, GitHub, file modification, autonomous activation, or
  runtime self-modification
- Next architecture target: TestRunner and EvidenceChain

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

## Boundary

Version `0.4.0` may create memories through the deterministic Reaction Core,
may create draft needs, draft proposals, shadow test plans, and fitness
evaluations, may render read-only cockpit snapshots, and may store resource and
readiness records. It may create draft patch records after approval. It must not
apply patches, run Git/GitHub actions, activate runtime reactions, modify files
through GENUS itself, start agents/workers, call an LLM, or introduce
vector/graph storage.
