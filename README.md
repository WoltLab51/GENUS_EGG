# GENUS EGG

GENUS EGG `v0.0.6` is a minimal, governed reaction organism backed by
SQLite. This repository contains the consolidated EGG-v0 slice through phase
`0.6`: Reaction Core, Habitat Core, Maturation Seed, Development Boundary, and
the first draft-only Growth Simulation.

SQLite is the source of truth. The ledger is append-only. Habitat, Maturation,
Development, and Growth are draft-safe only: they may observe, store manifests,
create draft records, and explain proposals, but they do not modify files,
generate patches, run Git/GitHub actions, or activate new runtime behavior.

```text
RawInput -> MeaningCandidate -> ValidationResult -> ReactionProduct -> MemoryObject
```

## Components

## Reaction Core

`genus-egg remember "text"` runs the deterministic v0 reaction flow:

- store `RawInput`
- derive `MeaningCandidate`
- store `ValidationResult` with `result=allow`
- create a `ReactionProduct` memory proposal
- create a `MemoryObject`
- record the complete append-only ledger chain

The v0 flow does not use an LLM, network access, or creative reaction choice.
`remember` remains fixed at seven ledger entries for the successful chain.

## Habitat Core

`genus-egg habitat` probes the local environment and stores a
`HabitatManifest` in SQLite. It records OS, hostname, Python version, repository
path, data path, SQLite path, Git availability, and the default permission
profile.

Default boundaries stay closed:

- `network_allowed=false`
- `github_allowed=false`
- `model_access=local_stub`
- forbidden paths include `.env`, `secrets`, and `.git/config`

## Maturation Seed

Successful reaction chains create `ReactionOutcome` and `ObservationRecord`
data. Capability needs can be drafted from observations, but only as inert
SQLite objects with `status=draft`.

`genus-egg needs detect` may derive a draft memory-indexing need from existing
observations. Detection is still draft-safe: no activation, patch, Git, or
runtime registration follows from it.

## Development Boundary

The Development Boundary can turn an existing `CapabilityNeed` into draft-only
`CapabilityProposal` and `CodeChangeProposal` objects. `ApprovalGate` blocks
file modification and activation in v0.0.6.

`genus-egg proposals draft-memory-indexing --need <need_id>` creates proposal
records only. `genus-egg growth simulate-memory-indexing --need <need_id>`
adds an explainable Growth Simulation with rationale and test plan, while
printing `Patch: none`, `Git: none`, and `Activation: blocked`.

## CLI

All commands accept `--db PATH`; the default database is
`data/genus_egg.sqlite`.

```powershell
genus-egg --version
genus-egg --db data/genus_egg.sqlite remember "larumipsum"
genus-egg --db data/genus_egg.sqlite memories
genus-egg --db data/genus_egg.sqlite ledger --chain <chain_id>
genus-egg --db data/genus_egg.sqlite habitat
genus-egg --db data/genus_egg.sqlite observations
genus-egg --db data/genus_egg.sqlite needs
genus-egg --db data/genus_egg.sqlite needs draft-memory-indexing
genus-egg --db data/genus_egg.sqlite needs detect
genus-egg --db data/genus_egg.sqlite proposals
genus-egg --db data/genus_egg.sqlite proposals draft-memory-indexing --need <need_id>
genus-egg --db data/genus_egg.sqlite growth simulate-memory-indexing --need <need_id>
```

The same commands can also be run as a module during local development:

```powershell
python -m genus_egg.cli --db data/genus_egg.sqlite remember "larumipsum"
```

## Development

```powershell
.venv\Scripts\python.exe -m pytest
```
