from __future__ import annotations

from genus_egg.cockpit.cockpit_snapshot import CockpitSnapshot
from genus_egg.truth.sqlite_store import SQLiteStore


class CockpitDataAdapter:
    """Read-only adapter that projects SQLite truth into cockpit counters."""

    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def snapshot(self) -> CockpitSnapshot:
        latest_habitat = self.store.get_latest_habitat_manifest()
        fitness_evaluations = self.store.list_fitness_evaluations()
        latest_fitness = fitness_evaluations[-1] if fitness_evaluations else None
        return CockpitSnapshot(
            memory_count=len(self.store.list_memory_objects()),
            memory_index_entry_count=len(self.store.list_memory_index_entries()),
            ledger_entry_count=len(self.store.list_ledger_entries()),
            habitat_manifest_count=self.store.count_rows("habitat_manifest"),
            resource_snapshot_count=len(self.store.list_resource_snapshots()),
            habitat_readiness_report_count=len(
                self.store.list_habitat_readiness_reports()
            ),
            reaction_outcome_count=len(self.store.list_reaction_outcomes()),
            observation_count=len(self.store.list_observation_records()),
            capability_need_count=len(self.store.list_capability_needs()),
            capability_proposal_count=len(self.store.list_capability_proposals()),
            code_change_proposal_count=len(self.store.list_code_change_proposals()),
            shadow_plan_count=len(self.store.list_shadow_test_plans()),
            fitness_evaluation_count=len(fitness_evaluations),
            sandbox_patch_count=len(self.store.list_sandbox_patches()),
            patch_approval_count=len(self.store.list_patch_approvals()),
            test_run_count=len(self.store.list_test_runs()),
            evidence_record_count=len(self.store.list_evidence_records()),
            evidence_chain_count=len(self.store.list_evidence_chains()),
            git_status_count=len(self.store.list_git_status_reports()),
            git_preparation_count=len(self.store.list_git_branch_preparations()),
            github_draft_pr_count=len(self.store.list_github_draft_prs()),
            activation_request_count=len(self.store.list_activation_requests()),
            activation_decision_count=len(self.store.list_activation_decisions()),
            rollback_plan_count=len(self.store.list_rollback_plans()),
            capability_activation_count=len(self.store.list_capability_activations()),
            capability_monitor_count=len(self.store.list_capability_monitors()),
            fossil_record_count=len(self.store.list_fossil_records()),
            latest_habitat_id=latest_habitat.habitat_id if latest_habitat else None,
            latest_fitness_score=latest_fitness.score if latest_fitness else None,
            activation_state=self._activation_state(),
        )

    def _activation_state(self) -> str:
        return (
            "active"
            if any(
                activation.activation == "active"
                for activation in self.store.list_capability_activations()
            )
            else "blocked"
        )
