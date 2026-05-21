from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RollbackPlan:
    rollback_plan_id: str
    code_proposal_id: str
    status: str
    steps_json: str
    payload_json: str | None
    created_at: str
