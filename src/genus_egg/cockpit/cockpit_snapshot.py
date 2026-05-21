from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CockpitSnapshot:
    memory_count: int
    ledger_entry_count: int
    habitat_manifest_count: int
    resource_snapshot_count: int
    habitat_readiness_report_count: int
    reaction_outcome_count: int
    observation_count: int
    capability_need_count: int
    capability_proposal_count: int
    code_change_proposal_count: int
    shadow_plan_count: int
    fitness_evaluation_count: int
    sandbox_patch_count: int
    patch_approval_count: int
    test_run_count: int
    evidence_record_count: int
    evidence_chain_count: int
    git_status_count: int
    git_preparation_count: int
    github_draft_pr_count: int
    latest_habitat_id: str | None
    latest_fitness_score: int | None
    activation_state: str
