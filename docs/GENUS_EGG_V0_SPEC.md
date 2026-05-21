# GENUS EGG v0/v0.3 Spec

## Goal

GENUS EGG `0.3.0` extends the consolidated EGG-v0 base, v0.1 evaluation layer,
and read-only Inspection Cockpit with Habitat Contract v1.

The system may remember deterministic user input, persist its local habitat,
record maturation observations, draft capability needs, draft development
proposals, explain a growth proposal, create shadow test plans, score draft
proposals, render local inspection snapshots, and assess habitat readiness. It
must not modify files, generate patches, run Git/GitHub actions, execute
proposal code, register new runtime reactions, or activate new capabilities.

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
- `--db PATH` selects the SQLite database; default is `data/genus_egg.sqlite`.

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

## Persistence

The `0.3.0` schema contains:

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
