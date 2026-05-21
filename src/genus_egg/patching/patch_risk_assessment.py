from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PatchRiskAssessment:
    risk_assessment_id: str
    code_proposal_id: str
    risk_level: str
    rationale: str
    blocked: bool
    payload_json: str | None
    created_at: str
