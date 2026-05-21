# GENUS EGG Concept

GENUS is a governed digital reaction organism.

It is not a plain `User -> LLM -> Action` loop. The v0 shape is:

```text
Signal -> Meaning -> Validation -> Reaction -> Product -> Memory -> Ledger
```

The model may interpret in later versions. GENUS decides through governed,
deterministic reaction rules. The consolidated `v0.0.6` EGG focuses on a
stable core:

- a Reaction Core that turns approved inputs into artifacts,
- a Habitat Core that observes local boundaries without acting,
- a Maturation Seed that records outcomes and draft needs,
- a Development Boundary that creates draft proposals but blocks activation,
- SQLite as the source of truth,
- an append-only ledger for chain history,
- strict safety boundaries before any future active development behavior.

The first usable behavior is memory creation through `remember`. Habitat,
Maturation, Development, and Growth behavior remains draft-safe only.
