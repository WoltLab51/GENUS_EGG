# GENUS EGG v0/v0.8 Spec

## Goal

GENUS EGG `0.8.0` extends the consolidated EGG-v0 base, v0.1 evaluation layer,
read-only Inspection Cockpit, and Habitat Contract v1 with a SandboxPatch
Boundary, EvidenceChain, Local GitConnector, draft-only GitHubConnector, and
Activation Boundary.

The system may remember deterministic user input, persist its local habitat,
record maturation observations, draft capability needs, draft development
proposals, explain a growth proposal, create shadow test plans, score draft
proposals, render local inspection snapshots, assess habitat readiness, and
draft sandbox patch records after approval. It may read local Git status and
store deterministic branch-preparation records. It must not push, merge,
rebase, force-push, run GitHub actions, execute arbitrary commands, register
new runtime reactions, or activate new capabilities. GitHub remains blocked by
default and draft-only when explicitly allowed. Activation remains modeled and
blocked unless a later phase adds rollback-backed decision paths.

```text
RawInput -> MeaningCandidate -> ValidationResult -> ReactionProduct -> MemoryObject
```

```text
CapabilityNeed -> CapabilityProposal -> CodeChangeProposal
-> ShadowTestPlan -> FitnessEvaluation -> EvaluationReport
```

## CLI

- `genus-egg --version` prints the package version.
- `genus-egg remember "text"` creates a governed memory chain.
- `genus-egg memories` lists stored memory objects.
- `genus-egg ledger --chain CHAIN_ID` lists ledger entries for one chain.
- `genus-egg habitat` probes and stores the local habitat manifest.
- `genus-egg habitat readiness` stores a resource snapshot and readiness report.
- `genus-egg observations` lists maturation observations.
- `genus-egg needs` lists stored capability needs.
- `genus-egg needs draft-memory-indexing` creates a deterministic draft
  capability need without activation.
- `genus-egg needs detect` derives a draft memory-indexing need from existing
  observations when the PatternDetector sees the documented pattern.
- `genus-egg proposals` lists stored capability proposals.
- `genus-egg proposals draft-memory-indexing --need NEED_ID` creates draft-only
  development proposal objects from an existing need.
- `genus-egg growth simulate-memory-indexing --need NEED_ID` explains a
  draft-only `ReactionSpec index_memory` growth simulation with rationale and
  test plan.
- `genus-egg shadow plan --code-proposal CODE_PROPOSAL_ID` creates a
  draft-only `ShadowTestPlan`.
- `genus-egg fitness evaluate --code-proposal CODE_PROPOSAL_ID` stores a
  draft-only `FitnessEvaluation`.
- `genus-egg fitness list` lists stored fitness evaluations.
- `genus-egg patch approve --code-proposal CODE_PROPOSAL_ID` stores explicit
  approval for a sandbox patch draft.
- `genus-egg patch draft --code-proposal CODE_PROPOSAL_ID` stores draft-only
  sandbox patch records.
- `genus-egg patch list` lists stored sandbox patches.
- `genus-egg tests run --patch PATCH_ID` runs the controlled internal
  `sandbox_patch_static_check`.
- `genus-egg evidence list` lists stored evidence records.
- `genus-egg git status` stores and prints a read-only local Git status report.
- `genus-egg git prepare-branch --patch PATCH_ID` stores a deterministic local
  branch-preparation record for an existing `SandboxPatch`.
- `genus-egg github draft-pr --patch PATCH_ID` stores a draft-only GitHub PR
  boundary record when all prerequisites pass.
- `genus-egg activation request --code-proposal CODE_PROPOSAL_ID` stores a
  blocked activation request when proposal, approval, evidence, and fitness
  records exist.
- `genus-egg activation reject --request REQUEST_ID` stores a blocked rejection
  decision.
- `genus-egg activation list` lists stored activation requests.
- `--db PATH` selects the SQLite database; default is `data/genus_egg.sqlite`.
- `genus-egg git ... --repo PATH` selects the local repository path for Git
  inspection; default is `.`.

## Reaction Core v0.0-0.2

- `parse_user_input` requires `RawInput` and produces `MeaningCandidate`.
- `validate_meaning` requires `MeaningCandidate` and produces `ValidationResult`.
- `create_memory_proposal` requires an allowed validation and produces a
  `ReactionProduct` with `product_type=memory_proposal`.
- `create_memory` requires a memory proposal and produces `MemoryObject`.

If no reaction is enabled, the kernel stops with `no_enabled_reaction`.
If more than one reaction is enabled, the kernel stops with `ambiguous_reaction`.
There is no creative selection.

Successful `remember` persists this sequence and records seven ledger entries:

- `raw_input_recorded`
- `meaning_candidate_created`
- `validation_recorded`
- `reaction_recorded`
- `reaction_product_created`
- `memory_object_created`
- `chain_completed`

## Habitat Core v0.3

