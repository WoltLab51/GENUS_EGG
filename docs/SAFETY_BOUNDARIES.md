# Safety Boundaries

These rules are hard boundaries for GENUS EGG package version `0.2.0`.

- No model writes directly.
- No memory exists without a `MeaningCandidate`.
- No memory exists without a `ValidationResult` with `result=allow`.
- No product exists without a reaction.
- No follow-up exists without an explicit graph edge.
- No product becomes an implicit signal.
- The ledger is append-only.
- SQLite is the source of truth.
- The graph is projection, not truth.
- Habitat Core is read-only and stores manifests only.
- Maturation Seed is draft-safe only.
- Pattern detection may create draft capability needs only.
- The Development Boundary may create draft proposal objects only.
- Shadow Testing may create static draft plans only.
- Fitness Evaluation may create informational draft scores only.
- Inspection Cockpit is read-only and may create no records.
- `ApprovalGate` blocks file modification and activation.
- Growth Simulation creates no patch and runs no Git.
- Shadow Testing executes no code and writes no files.
- Fitness scores activate nothing.
- Cockpit rendering activates nothing and mutates nothing.
- There is no Development Core activation in this version.
- There is no file modification by GENUS runtime.
- There is no GitHub action, patch generation, auto-merge, agent, worker,
  dashboard, LLM call, vector store, GraphDB, or self-modifying runtime.
