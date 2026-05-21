# GENUS EGG Roadmap

## Current Version

- Package version: `0.7.0`
- Architecture level: EGG-v0 base plus Shadow/Fitness evaluation, read-only
  Inspection Cockpit, Habitat Contract v1, SandboxPatch Boundary, and
  EvidenceChain, Local GitConnector, and draft-only GitHubConnector.
- Current boundary: draft needs, proposals, shadow plans, fitness scores,
  cockpit projections, readiness reports, patch draft records, and evidence
  records only; local Git status, preparation records, and draft-only GitHub PR
  records are allowed when gated, but no merge, auto-merge, non-draft PR,
  issue mutation, worker, or activation.

## Completed Phases

## Phase 0.0 - Project Skeleton

- Create root project structure.
- Add `pyproject.toml`, `src/genus_egg`, `tests`, `README`, and docs.
- Definition of done: tests run, CLI starts, empty SQLite DB can be created.
- Status: completed in `fa06187`.

## Phase 0.1 - SQLite + Ledger

- Add SQLite schema and storage layer.
- Add append-only ledger recording.
- Definition of done: raw input can be stored, ledger entry can be written,
  append-only behavior is tested.
- Status: completed in `fa06187`.

## Phase 0.2 - Reaction Core v0

- Add `RawInput`, `MeaningCandidate`, `ValidationResult`, `ReactionSpec`,
  `ReactionRegistry`, `ReactionCube`, `ReactionGraph`, `ReactionKernel`, and
  `MemoryObject`.
- Definition of done: `genus-egg remember "larumipsum"` creates a memory object
  and full ledger chain.
- Status: completed in `fa06187`.

## Phase 0.3 - Habitat Core v0

- Add `genus-egg habitat`, `HabitatManifest`, `EnvironmentProbe`, and
  `PermissionProfile`.
- Definition of done: `genus-egg habitat` shows OS, repo path, SQLite path, Git
  availability, and `network_allowed`.
- Status: completed in `c3960f3`.

## Phase 0.4 - Maturation Seed

- Add `ReactionOutcome`, `ObservationRecord`, and draft-only `CapabilityNeed`.
- Definition of done: successful reaction chains create maturation records, and
  capability needs can be drafted without activation.
- Status: completed in `1fea84e`.

## Phase 0.5 - Development Boundary

- Add draft `CapabilityProposal`, `CodeChangeProposal`, and blocking
  `ApprovalGate`.
- Definition of done: GENUS can create draft proposal objects, cannot modify
  code, and activation remains blocked.
- Status: completed in `c4d2a82`.

## Phase 0.6 - First Growth Simulation

- Simulate a memory indexing proposal.
- No patch.
- No Git.
- Only proposal, rationale, and test plan.
- Definition of done: GENUS can explain that it proposes a new
  `ReactionSpec index_memory` because memory retrieval would benefit from it.
- Status: completed in `5b8b294`.

## Draft-Safe Pattern Detection

- Add PatternDetector as a draft-safe observation reader.
- Add CapabilityNeed detection from stored observations.
- Definition of done: `genus-egg needs detect` can derive a draft memory
  indexing need from successful memory-chain observations without activation.
- Status: completed in `8b6b808`.

## GENUS EGG v0.1 - ShadowTester and FitnessEvaluator

- Add ShadowTester.
- Add FitnessEvaluator.
- Add `ShadowTestPlan`.
- Add `FitnessEvaluation`.
- Definition of done: GENUS can create static shadow plans and informational
  fitness scores for existing `CodeChangeProposal` records without executing
  code, writing files, creating patches, running Git/GitHub, or activating
  anything.
- Status: completed in current v0.1 work.

## GENUS EGG v0.2 - Inspection Cockpit

- Show Memory, Ledger, Observations, Needs, Proposals, Shadow Plans, and
  Fitness Scores.
- Keep the cockpit read-only unless a later plan explicitly opens a new
  approval boundary.
- Status: completed in current v0.2 work.

## GENUS EGG v0.3 - Habitat Contract v1

- Add ResourceSnapshot.
- Add HabitatReadinessReport.
- Add ready, limited, and blocked readiness status.
- Status: completed in current v0.3 work.

## Next Phase

## GENUS EGG v0.4 - SandboxPatch after Approval

- Add PatchApproval, SandboxPatch, PatchFileChange, and PatchRiskAssessment.
- Keep patch creation blocked without explicit approval.
- Status: completed in current v0.4 work.

## GENUS EGG v0.5 - TestRunner and EvidenceChain

- Add TestRun, TestResult, EvidenceRecord, and EvidenceChain.
- Link Evidence to FitnessEvaluation.
- Status: completed in current v0.5 work.

## GENUS EGG v0.6 - Local GitConnector

- Add read-only Git status.
- Prepare local branches only after approval.
- No push, merge, rebase, or force-push.
- Status: completed in current v0.6 work.

## Next Phase

## GENUS EGG v0.7 - GitHubConnector Draft PR Only

- Add GitHub metadata checks and draft-PR-only boundary.
- Require `github_allowed=true`, user approval, green tests, and evidence.
- No merge, auto-merge, issue mutation, labels, reviewers, secrets, or
  permission changes.
- Status: completed in current v0.7 work.

## Next Phase

## GENUS EGG v0.8 - Activation Boundary

- Add ActivationRequest, ActivationDecision, ReactionSpecCandidate, and
  RuntimeCompatibilityCheck.
- Keep activation blocked unless explicit decision prerequisites are modeled.
- Score, merge, and PR records activate nothing by themselves.
- Status: next.
