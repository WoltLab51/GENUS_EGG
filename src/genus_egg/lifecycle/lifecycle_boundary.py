from __future__ import annotations

import json

from genus_egg.activation.activation_boundary import (
    ActivationRequestNotFoundError,
)
from genus_egg.evaluation.shadow_tester import CodeChangeProposalNotFoundError
from genus_egg.ids import new_id
from genus_egg.lifecycle.capability_activation import CapabilityActivation
from genus_egg.lifecycle.capability_monitor import CapabilityMonitor
from genus_egg.lifecycle.fossil_record import FossilRecord
from genus_egg.lifecycle.rollback_plan import RollbackPlan
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class RollbackPlanRequiredError(RuntimeError):
    pass


class LifecycleBoundary:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def create_rollback_plan(self, code_proposal_id: str) -> RollbackPlan:
        proposal = self.store.get_code_change_proposal(code_proposal_id)
        if proposal is None:
            raise CodeChangeProposalNotFoundError(
                f"CodeChangeProposal not found: {code_proposal_id}"
            )

        plan = RollbackPlan(
            rollback_plan_id=new_id("rollbackplan"),
            code_proposal_id=code_proposal_id,
            status="draft_ready",
            steps_json=json.dumps(
                [
                    "keep prior ReactionSpec available",
                    "disable candidate registration",
                    "preserve MemoryObject and Ledger truth",
                    "record rollback evidence before any future activation",
                ],
                sort_keys=True,
            ),
            payload_json=json.dumps(
                {"activation": "blocked", "deletes_truth": False}, sort_keys=True
            ),
            created_at=utc_now(),
        )
        self.store.save_rollback_plan(plan)
        return plan

    def monitor(self, code_proposal_id: str) -> CapabilityMonitor:
        proposal = self.store.get_code_change_proposal(code_proposal_id)
        if proposal is None:
            raise CodeChangeProposalNotFoundError(
                f"CodeChangeProposal not found: {code_proposal_id}"
            )
        outcomes = self.store.list_reaction_outcomes()
        error_count = len([outcome for outcome in outcomes if not outcome.success])
        boundary_violations = 0
        utility_score = 100 if outcomes and error_count == 0 else 50
        monitor = CapabilityMonitor(
            monitor_id=new_id("capmonitor"),
            code_proposal_id=code_proposal_id,
            reaction_outcome_count=len(outcomes),
            error_count=error_count,
            boundary_violation_count=boundary_violations,
            utility_score=utility_score,
            status="observed",
            payload_json=json.dumps(
                {
                    "activation": "blocked",
                    "observes_reaction_outcomes": True,
                    "deletes_truth": False,
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_capability_monitor(monitor)
        return monitor

    def record_activation_candidate(
        self, activation_request_id: str
    ) -> CapabilityActivation:
        request = next(
            (
                item
                for item in self.store.list_activation_requests()
                if item.activation_request_id == activation_request_id
            ),
            None,
        )
        if request is None:
            raise ActivationRequestNotFoundError(
                f"ActivationRequest not found: {activation_request_id}"
            )

        rollback_plan = self._latest_rollback_plan(request.code_proposal_id)
        if rollback_plan is None:
            raise RollbackPlanRequiredError("RollbackPlan required")

        activation = CapabilityActivation(
            capability_activation_id=new_id("capactivation"),
            activation_request_id=activation_request_id,
            code_proposal_id=request.code_proposal_id,
            rollback_plan_id=rollback_plan.rollback_plan_id,
            status="blocked",
            activation="blocked",
            payload_json=json.dumps(
                {
                    "active_runtime_change": False,
                    "monitoring_required": True,
                    "rollback_plan_required": True,
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_capability_activation(activation)
        return activation

    def fossilize(self, source_kind: str, source_id: str, reason: str) -> FossilRecord:
        fossil = FossilRecord(
            fossil_record_id=new_id("fossil"),
            source_kind=source_kind,
            source_id=source_id,
            reason=reason,
            status="fossilized",
            payload_json=json.dumps(
                {"deletes_truth": False, "activation": "blocked"}, sort_keys=True
            ),
            created_at=utc_now(),
        )
        self.store.save_fossil_record(fossil)
        return fossil

    def _latest_rollback_plan(self, code_proposal_id: str) -> RollbackPlan | None:
        plans = [
            plan
            for plan in self.store.list_rollback_plans()
            if plan.code_proposal_id == code_proposal_id
        ]
        return plans[-1] if plans else None
