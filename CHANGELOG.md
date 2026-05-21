# Changelog

## 0.8.0 - 2026-05-21

- Added Activation Boundary models: `ActivationRequest`,
  `ActivationDecision`, `ReactionSpecCandidate`, and
  `RuntimeCompatibilityCheck`.
- Added SQLite tables for activation requests, decisions, candidates, and
  compatibility checks.
- Added `genus-egg activation request`, `genus-egg activation reject`, and
  `genus-egg activation list`.
- Required proposal, approval, evidence, and fitness records before activation
  requests can be modeled.
- Kept activation blocked without rollback data; scores, PR records, and
  approvals activate nothing.

## 0.7.0 - 2026-05-21

- Added draft-only GitHubConnector boundary.
- Added `GitHubDraftPr` records and the `github_draft_prs` SQLite table.
- Added `genus-egg github draft-pr --patch PATCH_ID`.
- Required `github_allowed=true`, existing sandbox patch approval, local Git
  preparation, and passing evidence before draft-PR records can be stored.
- Extended the Inspection Cockpit to include GitHub draft PR counts.
- Kept GitHub strictly bounded: no non-draft PR, merge, auto-merge, issue
  mutation, labels, reviewers, secrets, permissions, or activation.

## 0.6.0 - 2026-05-21

- Added Local GitConnector with read-only `GitStatusReport` storage.
- Added `GitBranchPreparation` records for existing sandbox patches.
- Added SQLite tables for Git status and branch-preparation records.
- Added `genus-egg git status` and `genus-egg git prepare-branch --patch PATCH_ID`.
- Extended the Inspection Cockpit to include local Git status and preparation
  counts.
- Kept Git bounded: no push, merge, rebase, force-push, GitHub action, or
  activation.

## 0.5.0 - 2026-05-21

- Added controlled TestRunner for sandbox patch static checks.
- Added `TestRun`, `TestResult`, `EvidenceRecord`, and `EvidenceChain`.
- Added SQLite tables for test and evidence records.
- Added `genus-egg tests run --patch PATCH_ID` and `genus-egg evidence list`.
- Fitness Evaluation now references stored evidence when present.
- Kept tests internal and bounded: no arbitrary shell executor and no
  activation.

## 0.4.0 - 2026-05-21

- Added SandboxPatch Boundary with explicit `PatchApproval`.
- Added `SandboxPatch`, `PatchFileChange`, and `PatchRiskAssessment` records.
- Added SQLite tables for patch approvals, draft patches, file changes, and
  risk assessments.
- Added `genus-egg patch approve`, `genus-egg patch draft`, and
  `genus-egg patch list`.
- Kept patches as records only: no file writes, no Git, no GitHub, and no
  activation.

## 0.3.0 - 2026-05-21

- Added Habitat Contract v1 with `ResourceSnapshot` and
  `HabitatReadinessReport`.
- Added SQLite tables for resource snapshots and readiness reports.
- Added `genus-egg habitat readiness`.
- Extended the Inspection Cockpit to include resource and readiness counts.
- Kept habitat probing read-only; readiness remains informational and
  activation stays blocked.

## 0.2.0 - 2026-05-21

- Added read-only Inspection Cockpit data projection.
- Added local HTML rendering for Cockpit snapshots.
- Added tests proving the Cockpit reads Memories, Ledger, Habitat,
  Observations, Needs, Proposals, Shadow Plans, and Fitness Scores without
  writing to SQLite.
- Kept runtime scope closed: no auth, cloud, worker, patch, Git/GitHub, or
  activation.

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
