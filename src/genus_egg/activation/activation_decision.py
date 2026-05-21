from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActivationDecision:
    activation_decision_id: str
    activation_request_id: str
    decision: str
    status: str
    activation: str
    rationale: str
    payload_json: str | None
    created_at: str
