from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActivationRequest:
    activation_request_id: str
    code_proposal_id: str
    status: str
    reason_code: str
    activation: str
    payload_json: str | None
    created_at: str
