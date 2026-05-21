# Changelog

## 0.1.0 - 2026-05-21

- Added draft-safe Shadow Testing for existing `CodeChangeProposal` records.
- Added draft-safe Fitness Evaluation with fixed criteria and numeric scores.
- Added `shadow_test_plans` and `fitness_evaluations` SQLite tables.
- Added CLI commands:
  - `genus-egg shadow plan --code-proposal CODE_PROPOSAL_ID`
  - `genus-egg fitness evaluate --code-proposal CODE_PROPOSAL_ID`
  - `genus-egg fitness list`
- Kept runtime scope closed: no patch, file modification, Git/GitHub action,
  worker, dashboard, LLM call, or activation.

## 0.0.6 - 2026-05-21

- Consolidated GENUS EGG v0 through phase `0.6`.
- Documented Reaction Core, Habitat Core, Maturation Seed, Development
  Boundary, and Growth Simulation.
- Added explicit project status and safety boundaries for draft-safe Habitat,
  Maturation, and Development behavior.
- Kept runtime scope unchanged: no file modification, GitHub action, agent,
  worker, vector store, GraphDB, patch generation, or autonomous activation.

## 0.0.2 - 2026-05-21

- Added the initial EGG-v0 foundation through Reaction Core v0.2.
- Added SQLite persistence, append-only ledger, and deterministic
  `remember` memory creation.
