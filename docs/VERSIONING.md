# GENUS EGG Versioning

GENUS EGG uses package versions for shipped repository states and EGG phase
labels for architecture milestones from the concept document.

## Current State

- Package version: `0.1.0`
- Architecture level: EGG-v0 base plus v0.1 Shadow Testing and Fitness
  Evaluation
- Current boundary: draft needs, proposals, shadow plans, and fitness scores
  only; no patch, Git, GitHub, file modification, autonomous activation, or
  runtime self-modification
- Next architecture target: inspection cockpit or later approval workflow,
  still without autonomous activation unless explicitly planned

## History

- `0.0.2`: Initial EGG-v0 foundation through Reaction Core v0.2.
- `0.0.6`: Habitat Core, Maturation Seed, Development Boundary, and First
  Growth Simulation consolidated as draft-safe EGG-v0.
- `0.1.0`: Shadow Testing and Fitness Evaluation for existing draft
  `CodeChangeProposal` records.

## Boundary

Version `0.1.0` may create memories through the deterministic Reaction Core and
may create draft needs, draft proposals, shadow test plans, and fitness
evaluations. It must not create patches, run Git/GitHub actions, activate
runtime reactions, modify files through GENUS itself, start agents/workers,
call an LLM, or introduce vector/graph storage.
