# GENUS EGG

GENUS EGG is a minimal, governed reaction organism. Version `0.0-0.2`
implements the first deterministic slice:

```text
RawInput -> MeaningCandidate -> ValidationResult -> ReactionProduct -> MemoryObject
```

SQLite is the source of truth. The ledger is append-only. No model writes
directly, and no runtime self-modification exists in this version.

## Quick Start

```powershell
python -m genus_egg.cli --db data/genus_egg.sqlite remember "larumipsum"
python -m genus_egg.cli --db data/genus_egg.sqlite memories
python -m genus_egg.cli --db data/genus_egg.sqlite ledger --chain <chain_id>
```

After installing the project, the console entrypoint is also available:

```powershell
genus-egg --db data/genus_egg.sqlite remember "larumipsum"
```

## Development

```powershell
python -m pytest
```
