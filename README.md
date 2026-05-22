# GENUS EGG

GENUS EGG `2.2.0` is a governed reaction organism backed by SQLite. Version
2.2 hardens the foundation without adding new runtime power. Version 2.1 added
a guided interaction layer for the controlled `index_memory` flow.
Version 2.0 added the first controlled capability activation: `index_memory`.

GENUS EGG 1.0 established the complete first EGG: a minimal, governed reaction
organism backed by SQLite. It can react, remember, observe, inspect its Habitat,
form draft needs and proposals, plan shadow tests, evaluate fitness, prepare
SandboxPatch records after approval, store evidence, prepare local Git and
draft-only GitHub PR records behind boundaries, model activation requests, and
keep rollback, monitoring, and fossilization records.

SQLite is the source of truth. The ledger is append-only. GENUS may remember,
observe, draft, simulate, shadow-test, evaluate proposals, render local
inspection snapshots, assess its habitat readiness, draft sandbox patch objects
after explicit approval, read local Git status, and store deterministic local
branch-preparation records. It can prepare a draft-only GitHub PR record when
the Habitat explicitly allows GitHub and evidence is present. It can model
activation requests and rejection decisions. In 2.0+, GENUS may activate only
`index_memory`, only through explicit CLI approval, and only after rollback data
exists. In 2.2, Guards are real minimal inhibitors with reason codes, validation
rejects unsafe write-path meanings, and SQLite/Ledger invariants are stronger.
GENUS still may not merge, auto-merge, create non-draft PRs, mutate issues,
change labels or reviewers, touch secrets/permissions, start workers, call an
LLM, activate arbitrary capabilities, or rewrite its active core live.

The core rule remains:

```text
GENUS merged nicht eigenmaechtig,
aktiviert nicht eigenmaechtig
und veraendert seinen aktiven Kern nicht live.
```

```text
RawInput -> MeaningCandidate -> ValidationResult -> ReactionProduct -> MemoryObject
```

```text
CapabilityNeed -> CapabilityProposal -> CodeChangeProposal
-> ShadowTestPlan -> FitnessEvaluation -> EvaluationReport
```

## Components

## Reaction Core

`genus-egg remember "text"` runs the deterministic v0 reaction flow:

- store `RawInput`
- derive `MeaningCandidate`
- store `ValidationResult` with `result=allow`
- create a `ReactionProduct` memory proposal
- create a `MemoryObject`
- record the complete append-only ledger chain

The v0 flow does not use an LLM, network access, or creative reaction choice.
`remember` remains fixed at seven ledger entries for the successful chain.
The explicit `remember` command uses `CommandParseAdapter`; free-language
semantic parsing is not implemented.

## Foundation Guards

Foundation Guards are deterministic inhibitors. They return
`GuardDecision(allow, reason_code)` and block missing content, low confidence,
non-allow validation, wrong continuation policy, unknown reactions, and
forbidden effects such as file writes, Git, GitHub, LLM calls, workers,
GraphDB, embeddings, or runtime self-modification.

Validation is conservative: only `memory_request` with non-empty content, high
confidence, and no clarification need is allowed. Clarification is not a
follow-up reaction in 2.2; it rejects with `needs_clarification`.

## Habitat Core

`genus-egg habitat` probes the local environment and stores a
`HabitatManifest` in SQLite. It records OS, hostname, Python version, repository
path, data path, SQLite path, Git availability, and the default permission
profile.

Default boundaries stay closed:

- `network_allowed=false`
- `github_allowed=false`
- `model_access=local_stub`
- forbidden paths include `.env`, `secrets`, and `.git/config`

`genus-egg habitat readiness` stores a `ResourceSnapshot` and
`HabitatReadinessReport` with `ready`, `limited`, or `blocked` status. The
resource snapshot records CPU count, CPU label, memory visibility, disk
capacity/free space, and `temperature=unknown` when no safe sensor is available.

## Maturation Seed

Successful reaction chains create `ReactionOutcome` and `ObservationRecord`
data. Capability needs can be drafted from observations, but only as inert
SQLite objects with `status=draft`.

`genus-egg needs detect` may derive a draft memory-indexing need from existing
observations. Detection is still draft-safe: no activation, patch, Git, or
runtime registration follows from it.

## Development Boundary

The Development Boundary can turn an existing `CapabilityNeed` into draft-only
`CapabilityProposal` and `CodeChangeProposal` objects. `ApprovalGate` blocks
file modification and activation.

