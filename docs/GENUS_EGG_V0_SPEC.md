# GENUS EGG v0 Spec

## Goal

Implement the first governed GENUS EGG v0 slice through phase `0.6`:

```text
RawInput -> MeaningCandidate -> ValidationResult -> ReactionProduct -> MemoryObject
```

The current system also records Habitat, Maturation Seed, Development Boundary,
Growth Simulation, and first PatternDetector artifacts, but it does not activate
new capabilities or modify code.

## CLI

- `genus-egg remember "text"` creates a memory chain.
- `genus-egg memories` lists stored memory objects.
- `genus-egg ledger --chain CHAIN_ID` lists ledger entries for one chain.
- `genus-egg habitat` probes and stores the local habitat manifest.
- `genus-egg observations` lists maturation observations.
- `genus-egg needs draft-memory-indexing` creates a deterministic draft
  capability need without activation.
- `genus-egg needs detect` uses the PatternDetector to derive a draft
  `CapabilityNeed` from stored observations.
- `genus-egg proposals draft-memory-indexing --need NEED_ID` creates draft-only
  development proposal objects without activation.
- `genus-egg growth simulate-memory-indexing --need NEED_ID` explains a
  draft-only `ReactionSpec index_memory` growth simulation with rationale and
  test plan.
- `--db PATH` selects the SQLite database; default is `data/genus_egg.sqlite`.

## Reaction Rules

- `parse_user_input` requires `RawInput` and produces `MeaningCandidate`.
- `validate_meaning` requires `MeaningCandidate` and produces `ValidationResult`.
- `create_memory_proposal` requires an allowed validation and produces a
  `ReactionProduct` with `product_type=memory_proposal`.
- `create_memory` requires a memory proposal and produces `MemoryObject`.

If no reaction is enabled, the kernel stops with `no_enabled_reaction`.
If more than one reaction is enabled, the kernel stops with `ambiguous_reaction`.
There is no creative selection.

## Persistence

The following tables are part of the current v0 schema:

- `raw_inputs`
- `meaning_candidates`
- `validation_results`
- `reactions`
- `reaction_products`
- `memory_objects`
- `ledger_entries`
- `habitat_manifest`
- `reaction_outcomes`
- `observation_records`
- `capability_needs`
- `capability_proposals`
- `code_change_proposals`

SQLite is the only source of truth. JSON payloads are stored as text.

## Habitat v0.3

The Habitat Core is read-only and boundary-focused. It records OS, repository
path, SQLite path, Git availability, network permission, GitHub permission, and
the default permission profile. Network and GitHub access default to false.

## Maturation Seed v0.4

After a successful reaction chain, GENUS records a `ReactionOutcome` and an
`ObservationRecord`. A deterministic `CapabilityNeed` can be created as
`draft`, but no activation, patch generation, Git operation, or runtime mutation
is allowed.

## Development Boundary v0.5

GENUS may turn an existing `CapabilityNeed` into draft-only
`CapabilityProposal` and `CodeChangeProposal` records. The `ApprovalGate` blocks
file modification and activation. No code patch, Git operation, runtime mutation,
or automatic activation is allowed.

## First Growth Simulation v0.6

GENUS can explain: `Ich schlage eine neue ReactionSpec index_memory vor, weil Memory-Retrieval später davon profitieren könnte.`
The simulation stores only draft proposal objects and a test plan. It creates no
patch, runs no Git command, and does not register or activate a runtime reaction.

## PatternDetector EGG v0.1

The PatternDetector scans existing `ObservationRecord` data and can derive the
draft memory indexing `CapabilityNeed` from observed successful memory chains.
It does not activate the need, write code, create patches, or run Git.
