from __future__ import annotations

import json

from genus_egg.activation.activation_decision import ActivationDecision
from genus_egg.activation.activation_request import ActivationRequest
from genus_egg.activation.reaction_spec_candidate import ReactionSpecCandidate
from genus_egg.activation.runtime_compatibility_check import RuntimeCompatibilityCheck
from genus_egg.evaluation.shadow_tester import CodeChangeProposalNotFoundError
from genus_egg.ids import new_id
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class ActivationPrerequisiteError(RuntimeError):
    pass


class ActivationRequestNotFoundError(RuntimeError):
    pass


class ActivationBoundary:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def request(
        self, code_proposal_id: str
    ) -> tuple[ActivationRequest, ReactionSpecCandidate, RuntimeCompatibilityCheck]:
        proposal = self.store.get_code_change_proposal(code_proposal_id)
        if proposal is None:
            raise CodeChangeProposalNotFoundError(
                f"CodeChangeProposal not found: {code_proposal_id}"
            )
        if not self._has_fitness(code_proposal_id):
            raise ActivationPrerequisiteError("FitnessEvaluation required")
        if not self._has_evidence_chain(code_proposal_id):
            raise ActivationPrerequisiteError("EvidenceChain required")
        if self.store.get_latest_patch_approval(code_proposal_id) is None:
            raise ActivationPrerequisiteError("PatchApproval required")
        rollback_plan = self._latest_rollback_plan(code_proposal_id)
        rollback_available = rollback_plan is not None
        reason_code = (
            "explicit_activation_decision_required"
            if rollback_available
            else "rollback_data_missing"
        )
        status = "review_required" if rollback_available else "blocked"

        request = ActivationRequest(
            activation_request_id=new_id("activationrequest"),
            code_proposal_id=code_proposal_id,
            status=status,
            reason_code=reason_code,
            activation="blocked",
            payload_json=json.dumps(
                {
                    "proposal": proposal.code_proposal_id,
                    "fitness_required": True,
                    "evidence_required": True,
                    "approval_required": True,
                    "rollback_required": True,
                    "rollback_available": rollback_available,
                    "rollback_plan_id": (
                        rollback_plan.rollback_plan_id if rollback_plan else None
                    ),
                    "score_activates": False,
                    "pr_activates": False,
                    "merge_activates": False,
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_activation_request(request)

        candidate = ReactionSpecCandidate(
            candidate_id=new_id("reactionspeccandidate"),
            activation_request_id=request.activation_request_id,
            name="index_memory",
            status="candidate_blocked",
            payload_json=json.dumps({"activation": "blocked"}, sort_keys=True),
            created_at=utc_now(),
        )
        self.store.save_reaction_spec_candidate(candidate)

        check = RuntimeCompatibilityCheck(
            compatibility_check_id=new_id("compatcheck"),
            activation_request_id=request.activation_request_id,
            status=status,
            reason_code=reason_code,
            payload_json=json.dumps(
                {
                    "runtime_mutation": "none",
                    "rollback_plan_required": True,
                    "activation": "blocked",
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_runtime_compatibility_check(check)
        return request, candidate, check

    def reject(self, activation_request_id: str, rationale: str) -> ActivationDecision:
        if not any(
            request.activation_request_id == activation_request_id
            for request in self.store.list_activation_requests()
        ):
            raise ActivationRequestNotFoundError(
                f"ActivationRequest not found: {activation_request_id}"
            )

        decision = ActivationDecision(
            activation_decision_id=new_id("activationdecision"),
            activation_request_id=activation_request_id,
            decision="rejected",
            status="final",
            activation="blocked",
            rationale=rationale,
            payload_json=json.dumps(
                {"fossilized": True, "runtime_change": "none"}, sort_keys=True
            ),
            created_at=utc_now(),
        )
        self.store.save_activation_decision(decision)
        return decision

    def _has_fitness(self, code_proposal_id: str) -> bool:
        return any(
            evaluation.code_proposal_id == code_proposal_id
            for evaluation in self.store.list_fitness_evaluations()
        )

    def _has_evidence_chain(self, code_proposal_id: str) -> bool:
        return any(
            chain.code_proposal_id == code_proposal_id
            for chain in self.store.list_evidence_chains()
        )

    def _latest_rollback_plan(self, code_proposal_id: str):
        plans = [
            plan
            for plan in self.store.list_rollback_plans()
            if plan.code_proposal_id == code_proposal_id
        ]
        return plans[-1] if plans else None