The Habitat Core is read-only and boundary-focused. `EnvironmentProbe` may read
environment metadata and persist a `HabitatManifest`; it may not alter the
environment.

The default profile is:

- `network_allowed=false`
- `github_allowed=false`
- `model_access=local_stub`
- `allowed_write_paths=["./data", "./sandbox"]`
- `forbidden_paths=[".env", "secrets", ".git/config"]`
- `user_approval_required=true`

`PermissionProfile` blocks exact forbidden paths and forbidden subpaths.

## Maturation Seed v0.4

After a successful reaction chain, GENUS records:

- `ReactionOutcome`
- `ObservationRecord`

GENUS may draft a `CapabilityNeed` for memory indexing. Needs are stored with
`status=draft`; there is no activation, patch generation, Git operation, or
runtime mutation.

`PatternDetector` may inspect stored `ObservationRecord` data and derive the
same draft memory-indexing need from successful memory chains. It remains
draft-safe and does not create proposals unless an explicit CLI command asks
for the next draft object.

## Development Boundary v0.5

GENUS may turn an existing `CapabilityNeed` into:

- `CapabilityProposal`
- `CodeChangeProposal`

Both are draft objects. A `CodeChangeProposal` may only be created when the
referenced `CapabilityNeed` exists.

For `draft-memory-indexing`, the documented values are:

- title: `Add memory indexing reaction`
- rationale: `Repeated memory creation and retrieval would benefit from indexed lookup.`
- status: `draft`
- allowed paths: `["src/genus_egg/memory", "tests"]`
- forbidden paths: at least `.env`, `secrets`, `.git/config`

`ApprovalGate` blocks activation:

- `can_modify_files(...) -> False`
- `can_activate(...) -> False`
- `assert_not_active(...)` blocks active changes

## First Growth Simulation v0.6

`genus-egg growth simulate-memory-indexing --need NEED_ID` creates the same
draft proposal chain through the Development Boundary and prints:

```text
Ich schlage eine neue ReactionSpec index_memory vor, weil Memory-Retrieval spaeter davon profitieren koennte.
```

The output includes proposal ID, code proposal ID, rationale, test plan,
`Patch: none`, `Git: none`, and `Activation: blocked`.

No patch is generated. No Git command is run. No runtime reaction is registered
or activated.

## Shadow Testing v0.1

`ShadowTester` accepts an existing `CodeChangeProposal` and creates a
`ShadowTestPlan`. It reads persisted proposal data and stores a static plan for
review. It does not execute code, write files, generate patches, call Git or
GitHub, start workers, or activate anything.

Each plan is stored with:

- `status=draft`
- `activation=blocked`
- fixed static-review checks for all evaluation criteria
- payload markers `patch=none`, `git=none`, `github=none`

If the referenced `CodeChangeProposal` does not exist, planning stops with a
clear error and stores nothing.

## Fitness Evaluation v0.1

`FitnessEvaluator` evaluates an existing `CodeChangeProposal` and its latest
`ShadowTestPlan`. If no plan exists yet, it creates a draft shadow plan first.

The fixed criteria are:

- `safety_boundary_fit`
- `habitat_fit`
- `test_plan_quality`
- `scope_control`
- `memory_flow_benefit`
- `rollback_readiness`
- `activation_risk`

The evaluation stores:

- numeric score from `0` to `100`
- per-criterion numeric scores
- textual rationale
- `activation=blocked`
- payload markers `patch=none`, `git=none`, `github=none`, `workers=none`

Scores do not activate anything. They are informational draft-safe records.

## Inspection Cockpit v0.2

`CockpitDataAdapter` reads SQLite truth and projects counts for Memories,
Ledger, Habitat, Reaction Outcomes, Observations, Needs, Proposals, Shadow
Plans, and Fitness Evaluations.

`CockpitHtmlRenderer` renders the snapshot into a local HTML inspection view.
It is read-only: no route, renderer, or adapter writes to SQLite, starts
workers, runs Git/GitHub, creates patches, or activates proposals.

## Habitat Contract v0.3

`HabitatContract` creates a `ResourceSnapshot` from safe local reads and a
`HabitatReadinessReport` with status `ready`, `limited`, or `blocked`.

The resource snapshot records CPU count, CPU label, total/available memory when
visible, disk total/free space, and `temperature=unknown` when no safe sensor is
available.

Readiness is deterministic and informational. It can mark a Habitat as ready,
limited, or blocked, but it grants no permissions and activates nothing.

## SandboxPatch Boundary v0.4

`SandboxPatchBoundary` can create `PatchApproval` records for existing
`CodeChangeProposal` records. A `SandboxPatch` can only be drafted when an
approved `PatchApproval` exists.

The patch draft stores:

- `SandboxPatch`
- `PatchRiskAssessment`
- `PatchFileChange`

Patch targets must be inside the proposal allowed paths and outside forbidden
paths. The boundary stores proposed file changes only; it does not write files,
apply patches, run Git, call GitHub, or activate anything.

