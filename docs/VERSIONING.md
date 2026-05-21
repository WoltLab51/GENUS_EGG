# GENUS EGG Versioning

GENUS EGG uses package versions for shipped repository states and EGG phase
labels for architecture milestones from the concept document.

## Current State

- Package version: `0.2.0`
- Architecture level: EGG-v0 base plus v0.1 Shadow/Fitness evaluation and v0.2
  read-only Inspection Cockpit
- Current boundary: draft needs, proposals, shadow plans, fitness scores, and
  cockpit projections only; no patch, Git, GitHub, file modification,
  autonomous activation, or runtime self-modification
- Next architecture target: Habitat Contract v1 and ResourceSnapshot

## History

- `0.0.2`: Initial EGG-v0 foundation through Reaction Core v0.2.
- `0.0.6`: Habitat Core, Maturation Seed, Development Boundary, and First
  Growth Simulation consolidated as draft-safe EGG-v0.
- `0.1.0`: Shadow Testing and Fitness Evaluation for existing draft
  `CodeChangeProposal` records.
- `0.2.0`: Read-only Inspection Cockpit for Memory, Ledger, Habitat,
  Observations, Needs, Proposals, Shadow Plans, and Fitness Scores.

## Boundary

Version `0.2.0` may create memories through the deterministic Reaction Core,
may create draft needs, draft proposals, shadow test plans, and fitness
evaluations, and may render read-only cockpit snapshots. It must not create
patches, run Git/GitHub actions, activate runtime reactions, modify files
through GENUS itself, start agents/workers, call an LLM, or introduce
vector/graph storage.
