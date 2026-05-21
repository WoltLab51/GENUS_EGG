from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SandboxPatch:
    patch_id: str
    code_proposal_id: str
    approval_id: str
    risk_assessment_id: str
    status: str
    activation: str
    payload_json: str | None
    created_at: str
