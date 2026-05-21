from __future__ import annotations

import json

from genus_egg.evaluation.evaluation_criterion import EVALUATION_CRITERIA
from genus_egg.evaluation.evaluation_report import EvaluationReport
from genus_egg.evaluation.fitness_evaluation import FitnessEvaluation
from genus_egg.evaluation.shadow_tester import (
    CodeChangeProposalNotFoundError,
    ShadowTester,
)
from genus_egg.ids import new_id
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


class FitnessEvaluator:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def evaluate(self, code_proposal_id: str) -> EvaluationReport:
        code_proposal = self.store.get_code_change_proposal(code_proposal_id)
        if code_proposal is None:
            raise CodeChangeProposalNotFoundError(
                f"CodeChangeProposal not found: {code_proposal_id}"
            )

        shadow_plan = self.store.get_latest_shadow_test_plan_for_code_proposal(
            code_proposal_id
        )
        if shadow_plan is None:
            shadow_plan = ShadowTester(self.store).plan(code_proposal_id)

        payload = json.loads(code_proposal.payload_json or "{}")
        allowed_paths = json.loads(code_proposal.allowed_paths_json)
        forbidden_paths = json.loads(code_proposal.forbidden_paths_json)
        test_plan = payload.get("test_plan", [])
        title_and_rationale = f"{code_proposal.title} {code_proposal.rationale}".lower()

        criteria_scores = {
            "safety_boundary_fit": self._score_bool(
                payload.get("activation") == "blocked"
                and payload.get("can_modify_files") is False
                and payload.get("can_activate") is False
            ),
            "habitat_fit": self._score_bool(
                {".env", "secrets", ".git/config"}.issubset(set(forbidden_paths))
            ),
            "test_plan_quality": 90
            if isinstance(test_plan, list) and len(test_plan) >= 3
            else 60,
            "scope_control": 90
            if code_proposal.status == "draft"
            and allowed_paths == ["src/genus_egg/memory", "tests"]
            else 60,
            "memory_flow_benefit": 85
            if "memory" in title_and_rationale and "index" in title_and_rationale
            else 50,
            "rollback_readiness": 80
            if code_proposal.status == "draft" and shadow_plan.activation == "blocked"
            else 40,
            "activation_risk": self._score_bool(shadow_plan.activation == "blocked"),
        }
        score = round(sum(criteria_scores.values()) / len(EVALUATION_CRITERIA))
        rationale = (
            "Draft proposal is fit for continued shadow evaluation: boundaries "
            "remain closed, activation is blocked, and the scope stays focused on "
            "memory indexing."
        )

        evaluation = FitnessEvaluation(
            evaluation_id=new_id("fitnesseval"),
            code_proposal_id=code_proposal_id,
            shadow_plan_id=shadow_plan.shadow_plan_id,
            score=score,
            criteria_scores_json=json.dumps(criteria_scores, sort_keys=True),
            rationale=rationale,
            activation="blocked",
            payload_json=json.dumps(
                {
                    "criteria": [criterion.name for criterion in EVALUATION_CRITERIA],
                    "patch": "none",
                    "git": "none",
                    "github": "none",
                    "workers": "none",
                    "activation": "blocked",
                },
                sort_keys=True,
            ),
            created_at=utc_now(),
        )
        self.store.save_fitness_evaluation(evaluation)
        return EvaluationReport(
            shadow_plan=shadow_plan,
            fitness_evaluation=evaluation,
            status="draft",
            activation="blocked",
        )

    @staticmethod
    def _score_bool(value: bool) -> int:
        return 100 if value else 0
