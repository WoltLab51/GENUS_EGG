# GENUS EGG v0.0-0.2 Spec

## Goal

Implement the first deterministic GENUS EGG flow:

```text
RawInput -> MeaningCandidate -> ValidationResult -> ReactionProduct -> MemoryObject
```

## CLI

- `genus-egg remember "text"` creates a memory chain.
- `genus-egg memories` lists stored memory objects.
- `genus-egg ledger --chain CHAIN_ID` lists ledger entries for one chain.
- `genus-egg habitat` probes and stores the local habitat manifest.
- `genus-egg observations` lists maturation observations.
- `genus-egg needs draft-memory-indexing` creates a deterministic draft
  capability need without activation.
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

The following tables are part of v0.0-0.2:

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
