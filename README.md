# GENUS EGG

GENUS EGG `v0.4.0` is a minimal, governed reaction organism backed by SQLite.
It contains the consolidated EGG-v0 base, the v0.1 evaluation layer, the
read-only Inspection Cockpit, Habitat Contract v1, and the SandboxPatch
Boundary.

SQLite is the source of truth. The ledger is append-only. GENUS may remember,
observe, draft, simulate, shadow-test, evaluate proposals, render local
inspection snapshots, assess its habitat readiness, and draft sandbox patch
objects after explicit approval. It still may not modify files, apply patches,
run Git/GitHub actions, start workers, call an LLM, or activate new runtime
behavior.

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

## CLI

All commands accept `--db PATH`; the default database is
`data/genus_egg.sqlite`.

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
```

The same commands can also be run as a module during local development:

```powershell
python -m genus_egg.cli --db data/genus_egg.sqlite remember "larumipsum"
```

## Development

```powershell
.venv\Scripts\python.exe -m pytest
```
