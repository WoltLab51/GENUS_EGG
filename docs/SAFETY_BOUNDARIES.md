# Safety Boundaries

These rules are hard boundaries for GENUS EGG v0 through the current phase
`0.5`:

- No model writes directly.
- No memory exists without a `MeaningCandidate`.
- No memory exists without a `ValidationResult` with `result=allow`.
- No product exists without a reaction.
- No follow-up exists without an explicit graph edge.
- No product becomes an implicit signal.
- The ledger is append-only.
- SQLite is the source of truth.
- The graph is projection, not truth.
- The Development Boundary may create draft proposal objects only.
- `ApprovalGate` blocks file modification and activation.
- There is no Development Core activation in this version.
- There is no GitHub action, patch generation, auto-merge, or self-modifying runtime.
