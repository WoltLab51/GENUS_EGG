# GENUS EGG Concept

GENUS is a governed digital reaction organism.

It is not a plain `User -> LLM -> Action` loop. The v0 shape is:

```text
Signal -> Meaning -> Validation -> Reaction -> Product -> Memory -> Ledger
```

The model may interpret in later versions. GENUS decides through governed,
deterministic reaction rules. The current `2.2.0` EGG contains a stable core,
its evaluation layer, the first controlled active capability, a guided terminal
interaction layer, and hardened foundation boundaries:

- a Reaction Core that turns approved inputs into artifacts,
- a Habitat Core that observes local boundaries without acting,
- a Maturation Seed that records outcomes and draft needs,
- a Development Boundary that creates draft proposals but blocks activation,
- a ShadowTester that plans static checks without executing code,
- a FitnessEvaluator that scores proposals without activating them,
- an Activation Boundary that can approve only `index_memory` after explicit
  CLI approval and rollback data,
- a deterministic SQLite Memory Index for activated memory lookup,
- a guided `memory-indexing` flow that carries IDs and asks before activation,
- deterministic Guards and conservative validation for the write path,
- SQLite as the source of truth,
- an append-only ledger for chain history,
- strict safety boundaries before any future active development behavior.

The first usable behavior is memory creation through `remember`. The first
controlled active capability is `index_memory`; all other Habitat, Maturation,
Development, Growth, Shadow Testing, Fitness, Git, GitHub, and Activation
surfaces remain bounded by explicit records and safety gates.
