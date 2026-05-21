from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReactionSpecCandidate:
    candidate_id: str
    activation_request_id: str
    name: str
    status: str
    payload_json: str | None
    created_at: str
