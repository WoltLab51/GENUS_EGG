# GENUS EGG Concept

GENUS is a governed digital reaction organism.

It is not a plain `User -> LLM -> Action` loop. The v0 shape is:

```text
Signal -> Meaning -> Validation -> Reaction -> Product -> Memory -> Ledger
```

The model may interpret in later versions. GENUS decides through governed,
deterministic reaction rules. The current `v0.1.0` EGG contains a stable core
and its first evaluation layer:

- a Reaction Core that turns approved inputs into artifacts,
- a Habitat Core that observes local boundaries without acting,
- a Maturation Seed that records outcomes and draft needs,
- a Development Boundary that creates draft proposals but blocks activation,
- a ShadowTester that plans static checks without executing code,
- a FitnessEvaluator that scores proposals without activating them,
- SQLite as the source of truth,
- an append-only ledger for chain history,
- strict safety boundaries before any future active development behavior.

The first usable behavior is memory creation through `remember`. Habitat,
Maturation, Development, Growth, Shadow Testing, and Fitness Evaluation remain
draft-safe only.
