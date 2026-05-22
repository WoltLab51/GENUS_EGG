# Safety Boundaries

These rules are hard boundaries for GENUS EGG package version `2.1.0`.

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
- Habitat readiness is informational and grants no permissions.
- SandboxPatch records require explicit PatchApproval.
- SandboxPatch records are not applied to the working tree.
- TestRunner is limited to controlled internal checks, not arbitrary shell.
- Evidence records are informational and activate nothing.
- Local GitConnector may read status and store preparation records only.
- Local GitConnector must not push, merge, rebase, force-push, call GitHub, or
  activate code.
- GitHubConnector is blocked unless `github_allowed=true`, user approval,
  passing evidence, and local Git preparation exist.
- GitHubConnector may store draft PR records only.
- GitHubConnector must not create non-draft PRs, merge, auto-merge, mutate
  issues, change labels/reviewers, touch secrets/permissions, or activate code.
- Activation Boundary may model requests, candidates, compatibility checks,
  rejection decisions, and the explicit `index_memory` approval path only.
- Activation requests stay blocked without rollback data.
- Scores, PR records, merges, approvals, and evidence never activate code by
  themselves.
- Rollback plans are records and do not execute rollback by themselves.
- CapabilityActivation records remain blocked except the explicitly approved
  `index_memory` activation.
- Monitoring observes outcomes and boundary violations only.
- Fossilization records history and must not delete truth.
- `index_memory` is the only activatable capability in this version.
- `index_memory` requires explicit CLI approval and rollback data.
- Memory indexing is SQLite-only: no LLM, no vector store, no GraphDB.
- Guided interaction is orchestration only; it may carry IDs and explain the
  safe chain, but it must use existing boundaries.
- `guide memory-indexing` must ask before activation and treat any answer other
  than `y` or `yes` as blocked.
- `guide memory-indexing` must not create a second activation chain when
  `index_memory` is already active.
- `ApprovalGate` blocks file modification and activation.
- Growth Simulation creates no patch and runs no Git.
- Shadow Testing executes no code and writes no files.
- Fitness scores activate nothing.
- Cockpit rendering activates nothing and mutates nothing.
- There is no Development Core activation in this version.
- There is no file modification by GENUS runtime.
- There is no non-draft GitHub action, active patch application, auto-merge,
  agent, worker, write-capable dashboard, LLM call, vector store, GraphDB, or
  self-modifying runtime.
