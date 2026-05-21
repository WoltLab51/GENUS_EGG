from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ObservationRecord:
    observation_id: str
    chain_id: str
    observation_type: str
    payload_json: str
    created_at: str
