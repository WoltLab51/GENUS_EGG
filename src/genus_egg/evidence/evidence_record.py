from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source_kind: str
    source_id: str
    code_proposal_id: str
    evidence_type: str
    summary: str
    payload_json: str | None
    created_at: str
