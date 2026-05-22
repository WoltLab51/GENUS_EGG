# GENUS EGG Foundation Review

GENUS EGG `2.2.1` hardens and polishes the foundation without adding runtime
power.

## Stable Now

- SQLite remains the only source of truth.
- The ledger remains append-only through the public API.
- Successful `remember` chains still create exactly seven ledger entries.
- `index_memory` remains the only activatable capability.
- Memory indexing remains deterministic, SQLite-only, and activation-gated.
- `guide memory-indexing` remains an interaction layer and asks before
  activation.
- Guards are real minimal inhibitors with explicit reason codes.
- Validation rejects unsafe or incomplete meaning candidates instead of blindly
  allowing every write path.
- ReactionCube coordinates and ReactionGraph edges are explicit objects.
- ReactionCode is intentionally minimal: it models only `BLOCKED` and the
  current `memory_request + normal + ready` path, not a full 8x8x8 space.

## Not Implemented

- No LLM semantic parser.
- No free-language command interpretation.
- No clarification follow-up reaction.
- No workers, agents, GraphDB, vector store, embeddings, or background jobs.
- No new GitHub capability.
- No runtime self-modification.
- No generic plugin or activation framework.
- No broad foreign-key migration across existing SQLite databases.

## Invariants

- No memory without a `MeaningCandidate`.
- No memory without a `ValidationResult` with `result=allow`.
- No follow-up without an explicit `ReactionEdge`.
- No successful memory chain outside the documented reaction order.
- No duplicate `(chain_id, step)` ledger entry.
- No public ledger update/delete API.
- No activation without explicit approval and rollback data.
- No capability activation except `index_memory`.
- No source file writes, Git, GitHub, LLM, worker, GraphDB, embedding, or
  self-modification effect may pass the foundation guards.

## Boundaries

The EGG may remember, inspect, evaluate, draft records, and run bounded internal
checks. It may not become an autonomous developer, background worker, generic
semantic agent, or GitHub actor.

Clarification is intentionally not a reaction in `2.2.0`. If a meaning needs
clarification, validation rejects it with `needs_clarification`; future
conversation state needs a separate plan.

Foreign keys are intentionally not fully enabled in `2.2.0`. The current schema
has accumulated many persisted records across early phases, and broad FK
enforcement would be invasive for existing local SQLite files. This release
uses a unique ledger-step index, stable CHECK constraints for new databases,
and store-level invariant checks where compatibility matters.

## EGG And PiGenus Separation

GENUS EGG remains separate from PiGenus because EGG is the governed foundation:
its job is to prove reaction physics, memory, boundaries, evaluation, evidence,
rollback, and controlled activation. PiGenus can later adopt mature EGG
capabilities, but it should not absorb unstable foundation experiments directly.

## Adoption Readiness Checklist

- Full pytest is green.
- `remember "larumipsum"` still completes with seven ledger entries.
- Guards expose reason codes for blocked reactions.
- Invalid validation states are rejected.
- Ledger duplicate steps are blocked.
- Memory indexing activates only after explicit approval.
- The guide asks before activation.
- Safety documentation reflects current boundaries.
- CI runs Python 3.12 tests.

## CI Verification

The GitHub Actions `tests` workflow was verified on `main` for commit
`f675a395a0c07005fdf537a1026ca3c17c0ad19b`.

- Run: `https://github.com/WoltLab51/GENUS_EGG/actions/runs/26315204243`
- Status: `completed`
- Conclusion: `success`
