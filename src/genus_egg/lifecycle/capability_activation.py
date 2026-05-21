from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityActivation:
    capability_activation_id: str
    activation_request_id: str
    code_proposal_id: str
    rollback_plan_id: str
    status: str
    activation: str
    payload_json: str | None
    created_at: str