## TestRunner and EvidenceChain v0.5

`TestRunner` is bounded to the internal `sandbox_patch_static_check`. It is not
a general shell executor.

For a `SandboxPatch`, it stores:

- `TestRun`
- `TestResult`
- `EvidenceRecord`
- `EvidenceChain`

`FitnessEvaluator` references stored evidence when it evaluates a related
`CodeChangeProposal`. Evidence improves traceability, but it does not activate
the proposal.

## Local GitConnector v0.6

`LocalGitConnector` can read local Git metadata and persist:

- `GitStatusReport`
- `GitBranchPreparation`

`genus-egg git status` reads the selected repository path and stores current
branch, dirty state, head commit, remotes, and a `git=read_only` payload.

`genus-egg git prepare-branch --patch PATCH_ID` requires an existing
`SandboxPatch`, blocks dirty working trees, derives a deterministic
`genus/sandbox-...` branch name, stores the preparation record, and creates an
`EvidenceRecord` documenting the preparation. It does not push, merge, rebase,
force-push, call GitHub, or activate anything.

## GitHubConnector v0.7

`GitHubConnector` is blocked by default because the Habitat default is
`github_allowed=false`.

`genus-egg github draft-pr --patch PATCH_ID` requires:

- an existing `SandboxPatch`
- the patch approval that created the sandbox patch
- latest Habitat with `github_allowed=true`
- local `GitBranchPreparation`
- passing TestRunner evidence

When those prerequisites exist, the connector stores:

- `GitHubDraftPr`

The stored record has `is_draft=true` and `activation=blocked`. Its payload
explicitly keeps `push=none`, `merge=none`, `auto_merge=none`,
`issue_mutation=none`, `labels=none`, `reviewers=none`, `secrets=none`, and
`permissions=none`.

The connector offers no non-draft PR path, no merge path, no issue mutation, no
labels/reviewers, no secret or permission changes, and no activation.

## Activation Boundary v0.8

`ActivationBoundary` models activation as its own explicit, blocked lifecycle.

It can store:

- `ActivationRequest`
- `ActivationDecision`
- `ReactionSpecCandidate`
- `RuntimeCompatibilityCheck`

An activation request requires an existing `CodeChangeProposal`, a
`PatchApproval`, an `EvidenceChain`, and a `FitnessEvaluation`. Missing
prerequisites stop the request and store nothing.

Even with prerequisites present, the request is stored with:

- `status=blocked`
- `reason_code=rollback_data_missing`
- `activation=blocked`

The runtime compatibility check also remains blocked until rollback data exists.
Scores, PR records, merges, approvals, and evidence do not activate anything by
themselves.

Rejection stores an `ActivationDecision` with `decision=rejected` and
`activation=blocked`; this can mark the request as fossilized in payload data
without deleting history.

## Persistence

The `0.8.0` schema contains:

- `raw_inputs`
- `meaning_candidates`
- `validation_results`
- `reactions`
- `reaction_products`
- `memory_objects`
- `ledger_entries`
- `habitat_manifest`
- `resource_snapshots`
- `habitat_readiness_reports`
- `reaction_outcomes`
- `observation_records`
- `capability_needs`
- `capability_proposals`
- `code_change_proposals`
- `shadow_test_plans`
- `fitness_evaluations`
- `patch_approvals`
- `patch_risk_assessments`
- `sandbox_patches`
- `patch_file_changes`
- `test_runs`
- `test_results`
- `evidence_records`
- `evidence_chains`
- `git_status_reports`
- `git_branch_preparations`
- `github_draft_prs`
- `activation_requests`
- `activation_decisions`
- `reaction_spec_candidates`
- `runtime_compatibility_checks`

SQLite is the only source of truth. JSON payloads are stored as text.

## Version Mapping

- Package `0.0.2`: EGG-v0 foundation through Reaction Core v0.2.
- Package `0.0.6`: consolidated EGG-v0 through phase v0.6, including Habitat
  Core, Maturation Seed, Development Boundary, and First Growth Simulation.
- Package `0.1.0`: Shadow Testing and Fitness Evaluation for existing draft
  `CodeChangeProposal` records.
- Package `0.2.0`: Read-only Inspection Cockpit over SQLite truth.
- Package `0.3.0`: Habitat Contract v1 with ResourceSnapshot and
  HabitatReadinessReport.
- Package `0.4.0`: SandboxPatch Boundary with explicit approval and draft patch
  records only.
- Package `0.5.0`: Controlled TestRunner and EvidenceChain.
- Package `0.6.0`: Local GitConnector status and branch-preparation records.
- Package `0.7.0`: Draft-only GitHubConnector records gated by Habitat,
  approval, local Git preparation, and passing evidence.
- Package `0.8.0`: Activation Boundary with blocked requests, decisions,
  candidates, and compatibility checks.
