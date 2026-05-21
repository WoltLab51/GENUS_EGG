from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FitnessEvaluation:
    evaluation_id: str
    code_proposal_id: str
    shadow_plan_id: str
    score: int
    criteria_scores_json: str
    rationale: str
    activation: str
    payload_json: str | None
    created_at: str
