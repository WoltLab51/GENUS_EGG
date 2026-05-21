from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PatchApproval:
    approval_id: str
    code_proposal_id: str
    approved_by: str
    approval_scope: str
    status: str
    payload_json: str | None
    created_at: str
