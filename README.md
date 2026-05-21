# GENUS EGG

GENUS EGG is a minimal, governed reaction organism. The current implementation
covers phases `0.0-0.6`: deterministic memory reaction, habitat awareness,
maturation seed records, a blocked development boundary, and first growth
simulation.

```text
RawInput -> MeaningCandidate -> ValidationResult -> ReactionProduct -> MemoryObject
```

SQLite is the source of truth. The ledger is append-only. No model writes
directly, no patch is generated, and no runtime self-modification exists in
this version.

## Quick Start

```powershell
python -m genus_egg.cli --db data/genus_egg.sqlite remember "larumipsum"
python -m genus_egg.cli --db data/genus_egg.sqlite memories
python -m genus_egg.cli --db data/genus_egg.sqlite ledger --chain <chain_id>
python -m genus_egg.cli --db data/genus_egg.sqlite habitat
python -m genus_egg.cli --db data/genus_egg.sqlite observations
python -m genus_egg.cli --db data/genus_egg.sqlite needs draft-memory-indexing
python -m genus_egg.cli --db data/genus_egg.sqlite proposals draft-memory-indexing --need <need_id>
python -m genus_egg.cli --db data/genus_egg.sqlite growth simulate-memory-indexing --need <need_id>
```

After installing the project, the console entrypoint is also available:

```powershell
genus-egg --db data/genus_egg.sqlite remember "larumipsum"
genus-egg --db data/genus_egg.sqlite habitat
genus-egg --db data/genus_egg.sqlite observations
genus-egg --db data/genus_egg.sqlite needs draft-memory-indexing
genus-egg --db data/genus_egg.sqlite proposals draft-memory-indexing --need <need_id>
genus-egg --db data/genus_egg.sqlite growth simulate-memory-indexing --need <need_id>
```

## Development

```powershell
.venv\Scripts\python.exe -m pytest
```
