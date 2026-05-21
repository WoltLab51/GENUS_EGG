from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityProposal:
    proposal_id: str
    need_id: str
    proposal_type: str
    description: str
    status: str
    payload_json: str | None
    created_at: str