`genus-egg proposals draft-memory-indexing --need <need_id>` creates proposal
records only. `genus-egg growth simulate-memory-indexing --need <need_id>`
adds an explainable Growth Simulation with rationale and test plan, while
printing `Patch: none`, `Git: none`, and `Activation: blocked`.

## Shadow Testing

`genus-egg shadow plan --code-proposal <code_proposal_id>` creates a
`ShadowTestPlan` for an existing `CodeChangeProposal`. The plan is a persisted
static review object. It does not execute code, write files, create patches, run
Git/GitHub, or activate anything.

## Fitness Evaluation

`genus-egg fitness evaluate --code-proposal <code_proposal_id>` evaluates a
draft `CodeChangeProposal` and its `ShadowTestPlan` against fixed criteria:

- `safety_boundary_fit`
- `habitat_fit`
- `test_plan_quality`
- `scope_control`
- `memory_flow_benefit`
- `rollback_readiness`
- `activation_risk`

The score is numeric from `0` to `100`, stored in SQLite, and never activates
the proposal. `genus-egg fitness list` lists stored evaluations.

## Inspection Cockpit

The Inspection Cockpit is a read-only projection over SQLite truth. It provides
a `CockpitDataAdapter` for counters across Memories, Ledger, Habitat,
Observations, Needs, Proposals, Shadow Plans, and Fitness Scores, plus a small
HTML renderer for local inspection.

The cockpit does not expose writes, routes, workers, auth, cloud sync, Git,
GitHub, patch creation, or activation.

## SandboxPatch Boundary

`genus-egg patch approve --code-proposal <code_proposal_id>` stores explicit
approval for a draft sandbox patch. `genus-egg patch draft --code-proposal
<code_proposal_id>` creates `SandboxPatch`, `PatchFileChange`, and
`PatchRiskAssessment` records only after approval.

No patch is applied to the working tree. No Git or GitHub action is run.
Activation remains blocked.

## EvidenceChain

`genus-egg tests run --patch <patch_id>` runs the controlled internal
`sandbox_patch_static_check` and stores `TestRun`, `TestResult`,
`EvidenceRecord`, and `EvidenceChain` records. `genus-egg evidence list` shows
stored evidence.

The runner is not a general shell executor. Evidence can improve Fitness
Evaluation context, but still activates nothing.

## Local GitConnector

`genus-egg git status` stores a read-only `GitStatusReport` with current branch,
dirty state, head commit, and remotes for the selected repository path.

`genus-egg git prepare-branch --patch <patch_id>` requires an existing
`SandboxPatch`, blocks dirty working trees, derives a deterministic branch name,
stores a `GitBranchPreparation`, and records Evidence. It does not push, merge,
rebase, force-push, run GitHub, or activate anything.

## GitHubConnector

`genus-egg github draft-pr --patch <patch_id>` is draft-only and blocked by
default because `github_allowed=false` in the default Habitat. When an explicit
Habitat record allows GitHub, the connector still requires a `SandboxPatch`,
local branch preparation, and passing Evidence before it stores a
`GitHubDraftPr`.

The GitHub connector records the draft-PR boundary in SQLite. It does not create
non-draft PRs, merge, auto-merge, mutate issues, change labels or reviewers,
touch secrets/permissions, or activate anything.

## Activation Boundary

`genus-egg activation request --code-proposal <code_proposal_id>` models an
activation request only after proposal, approval, evidence, and fitness records
exist. The request remains `Status: blocked` with
`Reason: rollback_data_missing`.

`genus-egg activation reject --request <request_id>` stores a blocked
`ActivationDecision`. Scores, PR records, merges, and approvals never activate
runtime behavior by themselves.

`genus-egg activation approve --request <request_id>` is the first active
capability gate. It allows only the `index_memory` candidate, requires a
`review_required` activation request and a `RollbackPlan`, stores an approved
decision, creates an active `CapabilityActivation`, and backfills the memory
index.

## Memory Indexing

After `index_memory` is approved, existing memories are indexed once and new
`remember` calls are indexed automatically after `MemoryObject` storage. This
index is SQLite-only and deterministic: no embeddings, no vector store, no
network, and no LLM.

`genus-egg memory search "query"` searches indexed memories. `genus-egg memory
index-status` shows whether indexing is active and how many memories are
indexed.

## Guided Interaction Layer

