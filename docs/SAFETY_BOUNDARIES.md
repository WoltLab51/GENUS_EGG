# Safety Boundaries

These rules are hard boundaries for GENUS EGG package version `0.8.0`.

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
- Activation Boundary may model requests, candidates, compatibility checks, and
  rejection decisions only.
- Activation requests stay blocked without rollback data.
- Scores, PR records, merges, approvals, and evidence never activate code by
  themselves.
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
