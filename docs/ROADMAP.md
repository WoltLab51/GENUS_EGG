# GENUS EGG Roadmap

## Completed Phases

## Phase 0.0 - Project Skeleton

- Create root project structure.
- Add `pyproject.toml`, `src/genus_egg`, `tests`, `README`, and docs.
- Definition of done: tests run, CLI starts, empty SQLite DB can be created.
- Status: completed in `fa06187`.

## Phase 0.1 - SQLite + Ledger

- Add SQLite schema and storage layer.
- Add append-only ledger recording.
- Definition of done: raw input can be stored, ledger entry can be written,
  append-only behavior is tested.
- Status: completed in `fa06187`.

## Phase 0.2 - Reaction Core v0

- Add `RawInput`, `MeaningCandidate`, `ValidationResult`, `ReactionSpec`,
  `ReactionRegistry`, `ReactionCube`, `ReactionGraph`, `ReactionKernel`, and
  `MemoryObject`.
- Definition of done: `genus-egg remember "larumipsum"` creates a memory object
  and full ledger chain.
- Status: completed in `fa06187`.

## Phase 0.3 - Habitat Core v0

- Add `genus-egg habitat`, `HabitatManifest`, `EnvironmentProbe`, and
  `PermissionProfile`.
- Definition of done: `genus-egg habitat` shows OS, repo path, SQLite path, Git
  availability, and `network_allowed`.
- Status: completed in `c3960f3`.

## Phase 0.4 - Maturation Seed

- Add `ReactionOutcome`, `ObservationRecord`, and draft-only `CapabilityNeed`.
- Definition of done: successful reaction chains create maturation records, and
  capability needs can be drafted without activation.
- Status: completed in `1fea84e`.

## Phase 0.5 - Development Boundary

- Add draft `CapabilityProposal`, `CodeChangeProposal`, and blocking
  `ApprovalGate`.
- Definition of done: GENUS can create draft proposal objects, cannot modify
  code, and activation remains blocked.
- Status: completed in `c4d2a82`.

## Next Phase

## Phase 0.6 - First Growth Simulation

- Simulate a memory indexing proposal.
- No patch.
- No Git.
- Only proposal, rationale, and test plan.
- Definition of done: GENUS can explain that it proposes a new
  `ReactionSpec index_memory` because memory retrieval would benefit from it.
- Status: next.
