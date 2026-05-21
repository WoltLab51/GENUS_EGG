from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceChain:
    evidence_chain_id: str
    code_proposal_id: str
    evidence_ids_json: str
    status: str
    payload_json: str | None
    created_at: str
