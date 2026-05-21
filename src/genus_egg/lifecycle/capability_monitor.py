from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityMonitor:
    monitor_id: str
    code_proposal_id: str
    reaction_outcome_count: int
    error_count: int
    boundary_violation_count: int
    utility_score: int
    status: str
    payload_json: str | None
    created_at: str
