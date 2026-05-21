# GENUS EGG Concept

GENUS is a governed digital reaction organism.

It is not a plain `User -> LLM -> Action` loop. The v0 shape is:

```text
Signal -> Meaning -> Validation -> Reaction -> Product -> Memory -> Ledger
```

The model may interpret in later versions. GENUS decides through governed,
deterministic reaction rules. This first EGG focuses on a stable core:

- a Reaction Core that turns approved inputs into artifacts,
- SQLite as the source of truth,
- an append-only ledger for chain history,
- strict safety boundaries before future maturation or development behavior.

The first usable behavior is memory creation through `remember`.
