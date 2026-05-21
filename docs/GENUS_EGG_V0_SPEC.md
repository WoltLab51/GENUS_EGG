# GENUS EGG v0.0.6 Spec

## Goal

Implement and consolidate the first governed GENUS EGG slice through phase
`0.6`: Reaction Core, Habitat Core, Maturation Seed, Development Boundary, and
First Growth Simulation.

The system may remember deterministic user input, persist its local habitat,
record maturation observations, draft capability needs, draft development
proposals, and explain a growth proposal. It must not modify files, generate
patches, run Git/GitHub actions, register new runtime reactions, or activate
new capabilities.

```text
RawInput -> MeaningCandidate -> ValidationResult -> ReactionProduct -> MemoryObject
```

## CLI

- `genus-egg --version` prints the package version.
- `genus-egg remember "text"` creates a governed memory chain.
- `genus-egg memories` lists stored memory objects.
- `genus-egg ledger --chain CHAIN_ID` lists ledger entries for one chain.
- `genus-egg habitat` probes and stores the local habitat manifest.
- `genus-egg observations` lists maturation observations.
- `genus-egg needs` lists stored capability needs.
- `genus-egg needs draft-memory-indexing` creates a deterministic draft
  capability need without activation.
- `genus-egg needs detect` derives a draft memory-indexing need from existing
  observations when the PatternDetector sees the documented pattern.
- `genus-egg proposals` lists stored capability proposals.
- `genus-egg proposals draft-memory-indexing --need NEED_ID` creates draft-only
  development proposal objects from an existing need.
- `genus-egg growth simulate-memory-indexing --need NEED_ID` explains a
  draft-only `ReactionSpec index_memory` growth simulation with rationale and
  test plan.
- `--db PATH` selects the SQLite database; default is `data/genus_egg.sqlite`.

## Reaction Core v0.0-0.2

- `parse_user_input` requires `RawInput` and produces `MeaningCandidate`.
- `validate_meaning` requires `MeaningCandidate` and produces `ValidationResult`.
- `create_memory_proposal` requires an allowed validation and produces a
  `ReactionProduct` with `product_type=memory_proposal`.
- `create_memory` requires a memory proposal and produces `MemoryObject`.

If no reaction is enabled, the kernel stops with `no_enabled_reaction`.
If more than one reaction is enabled, the kernel stops with `ambiguous_reaction`.
There is no creative selection.

Successful `remember` persists this sequence and records seven ledger entries:

- `raw_input_recorded`
- `meaning_candidate_created`
- `validation_recorded`
- `reaction_recorded`
- `reaction_product_created`
- `memory_object_created`
- `chain_completed`

## Habitat Core v0.3

The Habitat Core is read-only and boundary-focused. `EnvironmentProbe` may read
environment metadata and persist a `HabitatManifest`; it may not alter the
environment.

The default v0.0.6 profile is:

- `network_allowed=false`
- `github_allowed=false`
- `model_access=local_stub`
- `allowed_write_paths=["./data", "./sandbox"]`
- `forbidden_paths=[".env", "secrets", ".git/config"]`
- `user_approval_required=true`

`PermissionProfile` blocks exact forbidden paths and forbidden subpaths.

## Maturation Seed v0.4

After a successful reaction chain, GENUS records:

- `ReactionOutcome`
- `ObservationRecord`

GENUS may draft a `CapabilityNeed` for memory indexing. Needs are stored with
`status=draft`; there is no activation, patch generation, Git operation, or
runtime mutation.

`PatternDetector` may inspect stored `ObservationRecord` data and derive the
same draft memory-indexing need from successful memory chains. It remains
draft-safe and does not create proposals unless an explicit CLI command asks
for the next draft object.

## Development Boundary v0.5

GENUS may turn an existing `CapabilityNeed` into:

- `CapabilityProposal`
- `CodeChangeProposal`

Both are draft objects. A `CodeChangeProposal` may only be created when the
referenced `CapabilityNeed` exists.

For `draft-memory-indexing`, the documented values are:

- title: `Add memory indexing reaction`
- rationale: `Repeated memory creation and retrieval would benefit from indexed lookup.`
- status: `draft`
- allowed paths: `["src/genus_egg/memory", "tests"]`
- forbidden paths: at least `.env`, `secrets`, `.git/config`

`ApprovalGate` blocks v0.0.6 activation:

- `can_modify_files(...) -> False`
- `can_activate(...) -> False`
- `assert_not_active(...)` blocks active changes

## First Growth Simulation v0.6

`genus-egg growth simulate-memory-indexing --need NEED_ID` creates the same
draft proposal chain through the Development Boundary and prints:

```text
Ich schlage eine neue ReactionSpec index_memory vor, weil Memory-Retrieval spaeter davon profitieren koennte.
```

The output includes proposal ID, code proposal ID, rationale, test plan,
`Patch: none`, `Git: none`, and `Activation: blocked`.

No patch is generated. No Git command is run. No runtime reaction is registered
or activated.

## Persistence

The v0.0.6 schema contains:

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

## Version Mapping

- Package `0.0.2`: EGG-v0 foundation through Reaction Core v0.2.
- Package `0.0.6`: consolidated EGG-v0 through phase v0.6, including Habitat
  Core, Maturation Seed, Development Boundary, and First Growth Simulation.
