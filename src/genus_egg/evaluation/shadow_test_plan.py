from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShadowTestPlan:
    shadow_plan_id: str
    code_proposal_id: str
    plan_type: str
    status: str
    planned_checks_json: str
    activation: str
    payload_json: str | None
    created_at: str
