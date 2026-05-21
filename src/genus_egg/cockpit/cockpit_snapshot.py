from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CockpitSnapshot:
    memory_count: int
    ledger_entry_count: int
    habitat_manifest_count: int
    reaction_outcome_count: int
    observation_count: int
    capability_need_count: int
    capability_proposal_count: int
    code_change_proposal_count: int
    shadow_plan_count: int
    fitness_evaluation_count: int
    latest_habitat_id: str | None
    latest_fitness_score: int | None
    activation_state: str
