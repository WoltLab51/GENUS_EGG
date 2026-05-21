# GENUS EGG Roadmap

## Phase 0.0 - Project Skeleton

- Create root project structure.
- Add `pyproject.toml`, `src/genus_egg`, `tests`, `README`, and docs.
- Definition of done: tests run, CLI starts, empty SQLite DB can be created.

## Phase 0.1 - SQLite + Ledger

- Add SQLite schema and storage layer.
- Add append-only ledger recording.
- Definition of done: raw input can be stored, ledger entry can be written,
  append-only behavior is tested.

## Phase 0.2 - Reaction Core v0

- Add `RawInput`, `MeaningCandidate`, `ValidationResult`, `ReactionSpec`,
  `ReactionRegistry`, `ReactionCube`, `ReactionGraph`, `ReactionKernel`, and
  `MemoryObject`.
- Definition of done: `genus-egg remember "larumipsum"` creates a memory object
  and full ledger chain.

## Later Phases

- Phase 0.3: Habitat Core v0 with `genus-egg habitat`, `HabitatManifest`,
  `EnvironmentProbe`, and `PermissionProfile`.
- Phase 0.4: Maturation Seed with `ReactionOutcome`, `ObservationRecord`, and
  draft-only `CapabilityNeed`.
- Phase 0.5: Development Boundary with draft `CapabilityProposal`,
  `CodeChangeProposal`, and blocking `ApprovalGate`.
- Phase 0.6: First Growth Simulation.
