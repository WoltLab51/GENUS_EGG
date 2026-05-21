from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CodeChangeProposal:
    code_proposal_id: str
    proposal_id: str
    title: str
    rationale: str
    allowed_paths_json: str
    forbidden_paths_json: str
    status: str
    payload_json: str | None
    created_at: str