`genus-egg guide memory-indexing` runs a terminal Lotsenmodus for the full
safe `index_memory` chain. It creates the existing draft/evidence/rollback
records through their normal boundaries, prints every generated ID, and then
asks:

```text
Approve index_memory activation? [y/N]
```

Only `y` or `yes` calls the existing activation approval boundary. Any other
answer leaves the prepared `ActivationRequest` blocked and prints the manual
next command. If `index_memory` is already active, the guide creates no new
chain and prints the current index status plus a safe search command.

## Monitoring, Fossilization, And Rollback

`genus-egg rollback plan --code-proposal <code_proposal_id>` stores a
`RollbackPlan`. With rollback data present, activation requests can become
`review_required`, but activation remains blocked.

`genus-egg monitor capability --code-proposal <code_proposal_id>` records a
`CapabilityMonitor` with reaction outcomes, errors, boundary violations, and a
simple utility score. `genus-egg monitor activation --request <request_id>`
stores a blocked `CapabilityActivation` record only when a rollback plan exists.

`genus-egg fossilize record --source-kind KIND --source-id ID` stores a
`FossilRecord`. Fossilization marks history and never deletes SQLite truth.

## CLI

All commands accept `--db PATH`; the default database is
`data/genus_egg.sqlite`.
The Git commands also accept `--repo PATH`; the default repository path is `.`.

```powershell
genus-egg --version
genus-egg --db data/genus_egg.sqlite remember "larumipsum"
genus-egg --db data/genus_egg.sqlite memories
genus-egg --db data/genus_egg.sqlite ledger --chain <chain_id>
genus-egg --db data/genus_egg.sqlite habitat
genus-egg --db data/genus_egg.sqlite habitat readiness
genus-egg --db data/genus_egg.sqlite observations
genus-egg --db data/genus_egg.sqlite needs
genus-egg --db data/genus_egg.sqlite needs draft-memory-indexing
genus-egg --db data/genus_egg.sqlite needs detect
genus-egg --db data/genus_egg.sqlite proposals
genus-egg --db data/genus_egg.sqlite proposals draft-memory-indexing --need <need_id>
genus-egg --db data/genus_egg.sqlite growth simulate-memory-indexing --need <need_id>
genus-egg --db data/genus_egg.sqlite shadow plan --code-proposal <code_proposal_id>
genus-egg --db data/genus_egg.sqlite fitness evaluate --code-proposal <code_proposal_id>
genus-egg --db data/genus_egg.sqlite fitness list
genus-egg --db data/genus_egg.sqlite patch approve --code-proposal <code_proposal_id>
genus-egg --db data/genus_egg.sqlite patch draft --code-proposal <code_proposal_id>
genus-egg --db data/genus_egg.sqlite patch list
genus-egg --db data/genus_egg.sqlite tests run --patch <patch_id>
genus-egg --db data/genus_egg.sqlite evidence list
genus-egg --db data/genus_egg.sqlite git status
genus-egg --db data/genus_egg.sqlite git prepare-branch --patch <patch_id>
genus-egg --db data/genus_egg.sqlite github draft-pr --patch <patch_id>
genus-egg --db data/genus_egg.sqlite activation request --code-proposal <code_proposal_id>
genus-egg --db data/genus_egg.sqlite activation reject --request <request_id>
genus-egg --db data/genus_egg.sqlite activation approve --request <request_id>
genus-egg --db data/genus_egg.sqlite activation list
genus-egg --db data/genus_egg.sqlite memory index-status
genus-egg --db data/genus_egg.sqlite memory search "larum"
genus-egg --db data/genus_egg.sqlite guide memory-indexing
genus-egg --db data/genus_egg.sqlite rollback plan --code-proposal <code_proposal_id>
genus-egg --db data/genus_egg.sqlite rollback list
genus-egg --db data/genus_egg.sqlite monitor capability --code-proposal <code_proposal_id>
genus-egg --db data/genus_egg.sqlite monitor activation --request <request_id>
genus-egg --db data/genus_egg.sqlite monitor list
genus-egg --db data/genus_egg.sqlite fossilize record --source-kind KIND --source-id ID
genus-egg --db data/genus_egg.sqlite fossilize list
```

The same commands can also be run as a module during local development:

```powershell
python -m genus_egg.cli --db data/genus_egg.sqlite remember "larumipsum"
```

## Development

```powershell
.venv\Scripts\python.exe -m pytest
```
