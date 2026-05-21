from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityNeed:
    need_id: str
    source_observation_id: str | None
    need_type: str
    description: str
    status: str
    payload_json: str | None
    created_at: str
